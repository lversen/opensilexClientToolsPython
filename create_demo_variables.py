#!/usr/bin/env python3
"""
OpenSilex Smart Demo Variables Creator

This script creates demo ontology concepts (entities, characteristics, methods, units)
and variables in your OpenSilex system. It fixes the URI serialization issue by properly
capturing and using the returned URIs from concept creation.

Fixed Issue: The original script was passing JSON objects to VariableCreationDTO.entity
instead of URI strings, causing "Cannot deserialize value of type java.net.URI" errors.

Usage:
    python script.py <host> [--identifier <email>] [--password <password>]
    
Host can be:
    - Just an IP: 48.209.64.78 (will use http://{ip}:28081/sandbox/rest)
    - IP with port: 48.209.64.78:8080 (will use http://{ip}:{port}/sandbox/rest)
    - Hostname: localhost (will use http://localhost:28081/sandbox/rest)
    - Full URL: http://localhost:8080/rest
    
Examples:
    python script.py 48.209.64.78
    python script.py 192.168.1.100:8080
    python script.py localhost
    python script.py http://localhost:8080/rest --identifier user@example.com --password mypass
"""

import opensilexClientToolsPython
from opensilexClientToolsPython.models.variable_creation_dto import VariableCreationDTO
from opensilexClientToolsPython.models.entity_creation_dto import EntityCreationDTO
from opensilexClientToolsPython.models.characteristic_creation_dto import CharacteristicCreationDTO
from opensilexClientToolsPython.models.method_creation_dto import MethodCreationDTO
from opensilexClientToolsPython.models.unit_creation_dto import UnitCreationDTO
import sys
import argparse
import re

def construct_host_url(host_input):
    """
    Construct full host URL from various input formats.
    Accepts:
    - Full URL: http://example.com:8080/rest
    - IP address: 192.168.1.1
    - IP with port: 192.168.1.1:8080
    - Hostname: localhost
    - Hostname with port: localhost:8080
    """
    # Check if it's already a full URL (starts with http:// or https://)
    if host_input.startswith(('http://', 'https://')):
        return host_input
    
    # Check if it's an IP address (basic pattern) or hostname
    # This regex matches IP addresses and hostnames with optional port
    ip_pattern = r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|[a-zA-Z0-9.-]+)(:\d+)?$'
    match = re.match(ip_pattern, host_input)
    
    if match:
        host_part = match.group(1)
        port_part = match.group(2)  # This includes the colon if present
        
        # Default port and path based on the example
        default_port = ':28081'
        default_path = '/sandbox/rest'
        
        # If no port specified, use default
        if not port_part:
            port_part = default_port
        
        # Construct the full URL
        return f"http://{host_part}{port_part}{default_path}"
    
    # If we can't parse it, return as-is and let the connection fail with a clear error
    return host_input

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
            entities_list = list(entities_response)
            if entities_list:
                print(f"\n📊 Entities ({len(entities_list)}):")
                for entity in entities_list[:10]:  # Show first 10
                    if hasattr(entity, 'name') and hasattr(entity, 'uri'):
                        print(f"  - {entity.name} ({entity.uri})")
                if len(entities_list) > 10:
                    print(f"  ... and {len(entities_list) - 10} more")
    except Exception as e:
        print(f"  Could not list entities: {e}")
    
    try:
        # List characteristics
        chars_response = variables_api.search_characteristics(page_size=50)
        if chars_response:
            chars_list = list(chars_response)
            if chars_list:
                print(f"\n🎯 Characteristics ({len(chars_list)}):")
                for char in chars_list[:10]:  # Show first 10
                    if hasattr(char, 'name') and hasattr(char, 'uri'):
                        print(f"  - {char.name} ({char.uri})")
                if len(chars_list) > 10:
                    print(f"  ... and {len(chars_list) - 10} more")
    except Exception as e:
        print(f"  Could not list characteristics: {e}")
    
    try:
        # List methods
        methods_response = variables_api.search_methods(page_size=50)
        if methods_response:
            methods_list = list(methods_response)
            if methods_list:
                print(f"\n🔬 Methods ({len(methods_list)}):")
                for method in methods_list[:10]:  # Show first 10
                    if hasattr(method, 'name') and hasattr(method, 'uri'):
                        print(f"  - {method.name} ({method.uri})")
                if len(methods_list) > 10:
                    print(f"  ... and {len(methods_list) - 10} more")
    except Exception as e:
        print(f"  Could not list methods: {e}")
    
    try:
        # List units
        units_response = variables_api.search_units(page_size=50)
        if units_response:
            units_list = list(units_response)
            if units_list:
                print(f"\n📏 Units ({len(units_list)}):")
                for unit in units_list[:10]:  # Show first 10
                    if hasattr(unit, 'name') and hasattr(unit, 'uri'):
                        print(f"  - {unit.name} ({unit.uri})")
                if len(units_list) > 10:
                    print(f"  ... and {len(units_list) - 10} more")
    except Exception as e:
        print(f"  Could not list units: {e}")

