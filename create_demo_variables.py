#!/usr/bin/env python3
"""
OpenSilex Smart Demo Variables Creator - SSH Config Only

This script creates demo ontology concepts (entities, characteristics, methods, units)
and variables in your OpenSilex system. It exclusively uses SSH config for host management
via get_host.py.

Fixed Issue: The original script was passing JSON objects to VariableCreationDTO.entity
instead of URI strings, causing "Cannot deserialize value of type java.net.URI" errors.

Usage:
    python create_demo_variables.py
    
The script will:
1. List available SSH config hosts
2. Prompt you to select one
3. Connect and create demo variables
    
SSH Config Example:
    Host my-opensilex-dev
        HostName 192.168.1.100
        Port 28081
        
    Host my-opensilex-prod
        HostName opensilex.company.com
        Port 8080
"""

import opensilexClientToolsPython
from opensilexClientToolsPython.models.variable_creation_dto import VariableCreationDTO
from opensilexClientToolsPython.models.entity_creation_dto import EntityCreationDTO
from opensilexClientToolsPython.models.characteristic_creation_dto import CharacteristicCreationDTO
from opensilexClientToolsPython.models.method_creation_dto import MethodCreationDTO
from opensilexClientToolsPython.models.unit_creation_dto import UnitCreationDTO
import sys
from get_host import SSHConfigParser

def get_ssh_config_hosts():
    """Get all available hosts from SSH config"""
    try:
        ssh_parser = SSHConfigParser()
        return ssh_parser.get_all_hosts(), ssh_parser
    except Exception as e:
        print(f"⚠️ Error reading SSH config: {e}")
        return {}, None

def select_host_from_ssh_config():
    """Interactive host selection from SSH config"""
    hosts, ssh_parser = get_ssh_config_hosts()
    
    if not hosts:
        print("❌ No hosts found in SSH config")
        print("Please configure your OpenSilex hosts in ~/.ssh/config")
        print("\nExample SSH config entry:")
        print("Host my-opensilex")
        print("    HostName 192.168.1.100")
        print("    Port 28081")
        sys.exit(1)
    
    print("📋 Available OpenSilex hosts from SSH config:")
    print("=" * 50)
    
    host_list = list(hosts.keys())
    for i, host_name in enumerate(host_list, 1):
        host_config = hosts[host_name]
        hostname = host_config.get('hostname', host_name)
        port = host_config.get('port', '28081')
        print(f"{i}. {host_name}")
        print(f"   Hostname: {hostname}")
        print(f"   Port: {port}")
        print()
    
    while True:
        try:
            choice = input(f"Select host (1-{len(host_list)}) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                print("Exiting...")
                sys.exit(0)
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(host_list):
                selected_host = host_list[choice_num - 1]
                return selected_host, hosts[selected_host]
            else:
                print(f"Please enter a number between 1 and {len(host_list)}")
                
        except ValueError:
            print("Please enter a valid number or 'q' to quit")
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)

def construct_opensilex_url(host_name, host_config):
    """Construct OpenSilex API URL from SSH config"""
    hostname = host_config.get('hostname', host_name)
    port = host_config.get('port', '28081')
    
    # Construct the OpenSilex API URL
    api_url = f"http://{hostname}:{port}/sandbox/rest"
    
    print(f"🔗 Constructed API URL: {api_url}")
    return api_url

def get_credentials():
    """Get OpenSilex credentials from user"""
    print("\n🔐 OpenSilex Authentication:")
    print("-" * 30)
    
    identifier = input("Enter identifier (default: admin@opensilex.org): ").strip()
    if not identifier:
        identifier = "admin@opensilex.org"
    
    password = input("Enter password (default: admin): ").strip()
    if not password:
        password = "admin"
    
    return identifier, password

def connect_to_opensilex(host, identifier, password):
    """Connect to OpenSilex instance and return authenticated client"""
    try:
        pythonClient = opensilexClientToolsPython.ApiClient()
        pythonClient.connect_to_opensilex_ws(
            identifier=identifier,
            password=password,
            host=host
        )
        print(f"✓ Successfully connected to OpenSilex at {host}")
        return pythonClient
    except Exception as e:
        print(f"✗ Failed to connect to OpenSilex: {e}")
        return None

