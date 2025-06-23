#!/usr/bin/env python3
"""
OpenSilex Smart Demo Variables Creator

This script first discovers what ontology concepts (entities, characteristics, methods, units)
are available in your OpenSilex system, then creates demo variables using those existing concepts.
If no concepts exist, it will offer to create basic ones first.
"""

import opensilexClientToolsPython
from opensilexClientToolsPython.models.variable_creation_dto import VariableCreationDTO
from opensilexClientToolsPython.models.entity_creation_dto import EntityCreationDTO
from opensilexClientToolsPython.models.characteristic_creation_dto import CharacteristicCreationDTO
from opensilexClientToolsPython.models.method_creation_dto import MethodCreationDTO
from opensilexClientToolsPython.models.unit_creation_dto import UnitCreationDTO
from opensilexClientToolsPython.models.interest_entity_creation_dto import InterestEntityCreationDTO
import sys

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
    except:
        return False

def create_basic_concepts(variables_api):
    """Create basic ontology concepts if none exist"""
    print("\n🏗️ Creating basic ontology concepts...")
    print("-" * 60)
    
    created_concepts = {
        'entities': [],
        'characteristics': [],
        'methods': [],
        'units': []
    }
    
    # Basic entities
    basic_entities = [
        {"name": "Plant", "description": "Plant organism"},
        {"name": "Soil", "description": "Soil medium"},
        {"name": "Environment", "description": "Environmental conditions"},
        {"name": "Leaf", "description": "Plant leaf"},
        {"name": "Seed", "description": "Plant seed"}
    ]
    
    # Basic characteristics
    basic_characteristics = [
        {"name": "Height", "description": "Vertical measurement"},
        {"name": "Weight", "description": "Mass measurement"},
        {"name": "Temperature", "description": "Thermal measurement"},
        {"name": "Moisture", "description": "Water content"},
        {"name": "Color", "description": "Visual color attribute"},
        {"name": "Count", "description": "Numerical count"},
        {"name": "Area", "description": "Surface area measurement"},
        {"name": "Length", "description": "Linear measurement"}
    ]
    
    # Basic methods
    basic_methods = [
        {"name": "Manual Measurement", "description": "Manual measurement with tools"},
        {"name": "Visual Observation", "description": "Visual assessment"},
        {"name": "Sensor Reading", "description": "Automated sensor measurement"},
        {"name": "Laboratory Analysis", "description": "Laboratory analytical method"},
        {"name": "Digital Image Analysis", "description": "Computer vision analysis"}
    ]
    
    # Basic units
    basic_units = [
        {"name": "centimeter", "symbol": "cm", "description": "Length unit"},
        {"name": "gram", "symbol": "g", "description": "Mass unit"},
        {"name": "celsius", "symbol": "°C", "description": "Temperature unit"},
        {"name": "percent", "symbol": "%", "description": "Percentage unit"},
        {"name": "count", "symbol": "#", "description": "Count unit"},
        {"name": "meter", "symbol": "m", "description": "Length unit"},
        {"name": "kilogram", "symbol": "kg", "description": "Mass unit"},
        {"name": "liter", "symbol": "L", "description": "Volume unit"}
    ]
    
    # Create entities
    print("\n📊 Creating entities...")
    for entity_data in basic_entities:
        try:
            entity = EntityCreationDTO(**entity_data)
            result = variables_api.create_entity(body=entity)
            created_concepts['entities'].append({'name': entity_data['name'], 'uri': result})
            print(f"  ✓ Created entity: {entity_data['name']}")
        except Exception as e:
            print(f"  ✗ Failed to create entity {entity_data['name']}: {e}")
    
    # Create characteristics
    print("\n🎯 Creating characteristics...")
    for char_data in basic_characteristics:
        try:
            characteristic = CharacteristicCreationDTO(**char_data)
            result = variables_api.create_characteristic(body=characteristic)
            created_concepts['characteristics'].append({'name': char_data['name'], 'uri': result})
            print(f"  ✓ Created characteristic: {char_data['name']}")
        except Exception as e:
            print(f"  ✗ Failed to create characteristic {char_data['name']}: {e}")
    
    # Create methods
    print("\n🔬 Creating methods...")
    for method_data in basic_methods:
        try:
            method = MethodCreationDTO(**method_data)
            result = variables_api.create_method(body=method)
            created_concepts['methods'].append({'name': method_data['name'], 'uri': result})
            print(f"  ✓ Created method: {method_data['name']}")
        except Exception as e:
            print(f"  ✗ Failed to create method {method_data['name']}: {e}")
    
    # Create units
    print("\n📏 Creating units...")
    for unit_data in basic_units:
        try:
            unit = UnitCreationDTO(**unit_data)
            result = variables_api.create_unit(body=unit)
            created_concepts['units'].append({'name': unit_data['name'], 'uri': result})
            print(f"  ✓ Created unit: {unit_data['name']}")
        except Exception as e:
            print(f"  ✗ Failed to create unit {unit_data['name']}: {e}")
    
    return created_concepts

def create_demo_variables(variables_api, created_concepts):
    """Create demo variables using the created concepts"""
    print(f"\n🛠️ Creating demo variables using created concepts...")
    print("-" * 60)
    
    created_variables = []
    failed_variables = []
    
    # Helper function to find concept by name
    def find_concept_uri(concepts_list, name_contains):
        for concept in concepts_list:
            if name_contains.lower() in concept['name'].lower():
                return concept['uri']
        return None
    
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
            "entity": plant_uri,
            "characteristic": height_uri,
            "method": manual_uri,
            "unit": cm_uri,
            "datatype": "http://www.w3.org/2001/XMLSchema#decimal"
        })
    
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
    
    # Create the variables
    print("\n📐 Creating variables...")
    for var_data in demo_variables:
        try:
            variable = VariableCreationDTO(**var_data)
            result = variables_api.create_variable(body=variable)
            created_variables.append({
                'name': var_data['name'],
                'uri': result,
                'data': var_data
            })
            print(f"  ✓ Created variable: {var_data['name']}")
        except Exception as e:
            failed_variables.append({
                'name': var_data['name'],
                'error': str(e),
                'data': var_data
            })
            print(f"  ✗ Failed to create variable {var_data['name']}: {e}")
    
    return created_variables, failed_variables

def main():
    """Main function"""
    print("OpenSilex Smart Demo Variables Creator")
    print("=" * 50)
    
    # Configuration
    host = "http://48.209.64.78:28081/sandbox/rest"
    identifier = "admin@opensilex.org"  
    password = "admin"
    
    print(f"Host: {host}")
    print(f"User: {identifier}")
    
    # Connect to OpenSilex
    client = connect_to_opensilex(host, identifier, password)
    if not client:
        sys.exit(1)
    
    # Create Variables API instance
    try:
        variables_api = opensilexClientToolsPython.VariablesApi(client)
    except Exception as e:
        print(f"✗ Failed to create Variables API instance: {e}")
        sys.exit(1)
    
    # Check if we have existing concepts
    print("\n🔍 Checking for existing concepts...")
    has_concepts = check_if_concepts_exist(variables_api)
    
    if has_concepts:
        print("✓ Found existing concepts in the system")
        print("⚠️ This script is designed for empty systems. Please use the existing concepts.")
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
            print(f"  - {var['name']} ({var['uri']})")
    
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