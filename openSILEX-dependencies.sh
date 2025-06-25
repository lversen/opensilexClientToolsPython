#!/bin/bash

# OpenSILEX Docker Compose Requirements Installer for Debian 12
# This script installs all prerequisites for OpenSILEX Docker Compose deployment

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
    
    print_success "Docker configured for user $(whoami)"
    print_warning "You need to log out and log back in (or restart) for Docker group changes to take effect"
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
    
    print_success "All verifications passed!"
}

# Function to test Docker (if user is in docker group)
test_docker() {
    print_status "Testing Docker installation..."
    
    # Check if current session has docker group access
    if groups | grep -q docker; then
        if docker run --rm hello-world > /dev/null 2>&1; then
            print_success "Docker test successful!"
        else
            print_warning "Docker test failed. You may need to log out and log back in for group changes to take effect."
        fi
    else
        print_warning "User is not yet in docker group for this session. Please log out and log back in, then run: docker run --rm hello-world"
    fi
}

# Function to clone OpenSILEX repository (optional)
clone_opensilex() {
    read -p "Do you want to clone the OpenSILEX Docker Compose repository? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Cloning OpenSILEX Docker Compose repository..."
        
        # Clone the repository (version 1.4.7 as specified in README)
        git clone --branch 1.4.7 https://forgemia.inra.fr/OpenSILEX/opensilex-docker-compose
        cd opensilex-docker-compose
        
        print_success "OpenSILEX repository cloned successfully"
        print_status "Repository location: $(pwd)"
        print_status "Next steps:"
        echo "  1. cd opensilex-docker-compose"
        echo "  2. Review and modify opensilex.env file if needed"
        echo "  3. Run: docker compose --env-file opensilex.env build --build-arg UID=\$(id -u) --build-arg GID=\$(id -g)"
        echo "  4. Run: docker compose --env-file opensilex.env up start_opensilex_stack -d"
    fi
}

# Function to display post-installation instructions
display_instructions() {
    print_success "Installation completed successfully!"
    echo
    print_status "Post-installation steps:"
    echo "1. Log out and log back in (or restart your system) to apply Docker group changes"
    echo "2. Test Docker with: docker run --rm hello-world"
    echo "3. Clone OpenSILEX repository:"
    echo "   git clone --branch 1.4.7 https://forgemia.inra.fr/OpenSILEX/opensilex-docker-compose"
    echo "4. Navigate to the project: cd opensilex-docker-compose"
    echo "5. Build and start OpenSILEX:"
    echo "   docker compose --env-file opensilex.env build --build-arg UID=\$(id -u) --build-arg GID=\$(id -g)"
    echo "   docker compose --env-file opensilex.env up start_opensilex_stack -d"
    echo
    print_status "OpenSILEX will be available at: http://localhost:28081/sandbox/app"
    print_status "API documentation at: http://localhost:28081/sandbox/api-docs"
}

# Main execution
main() {
    echo "==============================================="
    echo "OpenSILEX Docker Compose Installer for Debian 12"
    echo "==============================================="
    echo
    
    # Pre-flight checks
    check_root
    check_sudo
    
    # Install components
    update_system
    install_git
    install_docker
    configure_docker_user
    
    # Verify installations
    verify_installations
    
    # Test Docker (may not work in current session)
    test_docker
    
    # Optional repository cloning
    clone_opensilex
    
    # Display final instructions
    display_instructions
}

# Execute main function
main "$@"