def check_if_concepts_exist(variables_api):
    """Quick check to see if any real concepts exist in the system"""
    try:
        # Try to get entities and check if we have real data
        entities_response = variables_api.search_entities(page_size=10)
        if entities_response:
            # Convert to list and check first item
            entities_list = list(entities_response) if hasattr(entities_response, '__iter__') else []
            if entities_list and len(entities_list) > 0:
                first_item = entities_list[0]
                # Check if this looks like real data (has a URI that starts with http)
                if hasattr(first_item, 'uri') and first_item.uri and first_item.uri.startswith('http'):
                    return True
                # Check if it has a name that's not 'metadata' or 'result'
                if hasattr(first_item, 'name') and first_item.name and first_item.name not in ['metadata', 'result']:
                    return True
        return False
    except Exception as e:
        print(f"Warning: Could not check existing concepts: {e}")
        return False

def extract_uri_from_response(response):
    """Extract URI string from API response (handles various response formats)"""
    
    # Handle dictionary response with 'result' key (the format your API is returning)
    if isinstance(response, dict):
        if 'result' in response and isinstance(response['result'], list):
            if len(response['result']) > 0:
                return response['result'][0]  # Return the first URI in the result list
        elif 'uri' in response:
            return response['uri']
    
    # Handle string response
    elif isinstance(response, str):
        return response
    
    # Handle object with uri attribute
    elif hasattr(response, 'uri'):
        return response.uri
    
    # Handle object with __dict__
    elif hasattr(response, '__dict__'):
        response_dict = response.__dict__
        if 'uri' in response_dict:
            return response_dict['uri']
        # Sometimes the response might have other patterns
        for key, value in response_dict.items():
            if 'uri' in key.lower() and isinstance(value, str):
                return value
    
    # If we still haven't found it, convert to string and see if it looks like a URI
    response_str = str(response)
    if response_str.startswith('http') or response_str.startswith('opensilex'):
        return response_str
    else:
        print(f"Warning: Could not extract URI from response: {response} (type: {type(response)})")
        return None

def list_existing_concepts(variables_api):
    """List existing concepts in the system"""
    print("\n🔍 Existing concepts in the system:")
    
    try:
        # List entities
        entities_response = variables_api.search_entities(page_size=50)
        if entities_response:
            entities_list = list(entities_response) if hasattr(entities_response, '__iter__') else []
            if entities_list:
                print(f"\n📦 Entities ({len(entities_list)}):")
                for entity in entities_list[:10]:  # Show first 10
                    name = entity.name if hasattr(entity, 'name') else 'Unknown'
                    uri = entity.uri if hasattr(entity, 'uri') else 'No URI'
                    print(f"  - {name} ({uri})")
                if len(entities_list) > 10:
                    print(f"  ... and {len(entities_list) - 10} more")
    except Exception as e:
        print(f"  Could not list entities: {e}")
    
    try:
        # List characteristics
        chars_response = variables_api.search_characteristics(page_size=50)
        if chars_response:
            chars_list = list(chars_response) if hasattr(chars_response, '__iter__') else []
            if chars_list:
                print(f"\n🔬 Characteristics ({len(chars_list)}):")
                for char in chars_list[:10]:  # Show first 10
                    name = char.name if hasattr(char, 'name') else 'Unknown'
                    uri = char.uri if hasattr(char, 'uri') else 'No URI'
                    print(f"  - {name} ({uri})")
                if len(chars_list) > 10:
                    print(f"  ... and {len(chars_list) - 10} more")
    except Exception as e:
        print(f"  Could not list characteristics: {e}")
    
    try:
        # List methods
        methods_response = variables_api.search_methods(page_size=50)
        if methods_response:
            methods_list = list(methods_response) if hasattr(methods_response, '__iter__') else []
            if methods_list:
                print(f"\n⚙️ Methods ({len(methods_list)}):")
                for method in methods_list[:10]:  # Show first 10
                    name = method.name if hasattr(method, 'name') else 'Unknown'
                    uri = method.uri if hasattr(method, 'uri') else 'No URI'
                    print(f"  - {name} ({uri})")
                if len(methods_list) > 10:
                    print(f"  ... and {len(methods_list) - 10} more")
    except Exception as e:
        print(f"  Could not list methods: {e}")
    
    try:
        # List units
        units_response = variables_api.search_units(page_size=50)
        if units_response:
            units_list = list(units_response) if hasattr(units_response, '__iter__') else []
            if units_list:
                print(f"\n📏 Units ({len(units_list)}):")
                for unit in units_list[:10]:  # Show first 10
                    name = unit.name if hasattr(unit, 'name') else 'Unknown'
                    uri = unit.uri if hasattr(unit, 'uri') else 'No URI'
                    print(f"  - {name} ({uri})")
                if len(units_list) > 10:
                    print(f"  ... and {len(units_list) - 10} more")
    except Exception as e:
        print(f"  Could not list units: {e}")