def create_basic_concepts(variables_api):
    """Create basic ontology concepts needed for demo variables"""
    print(f"\n🏗️ Creating basic ontology concepts...")
    print("-" * 60)
    
    created_concepts = {
        'entities': [],
        'characteristics': [],
        'methods': [],
        'units': []
    }
    
    # Define basic entities
    basic_entities = [
        {"name": "Plant", "description": "Whole plant organism"},
        {"name": "Soil", "description": "Soil environment"},
        {"name": "Environment", "description": "Environmental conditions"},
        {"name": "Leaf", "description": "Plant leaf"},
        {"name": "Seed", "description": "Plant seed"}
    ]
    
    # Define basic characteristics
    basic_characteristics = [
        {"name": "Height", "description": "Vertical measurement"},
        {"name": "Weight", "description": "Mass measurement"},
        {"name": "Temperature", "description": "Temperature measurement"},
        {"name": "Moisture", "description": "Water content"},
        {"name": "Color", "description": "Visual color"},
        {"name": "Count", "description": "Number of items"},
        {"name": "Area", "description": "Surface measurement"},
        {"name": "Length", "description": "Linear measurement"}
    ]
    
    # Define basic methods
    basic_methods = [
        {"name": "Manual Measurement", "description": "Measurement by hand"},
        {"name": "Visual Observation", "description": "Visual assessment"},
        {"name": "Sensor Reading", "description": "Automated sensor measurement"},
        {"name": "Laboratory Analysis", "description": "Lab-based measurement"},
        {"name": "Digital Image Analysis", "description": "Computer vision measurement"}
    ]
    
    # Define basic units
    basic_units = [
        {"name": "centimeter", "description": "Unit of length", "symbol": "cm"},
        {"name": "gram", "description": "Unit of mass", "symbol": "g"},
        {"name": "celsius", "description": "Temperature unit", "symbol": "°C"},
        {"name": "percent", "description": "Percentage", "symbol": "%"},
        {"name": "count", "description": "Dimensionless count", "symbol": ""},
        {"name": "meter", "description": "Unit of length", "symbol": "m"},
        {"name": "kilogram", "description": "Unit of mass", "symbol": "kg"},
        {"name": "liter", "description": "Unit of volume", "symbol": "L"}
    ]
    
    # Create entities
    print("\n📊 Creating entities...")
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
    print("\n🎯 Creating characteristics...")
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
    print("\n🔬 Creating methods...")
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
    
    # Create demo variables based on created concepts
    demo_variables = []
    
    # Plant height variable
    plant_uri = find_concept_uri(created_concepts['entities'], 'plant')
    height_uri = find_concept_uri(created_concepts['characteristics'], 'height')
    manual_uri = find_concept_uri(created_concepts['methods'], 'manual')
    cm_uri = find_concept_uri(created_concepts['units'], 'centimeter')
    
    if all([plant_uri, height_uri, manual_uri, cm_uri]):
        demo_variables.append({
            "name": "Plant Height",
            "description": "Height measurement of plant in centimeters",
            "entity": plant_uri,  # This is now a URI string, not an object
            "characteristic": height_uri,
            "method": manual_uri,
            "unit": cm_uri,
            "datatype": "http://www.w3.org/2001/XMLSchema#decimal"
        })
    else:
        print(f"  ⚠️ Skipping Plant Height variable - missing URIs: plant={plant_uri}, height={height_uri}, manual={manual_uri}, cm={cm_uri}")
    
    # Environmental temperature variable
    env_uri = find_concept_uri(created_concepts['entities'], 'environment')
    temp_uri = find_concept_uri(created_concepts['characteristics'], 'temperature')
    sensor_uri = find_concept_uri(created_concepts['methods'], 'sensor')
    celsius_uri = find_concept_uri(created_concepts['units'], 'celsius')
    
    if all([env_uri, temp_uri, sensor_uri, celsius_uri]):
        demo_variables.append({
            "name": "Environmental Temperature",
            "description": "Temperature measurement of environment in celsius",
            "entity": env_uri,
            "characteristic": temp_uri,
            "method": sensor_uri,
            "unit": celsius_uri,
            "datatype": "http://www.w3.org/2001/XMLSchema#decimal"
        })
    else:
        print(f"  ⚠️ Skipping Environmental Temperature variable - missing URIs: env={env_uri}, temp={temp_uri}, sensor={sensor_uri}, celsius={celsius_uri}")
    
    # Seed weight variable
    seed_uri = find_concept_uri(created_concepts['entities'], 'seed')
    weight_uri = find_concept_uri(created_concepts['characteristics'], 'weight')
    lab_uri = find_concept_uri(created_concepts['methods'], 'laboratory')
    gram_uri = find_concept_uri(created_concepts['units'], 'gram')
    
    if all([seed_uri, weight_uri, lab_uri, gram_uri]):
        demo_variables.append({
            "name": "Seed Weight",
            "description": "Weight measurement of individual seeds in grams",
            "entity": seed_uri,
            "characteristic": weight_uri,
            "method": lab_uri,
            "unit": gram_uri,
            "datatype": "http://www.w3.org/2001/XMLSchema#decimal"
        })
    else:
        print(f"  ⚠️ Skipping Seed Weight variable - missing URIs: seed={seed_uri}, weight={weight_uri}, lab={lab_uri}, gram={gram_uri}")
    
    # Leaf count variable
    leaf_uri = find_concept_uri(created_concepts['entities'], 'leaf')
    count_uri = find_concept_uri(created_concepts['characteristics'], 'count')
    visual_uri = find_concept_uri(created_concepts['methods'], 'visual')
    count_unit_uri = find_concept_uri(created_concepts['units'], 'count')
    
    if all([leaf_uri, count_uri, visual_uri, count_unit_uri]):
        demo_variables.append({
            "name": "Leaf Count",
            "description": "Number of leaves per plant",
            "entity": leaf_uri,
            "characteristic": count_uri,
            "method": visual_uri,
            "unit": count_unit_uri,
            "datatype": "http://www.w3.org/2001/XMLSchema#integer"
        })
    else:
        print(f"  ⚠️ Skipping Leaf Count variable - missing URIs: leaf={leaf_uri}, count={count_uri}, visual={visual_uri}, count_unit={count_unit_uri}")
    
    # Soil moisture variable
    soil_uri = find_concept_uri(created_concepts['entities'], 'soil')
    moisture_uri = find_concept_uri(created_concepts['characteristics'], 'moisture')
    percent_uri = find_concept_uri(created_concepts['units'], 'percent')
    
    if all([soil_uri, moisture_uri, sensor_uri, percent_uri]):
        demo_variables.append({
            "name": "Soil Moisture Content",
            "description": "Moisture content of soil as percentage",
            "entity": soil_uri,
            "characteristic": moisture_uri,
            "method": sensor_uri,
            "unit": percent_uri,
            "datatype": "http://www.w3.org/2001/XMLSchema#decimal"
        })
    else:
        print(f"  ⚠️ Skipping Soil Moisture Content variable - missing URIs: soil={soil_uri}, moisture={moisture_uri}, sensor={sensor_uri}, percent={percent_uri}")
    
    print(f"\n📋 Prepared {len(demo_variables)} variables for creation.")
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
    # Set up command line argument parser
    parser = argparse.ArgumentParser(
        description='OpenSilex Smart Demo Variables Creator - Creates demo ontology concepts and variables',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 48.209.64.78                          # Just IP address (uses default port 28081 and path /sandbox/rest)
  %(prog)s 192.168.1.100:8080                    # IP with custom port
  %(prog)s localhost                              # Hostname
  %(prog)s http://localhost:8080/rest            # Full URL
  %(prog)s 48.209.64.78 --identifier user@example.com
  %(prog)s 192.168.1.100 -i admin@example.com -p secretpass
        """
    )
    
    # Add arguments
    parser.add_argument('host', 
                        help='OpenSilex host (IP address, hostname, or full URL)')
    
    parser.add_argument('-i', '--identifier', 
                        default='admin@opensilex.org',
                        help='User identifier/email for authentication (default: admin@opensilex.org)')
    
    parser.add_argument('-p', '--password', 
                        default='admin',
                        help='Password for authentication (default: admin)')
    
    parser.add_argument('--port', 
                        type=int,
                        help='Override default port 28081 (only used when host is IP/hostname without port)')
    
    parser.add_argument('--path', 
                        default='/sandbox/rest',
                        help='Override default path (default: /sandbox/rest)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Construct the full host URL
    HOST = construct_host_url(args.host)
    
    # If user specified custom port or path and didn't provide full URL, reconstruct
    if not args.host.startswith(('http://', 'https://')):
        if args.port or args.path != '/sandbox/rest':
            # Extract the host part without port
            match = re.match(r'^([^:]+)(:\d+)?', args.host)
            if match:
                host_part = match.group(1)
                port = f":{args.port}" if args.port else (match.group(2) or ':28081')
                path = args.path
                HOST = f"http://{host_part}{port}{path}"
    
    IDENTIFIER = args.identifier
    PASSWORD = args.password
    
    print("OpenSilex Smart Demo Variables Creator")
    print("=" * 50)
    print(f"Host: {HOST}")
    print(f"User: {IDENTIFIER}")
    
    # Connect to OpenSilex
    client = connect_to_opensilex(HOST, IDENTIFIER, PASSWORD)
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
        choice = input("\nChoose an option (1/2/3): ")
        
        if choice == "1":
            print("Using existing concepts to create variables...")
            # TODO: Could implement logic to use existing concepts
            print("⚠️ Feature not yet implemented. Please use option 2 or 3.")
            sys.exit(0)
        elif choice == "2":
            print("Creating additional basic concepts...")
        elif choice == "3":
            print("Exiting without changes.")
            sys.exit(0)
        else:
            print("Invalid choice. Exiting.")
            sys.exit(0)
    else:
        print("📭 No concepts found in the system")
        response = input("\nWould you like to create basic demo concepts and variables? (y/n): ")
        
        if response.lower() != 'y':
            print("Exiting without creating anything.")
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
    print("\nYou can now:")
    print("  1. View these variables in the OpenSilex web interface")
    print("  2. Use them to create data entries")
    print("  3. Create additional variables using the web interface or API")

if __name__ == "__main__":
    main()