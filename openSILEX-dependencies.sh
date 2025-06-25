#!/bin/bash

# OpenSILEX Docker Compose Requirements Installer for Debian 12
# This script installs all prerequisites for OpenSILEX Docker Compose deployment
# Including VS Code Dev Containers support

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root. Please run as a regular user with sudo privileges."
        exit 1
    fi
}

# Function to check if user has sudo privileges
check_sudo() {
    if ! sudo -n true 2>/dev/null; then
        print_error "This script requires sudo privileges. Please ensure your user can use sudo."
        exit 1
    fi
}

# Function to update system packages
update_system() {
    print_status "Updating system packages..."
    sudo apt update && sudo apt upgrade -y
    print_success "System packages updated"
}

# Function to install git
install_git() {
    if command -v git &> /dev/null; then
        print_success "Git is already installed ($(git --version))"
    else
        print_status "Installing Git..."
        sudo apt install -y git
        print_success "Git installed successfully"
    fi
}

# Function to install Docker
install_docker() {
    if command -v docker &> /dev/null; then
        print_success "Docker is already installed ($(docker --version))"
    else
        print_status "Installing Docker..."
        
        # Install prerequisites
        sudo apt install -y ca-certificates curl gnupg lsb-release
        
        # Add Docker's official GPG key
        sudo mkdir -p /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        
        # Add Docker repository
        echo \
          "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
          $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # Update package index
        sudo apt update
        
        # Install Docker Engine, containerd, and Docker Compose
        sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        
        print_success "Docker installed successfully"
    fi
}

# Function to configure Docker for current user
configure_docker_user() {
    print_status "Configuring Docker for user $(whoami)..."
    
    # Add user to docker group
    sudo usermod -aG docker $(whoami)
    
    # Start and enable Docker service
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # Fix Docker socket permissions (for immediate access)
    sudo chmod 666 /var/run/docker.sock
    
    print_success "Docker configured for user $(whoami)"
    print_warning "You need to log out and log back in (or restart) for Docker group changes to take effect"
}

# Function to install VS Code (optional - not needed for remote development)
install_vscode() {
    print_status "VS Code Installation Check:"
    print_status "If you're using VS Code with Remote-SSH, you don't need VS Code installed on this host."
    print_status "The Remote-SSH extension handles everything from your local VS Code."
    
    if command -v code &> /dev/null; then
        print_success "VS Code is already installed locally on this host"
        return 0
    fi
    
    read -p "Do you want to install VS Code locally on this host? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Installing VS Code locally..."
        
        # Download and install VS Code
        wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
        sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
        sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
        
        sudo apt update
        sudo apt install -y code
        
        print_success "VS Code installed successfully"
        return 0
    else
        print_success "Skipping VS Code installation (recommended for remote development)"
        return 1
    fi
}

# Function to configure workspace for remote VS Code development
configure_vscode_containers() {
    print_status "Configuring host for VS Code Remote Development with Containers..."
    
    # Install jq for JSON manipulation if not present
    if ! command -v jq &> /dev/null; then
        print_status "Installing jq for JSON configuration..."
        sudo apt install -y jq
    fi
    
    # Note for remote development
    print_status "Host is configured for VS Code Remote-SSH with Dev Containers extension"
    print_status "Make sure your local VS Code has the following extensions:"
    print_status "  - Remote - SSH"
    print_status "  - Dev Containers"
    
    print_success "Host container development configuration completed"
}