def create_basic_concepts(variables_api):
    """Create basic demo concepts and return their URIs"""
    print(f"\n🛠️ Creating basic demo concepts...")
    print("-" * 60)
    
    created_concepts = {
        'entities': [],
        'characteristics': [],
        'methods': [],
        'units': []
    }
    
    # Basic entities to create
    basic_entities = [
        {
            'name': 'Plant',
            'description': 'Living plant organism',
            'exact_match': []
        },
        {
            'name': 'Leaf',
            'description': 'Plant leaf structure',
            'exact_match': []
        },
        {
            'name': 'Stem',
            'description': 'Plant stem structure',
            'exact_match': []
        }
    ]
    
    # Basic characteristics to create
    basic_characteristics = [
        {
            'name': 'Height',
            'description': 'Vertical measurement from base to top',
            'exact_match': []
        },
        {
            'name': 'Width',
            'description': 'Horizontal measurement',
            'exact_match': []
        },
        {
            'name': 'Temperature',
            'description': 'Thermal measurement',
            'exact_match': []
        }
    ]
    
    # Basic methods to create
    basic_methods = [
        {
            'name': 'Manual Measurement',
            'description': 'Measurement taken manually with tools',
            'exact_match': []
        },
        {
            'name': 'Sensor Reading',
            'description': 'Automated measurement via sensors',
            'exact_match': []
        }
    ]
    
    # Basic units to create
    basic_units = [
        {
            'name': 'Centimeter',
            'description': 'Unit of length measurement',
            'exact_match': [],
            'symbol': 'cm'
        },
        {
            'name': 'Celsius',
            'description': 'Unit of temperature measurement',
            'exact_match': [],
            'symbol': '°C'
        }
    ]
    
    # Create entities
    print("\n📦 Creating entities...")
    for entity_data in basic_entities:
        try:
            entity = EntityCreationDTO(**entity_data)
            result = variables_api.create_entity(body=entity)
            uri = extract_uri_from_response(result)
            if uri:
                created_concepts['entities'].append({'name': entity_data['name'], 'uri': uri})
                print(f"  ✓ Created entity: {entity_data['name']} -> {uri}")
            else:
                print(f"  ✗ Failed to extract URI for entity {entity_data['name']}")
        except Exception as e:
            print(f"  ✗ Failed to create entity {entity_data['name']}: {e}")
    
    # Create characteristics
    print("\n🔬 Creating characteristics...")
    for char_data in basic_characteristics:
        try:
            characteristic = CharacteristicCreationDTO(**char_data)
            result = variables_api.create_characteristic(body=characteristic)
            uri = extract_uri_from_response(result)
            if uri:
                created_concepts['characteristics'].append({'name': char_data['name'], 'uri': uri})
                print(f"  ✓ Created characteristic: {char_data['name']} -> {uri}")
            else:
                print(f"  ✗ Failed to extract URI for characteristic {char_data['name']}")
        except Exception as e:
            print(f"  ✗ Failed to create characteristic {char_data['name']}: {e}")
    
    # Create methods
    print("\n⚙️ Creating methods...")
    for method_data in basic_methods:
        try:
            method = MethodCreationDTO(**method_data)
            result = variables_api.create_method(body=method)
            uri = extract_uri_from_response(result)
            if uri:
                created_concepts['methods'].append({'name': method_data['name'], 'uri': uri})
                print(f"  ✓ Created method: {method_data['name']} -> {uri}")
            else:
                print(f"  ✗ Failed to extract URI for method {method_data['name']}")
        except Exception as e:
            print(f"  ✗ Failed to create method {method_data['name']}: {e}")
    
    # Create units
    print("\n📏 Creating units...")
    for unit_data in basic_units:
        try:
            unit = UnitCreationDTO(**unit_data)
            result = variables_api.create_unit(body=unit)
            uri = extract_uri_from_response(result)
            if uri:
                created_concepts['units'].append({'name': unit_data['name'], 'uri': uri})
                print(f"  ✓ Created unit: {unit_data['name']} -> {uri}")
            else:
                print(f"  ✗ Failed to extract URI for unit {unit_data['name']}")
        except Exception as e:
            print(f"  ✗ Failed to create unit {unit_data['name']}: {e}")
    
    # Debug: Print summary of created concepts
    print(f"\n🔍 Debug - Created concept summary:")
    print(f"   Entities: {len(created_concepts['entities'])}")
    for entity in created_concepts['entities']:
        print(f"     - {entity['name']}: {entity['uri']}")
    print(f"   Characteristics: {len(created_concepts['characteristics'])}")
    for char in created_concepts['characteristics']:
        print(f"     - {char['name']}: {char['uri']}")
    print(f"   Methods: {len(created_concepts['methods'])}")
    for method in created_concepts['methods']:
        print(f"     - {method['name']}: {method['uri']}")
    print(f"   Units: {len(created_concepts['units'])}")
    for unit in created_concepts['units']:
        print(f"     - {unit['name']}: {unit['uri']}")
    
    return created_concepts

