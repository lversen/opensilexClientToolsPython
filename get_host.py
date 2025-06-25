#!/usr/bin/env python3
"""
SSH Config Parser - Extract host information from SSH config file
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional


class SSHConfigParser:
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize SSH Config Parser
        
        Args:
            config_path: Path to SSH config file. If None, uses default location.
        """
        if config_path is None:
            # Default SSH config locations
            home = Path.home()
            if os.name == 'nt':  # Windows
                self.config_path = home / '.ssh' / 'config'
            else:  # Unix/Linux/macOS
                self.config_path = home / '.ssh' / 'config'
        else:
            self.config_path = Path(config_path)
        
        self.hosts = {}
        self._parse_config()
    
    def _parse_config(self):
        """Parse the SSH config file and extract host information"""
        if not self.config_path.exists():
            print(f"SSH config file not found: {self.config_path}")
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading SSH config file: {e}")
            return
        
        current_host = None
        current_config = {}
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Split line into key and value
            parts = line.split(None, 1)
            if len(parts) < 2:
                continue
            
            key = parts[0].lower()
            value = parts[1]
            
            if key == 'host':
                # Save previous host if exists
                if current_host:
                    self.hosts[current_host] = current_config
                
                # Start new host
                current_host = value
                current_config = {'line_number': line_num}
            
            elif current_host:
                # Add configuration to current host
                current_config[key] = value
        
        # Don't forget the last host
        if current_host:
            self.hosts[current_host] = current_config
    
    def get_host(self, hostname: str) -> Optional[Dict]:
        """
        Get configuration for a specific host
        
        Args:
            hostname: The host name to look up
            
        Returns:
            Dictionary with host configuration or None if not found
        """
        return self.hosts.get(hostname)
    
    def list_hosts(self) -> List[str]:
        """
        Get list of all configured hosts
        
        Returns:
            List of host names
        """
        return list(self.hosts.keys())
    
    def get_all_hosts(self) -> Dict:
        """
        Get all hosts and their configurations
        
        Returns:
            Dictionary with all host configurations
        """
        return self.hosts.copy()
    
    def search_hosts(self, pattern: str) -> Dict:
        """
        Search for hosts matching a pattern
        
        Args:
            pattern: String pattern to search for in host names
            
        Returns:
            Dictionary with matching hosts and their configurations
        """
        matching_hosts = {}
        pattern_lower = pattern.lower()
        
        for host, config in self.hosts.items():
            if pattern_lower in host.lower():
                matching_hosts[host] = config
        
        return matching_hosts
    
    def find_host_by_ip(self, ip_address: str) -> Optional[str]:
        """
        Find host by IP address (searches both Host and HostName fields)
        
        Args:
            ip_address: IP address to search for
            
        Returns:
            Host name if found, None otherwise
        """
        for host, config in self.hosts.items():
            # Check if the Host itself is the IP
            if host == ip_address:
                return host
            # Check if HostName matches the IP
            if config.get('hostname') == ip_address:
                return host
        
        return None
    
    def print_host_info(self, hostname: str):
        """Print formatted information for a specific host"""
        host_config = self.get_host(hostname)
        
        if not host_config:
            print(f"Host '{hostname}' not found in SSH config")
            return
        
        print(f"\nHost: {hostname}")
        print("-" * (len(hostname) + 6))
        
        for key, value in host_config.items():
            if key != 'line_number':
                print(f"{key.capitalize()}: {value}")
    
    def print_all_hosts(self):
        """Print information for all configured hosts"""
        if not self.hosts:
            print("No hosts found in SSH config")
            return
        
        print(f"\nFound {len(self.hosts)} host(s) in {self.config_path}:")
        print("=" * 50)
        
        for hostname in sorted(self.hosts.keys()):
            self.print_host_info(hostname)
            print()


def main():
    """Main function to demonstrate usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Parse SSH config and extract host information')
    parser.add_argument('--config', '-c', help='Path to SSH config file')
    parser.add_argument('--host', '-H', help='Get information for specific host')
    parser.add_argument('--list', '-l', action='store_true', help='List all hosts')
    parser.add_argument('--search', '-s', help='Search for hosts matching pattern')
    parser.add_argument('--all', '-a', action='store_true', help='Show all host information')
    parser.add_argument('--ip', '-i', help='Find host by IP address')
    
    args = parser.parse_args()
    
    # Initialize parser
    ssh_parser = SSHConfigParser(args.config)
    
    if args.host:
        ssh_parser.print_host_info(args.host)
    elif args.ip:
        host = ssh_parser.find_host_by_ip(args.ip)
        if host:
            ssh_parser.print_host_info(host)
        else:
            print(f"No host found with IP address: {args.ip}")
    elif args.list:
        hosts = ssh_parser.list_hosts()
        if hosts:
            print("Configured hosts:")
            for host in sorted(hosts):
                print(f"  {host}")
        else:
            print("No hosts found in SSH config")
    elif args.search:
        matching_hosts = ssh_parser.search_hosts(args.search)
        if matching_hosts:
            print(f"Hosts matching '{args.search}':")
            for host in sorted(matching_hosts.keys()):
                ssh_parser.print_host_info(host)
        else:
            print(f"No hosts found matching '{args.search}'")
    elif args.all:
        ssh_parser.print_all_hosts()
    else:
        # Default: show usage and list hosts
        print("SSH Config Parser")
        print(f"Config file: {ssh_parser.config_path}")
        
        hosts = ssh_parser.list_hosts()
        if hosts:
            print(f"\nFound {len(hosts)} configured host(s):")
            for host in sorted(hosts):
                print(f"  {host}")
            print("\nUse --help for more options")
        else:
            print("No hosts found in SSH config")


if __name__ == "__main__":
    main()