# Function to create VS Code workspace for OpenSILEX
create_vscode_workspace() {
    if [ ! -d "$HOME/opensilex-docker-compose" ]; then
        print_warning "OpenSILEX repository not found. Skipping workspace creation."
        return 0
    fi
    
    print_status "Creating VS Code workspace for OpenSILEX..."
    
    # Create .vscode directory in the project
    mkdir -p "$HOME/opensilex-docker-compose/.vscode"
    
    # Create launch configuration for debugging
    cat > "$HOME/opensilex-docker-compose/.vscode/launch.json" << 'EOF'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Attach to OpenSILEX Container",
            "type": "java",
            "request": "attach",
            "hostName": "localhost",
            "port": 5005
        }
    ]
}
EOF
    
    # Create settings for the workspace
    cat > "$HOME/opensilex-docker-compose/.vscode/settings.json" << 'EOF'
{
    "java.debug.settings.enableHotCodeReplace": true,
    "java.debug.settings.enableRunDebugCodeLens": true,
    "files.exclude": {
        "**/target": true,
        "**/node_modules": true,
        "**/.git": true
    }
}
EOF

    # Create devcontainer configuration
    mkdir -p "$HOME/opensilex-docker-compose/.devcontainer"
    cat > "$HOME/opensilex-docker-compose/.devcontainer/devcontainer.json" << 'EOF'
{
    "name": "OpenSILEX Development",
    "dockerComposeFile": "../docker-compose.yml",
    "service": "opensilexapp",
    "workspaceFolder": "/home/opensilex/opensilex-dev",
    "shutdownAction": "none",
    "customizations": {
        "vscode": {
            "extensions": [
                "vscjava.vscode-java-pack",
                "ms-python.python",
                "ms-vscode.vscode-json"
            ]
        }
    },
    "forwardPorts": [28081, 27017, 5005],
    "postCreateCommand": "echo 'OpenSILEX development container ready!'"
}
EOF
    
    print_success "VS Code workspace created for OpenSILEX"
    print_status "Workspace location: $HOME/opensilex-docker-compose/.vscode"
}

# Function to fix common VS Code container permission issues
fix_vscode_permissions() {
    print_status "Fixing VS Code container permissions..."
    
    # Ensure user is in docker group (already done in configure_docker_user)
    
    # Fix Docker socket permissions for immediate access
    if [ -S /var/run/docker.sock ]; then
        sudo chmod 666 /var/run/docker.sock
        print_success "Docker socket permissions fixed"
    fi
    
    # Create Docker config directory with proper permissions
    mkdir -p ~/.docker
    sudo chown -R $(whoami):$(whoami) ~/.docker
    
    # Ensure VS Code can access Docker
    if [ -f ~/.config/Code/User/settings.json ]; then
        print_success "VS Code container permissions configured"
    fi
    
    print_warning "Note: You may need to restart VS Code after logging out/in for all changes to take effect"
}

# Function to verify installations
verify_installations() {
    print_status "Verifying installations..."
    
    echo "Checking Git:"
    if git --version; then
        print_success "Git verification passed"
    else
        print_error "Git verification failed"
        return 1
    fi
    
    echo "Checking Docker:"
    if docker --version; then
        print_success "Docker verification passed"
    else
        print_error "Docker verification failed"
        return 1
    fi
    
    echo "Checking Docker Compose:"
    if docker compose version; then
        print_success "Docker Compose verification passed"
    else
        print_error "Docker Compose verification failed"
        return 1
    fi
    
    echo "Checking Docker permissions:"
    if groups | grep -q docker; then
        print_success "User is in docker group"
    else
        print_warning "User not in docker group for this session"
    fi
    
    if [ -S /var/run/docker.sock ]; then
        print_success "Docker socket found"
        if [ -r /var/run/docker.sock ] && [ -w /var/run/docker.sock ]; then
            print_success "Docker socket permissions OK"
        else
            print_warning "Docker socket permission issues detected"
        fi
    fi
    
    # Optional VS Code check
    if command -v code &> /dev/null; then
        echo "Checking local VS Code installation:"
        if code --version; then
            print_success "Local VS Code installation verified"
        fi
    else
        print_status "No local VS Code installation (normal for remote development)"
    fi
    
    print_success "Host verification completed!"
}