def create_demo_variables(variables_api, created_concepts):
    """Create demo variables using the created concepts"""
    print(f"\n🛠️ Creating demo variables using created concepts...")
    print("-" * 60)
    
    created_variables = []
    failed_variables = []
    
    # Helper function to find concept URI by name
    def find_concept_uri(concepts_list, name_contains):
        for concept in concepts_list:
            if name_contains.lower() in concept['name'].lower():
                return concept['uri']
        return None
    
    # Validate that we have enough concepts to create variables
    if not created_concepts['entities'] or not created_concepts['characteristics'] or not created_concepts['methods'] or not created_concepts['units']:
        print("⚠️ Not enough concepts were created successfully. Cannot create variables.")
        return [], []
    
    # Define demo variables using created concepts
    demo_variables = []
    
    # Try to create Plant Height variable
    plant_uri = find_concept_uri(created_concepts['entities'], 'plant')
    height_uri = find_concept_uri(created_concepts['characteristics'], 'height')
    manual_uri = find_concept_uri(created_concepts['methods'], 'manual')
    cm_uri = find_concept_uri(created_concepts['units'], 'centimeter')
    
    if plant_uri and height_uri and manual_uri and cm_uri:
        demo_variables.append({
            'name': 'Plant Height Manual',
            'description': 'Plant height measured manually',
            'entity': plant_uri,
            'characteristic': height_uri,
            'method': manual_uri,
            'unit': cm_uri,
            'datatype': 'http://www.w3.org/2001/XMLSchema#decimal',
            'exact_match': []
        })
    
    # Try to create Leaf Width variable
    leaf_uri = find_concept_uri(created_concepts['entities'], 'leaf')
    width_uri = find_concept_uri(created_concepts['characteristics'], 'width')
    
    if leaf_uri and width_uri and manual_uri and cm_uri:
        demo_variables.append({
            'name': 'Leaf Width Manual',
            'description': 'Leaf width measured manually',
            'entity': leaf_uri,
            'characteristic': width_uri,
            'method': manual_uri,
            'unit': cm_uri,
            'datatype': 'http://www.w3.org/2001/XMLSchema#decimal',
            'exact_match': []
        })
    
    # Try to create Temperature Sensor variable
    temp_uri = find_concept_uri(created_concepts['characteristics'], 'temperature')
    sensor_uri = find_concept_uri(created_concepts['methods'], 'sensor')
    celsius_uri = find_concept_uri(created_concepts['units'], 'celsius')
    
    if plant_uri and temp_uri and sensor_uri and celsius_uri:
        demo_variables.append({
            'name': 'Plant Temperature Sensor',
            'description': 'Plant temperature measured by sensor',
            'entity': plant_uri,
            'characteristic': temp_uri,
            'method': sensor_uri,
            'unit': celsius_uri,
            'datatype': 'http://www.w3.org/2001/XMLSchema#decimal',
            'exact_match': []
        })
    
    if len(demo_variables) == 0:
        print("⚠️ No variables can be created - insufficient concepts available.")
        return [], []
    
    # Create variables
    for var_data in demo_variables:
        try:
            variable = VariableCreationDTO(**var_data)
            result = variables_api.create_variable(body=variable)
            uri = extract_uri_from_response(result)
            if uri:
                created_variables.append({'name': var_data['name'], 'uri': uri})
                print(f"  ✓ Created variable: {var_data['name']} -> {uri}")
            else:
                created_variables.append({'name': var_data['name'], 'uri': 'URI extraction failed'})
                print(f"  ✓ Created variable: {var_data['name']} (but URI extraction failed)")
        except Exception as e:
            failed_variables.append({'name': var_data['name'], 'error': str(e)})
            print(f"  ✗ Failed to create variable {var_data['name']}: {e}")
    
    return created_variables, failed_variables