# Function to test Docker (if user is in docker group)
test_docker() {
    print_status "Testing Docker installation..."
    
    # Test Docker access
    if docker run --rm hello-world > /dev/null 2>&1; then
        print_success "Docker test successful!"
    else
        print_warning "Docker test failed. You may need to log out and log back in for group changes to take effect."
        print_status "Try running: docker run --rm hello-world"
    fi
}

# Function to clone OpenSILEX repository (optional)
clone_opensilex() {
    read -p "Do you want to clone the OpenSILEX Docker Compose repository? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Cloning OpenSILEX Docker Compose repository..."
        
        # Clone the repository (version 1.4.7 as specified in README)
        if [ ! -d "$HOME/opensilex-docker-compose" ]; then
            cd "$HOME"
            git clone --branch 1.4.7 https://forgemia.inra.fr/OpenSILEX/opensilex-docker-compose
            cd opensilex-docker-compose
        else
            print_warning "Repository already exists at $HOME/opensilex-docker-compose"
            cd "$HOME/opensilex-docker-compose"
        fi
        
        print_success "OpenSILEX repository available at: $(pwd)"
        return 0
    fi
    return 1
}

# Function to display post-installation instructions
display_instructions() {
    print_success "Installation completed successfully!"
    echo
    print_status "Post-installation steps:"
    echo "1. IMPORTANT: Log out and log back in (or restart your system) to apply Docker group changes"
    echo "2. Test Docker permissions with: docker run --rm hello-world"
    echo
    print_status "For VS Code Remote Development:"
    echo "3. From your local VS Code, ensure these extensions are installed:"
    echo "   - Remote - SSH"
    echo "   - Dev Containers"
    echo "4. Connect to this host via Remote-SSH"
    echo "5. Open the OpenSILEX project folder"
    echo "6. Use Ctrl+Shift+P -> 'Dev Containers: Reopen in Container'"
    
    if [ -d "$HOME/opensilex-docker-compose" ]; then
        echo
        print_status "OpenSILEX Project Setup:"
        echo "7. Navigate to: cd ~/opensilex-docker-compose"
        echo "8. Build and start OpenSILEX:"
        echo "   docker compose --env-file opensilex.env build --build-arg UID=\$(id -u) --build-arg GID=\$(id -g)"
        echo "   docker compose --env-file opensilex.env up start_opensilex_stack -d"
    else
        echo
        print_status "To get started with OpenSILEX:"
        echo "7. Clone repository: git clone --branch 1.4.7 https://forgemia.inra.fr/OpenSILEX/opensilex-docker-compose"
        echo "8. Follow build instructions above"
    fi
    
    echo
    print_status "Access URLs:"
    echo "- OpenSILEX: http://localhost:28081/sandbox/app"
    echo "- API Docs: http://localhost:28081/sandbox/api-docs"
    
    echo
    print_status "Container Permission Fixes Applied:"
    echo "✓ User added to docker group"
    echo "✓ Docker socket permissions configured"
    echo "✓ Development workspace configured"
    echo "✓ Ready for VS Code Remote + Dev Containers"
}

# Main execution
main() {
    echo "==============================================="
    echo "OpenSILEX Docker Compose Installer for Debian 12"
    echo "with VS Code Dev Containers Support"
    echo "==============================================="
    echo
    
    # Pre-flight checks
    check_root
    check_sudo
    
    # Install core components
    update_system
    install_git
    install_docker
    configure_docker_user
    
    # Install and configure VS Code (optional)
    if install_vscode; then
        configure_vscode_containers
        fix_vscode_permissions
    fi
    
    # Clone repository and setup workspace
    if clone_opensilex; then
        if command -v code &> /dev/null; then
            create_vscode_workspace
        fi
    fi
    
    # Verify installations
    verify_installations
    
    # Test Docker (may not work in current session)
    test_docker
    
    # Display final instructions
    display_instructions
}

# Execute main function
main "$@"