def main():
    """Main function to orchestrate the demo setup"""
    print("OpenSilex Smart Demo Variables Creator - SSH Config Only")
    print("=" * 60)
    
    # Select host from SSH config
    host_name, host_config = select_host_from_ssh_config()
    
    # Construct OpenSilex API URL
    api_url = construct_opensilex_url(host_name, host_config)
    
    # Get credentials
    identifier, password = get_credentials()
    
    print(f"\n🚀 Connecting to OpenSilex...")
    print(f"Host: {host_name}")
    print(f"API URL: {api_url}")
    print(f"User: {identifier}")
    
    # Connect to OpenSilex
    client = connect_to_opensilex(api_url, identifier, password)
    if not client:
        sys.exit(1)
    
    # Create API instance
    variables_api = opensilexClientToolsPython.VariablesApi(client)
    
    # Check if concepts already exist
    print("\n🔍 Checking for existing concepts...")
    concepts_exist = check_if_concepts_exist(variables_api)
    
    if concepts_exist:
        # List existing concepts
        list_existing_concepts(variables_api)
        
        print("\n⚠️ Concepts already exist in the system.")
        print("\nOptions:")
        print("1. Use existing concepts to create variables")
        print("2. Create additional basic concepts anyway")
        print("3. Exit without changes")
        
        while True:
            try:
                choice = input("\nChoose an option (1/2/3): ").strip()
                
                if choice == "1":
                    print("Using existing concepts to create variables...")
                    # TODO: Could implement logic to use existing concepts
                    print("⚠️ Feature not yet implemented. Please use option 2 or 3.")
                    sys.exit(0)
                elif choice == "2":
                    print("Creating additional basic concepts...")
                    break
                elif choice == "3":
                    print("Exiting without changes.")
                    sys.exit(0)
                else:
                    print("Please enter 1, 2, or 3")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                sys.exit(0)
    else:
        print("📭 No concepts found in the system")
        
        while True:
            try:
                response = input("\nWould you like to create basic demo concepts and variables? (y/n): ").strip().lower()
                
                if response == 'n':
                    print("Exiting without creating anything.")
                    sys.exit(0)
                elif response == 'y':
                    break
                else:
                    print("Please enter 'y' or 'n'")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                sys.exit(0)
    
    # Create basic concepts
    created_concepts = create_basic_concepts(variables_api)
    
    # Create demo variables
    created_vars, failed_vars = create_demo_variables(variables_api, created_concepts)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Summary:")
    print(f"✓ Successfully created {len(created_vars)} variables")
    
    if created_vars:
        print("\nCreated variables:")
        for var in created_vars:
            print(f"  - {var['name']}")
    
    if failed_vars:
        print(f"\n✗ Failed to create {len(failed_vars)} variables")
        print("\nFailed variables:")
        for var in failed_vars:
            print(f"  - {var['name']}: {var['error']}")
    
    print("\n✨ Demo setup complete!")
    print(f"\nConnected to: {host_name} ({api_url})")
    print("\nYou can now:")
    print("  1. View these variables in the OpenSilex web interface")
    print("  2. Use them to create data entries")
    print("  3. Create additional variables using the web interface or API")

if __name__ == "__main__":
    main()