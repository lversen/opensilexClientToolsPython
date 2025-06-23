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

def discover_available_concepts(variables_api):
    """Discover what ontology concepts are already available in the system"""
    print("\n🔍 Discovering available concepts in your OpenSilex system...")
    print("-" * 60)
    
    concepts = {
        'entities': [],
        'characteristics': [],
        'methods': [],
        'units': [],
        'entities_of_interest': []
    }
    
    try:
        # Get entities
        entities = variables_api.search_entities(page_size=100)
        concepts['entities'] = list(entities) if entities else []
        print(f"📊 Found {len(concepts['entities'])} entities")
        
        # Get characteristics  
        characteristics = variables_api.search_characteristics(page_size=100)
        concepts['characteristics'] = list(characteristics) if characteristics else []
        print(f"🎯 Found {len(concepts['characteristics'])} characteristics")
        
        # Get methods
        methods = variables_api.search_methods(page_size=100)
        concepts['methods'] = list(methods) if methods else []
        print(f"🔬 Found {len(concepts['methods'])} methods")
        
        # Get units
        units = variables_api.search_units(page_size=100)
        concepts['units'] = list(units) if units else []
        print(f"📏 Found {len(concepts['units'])} units")
        
        # Get entities of interest
        try:
            entities_of_interest = variables_api.search_interest_entity(page_size=100)
            concepts['entities_of_interest'] = list(entities_of_interest) if entities_of_interest else []
            print(f"⭐ Found {len(concepts['entities_of_interest'])} entities of interest")
        except AttributeError as ae:
            print(f"⚠️ Note: Entities of interest not available: {ae}")
            concepts['entities_of_interest'] = []
        
    except Exception as e:
        print(f"⚠️ Error discovering concepts: {e}")
    
    return concepts

def display_available_concepts(concepts):
    """Display available concepts in a user-friendly way"""
    print("\n📋 Available Concepts:")
    print("=" * 60)
    
    for concept_type, items in concepts.items():
        if items:
            print(f"\n{concept_type.upper().replace('_', ' ')}:")
            # Convert to list if needed and handle different response types
            items_list = list(items) if hasattr(items, '__iter__') and not isinstance(items, str) else []
            
            for i, item in enumerate(items_list[:10], 1):  # Show first 10
                name = getattr(item, 'name', 'N/A')
                uri = getattr(item, 'uri', 'N/A')
                print(f"  [{i:2d}] {name} ({uri})")
            if len(items_list) > 10:
                print(f"  ... and {len(items_list) - 10} more")
        else:
            print(f"\n{concept_type.upper().replace('_', ' ')}: None found")

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
    print("Creating entities...")
    for entity_data in basic_entities:
        try:
            entity = EntityCreationDTO(**entity_data)
            result = variables_api.create_entity(body=entity)
            created_concepts['entities'].append({'name': entity_data['name'], 'uri': result})
            print(f"✓ Created entity: {entity_data['name']}")
        except Exception as e:
            print(f"✗ Failed to create entity {entity_data['name']}: {e}")
    
    # Create characteristics
    print("Creating characteristics...")
    for char_data in basic_characteristics:
        try:
            characteristic = CharacteristicCreationDTO(**char_data)
            result = variables_api.create_characteristic(body=characteristic)
            created_concepts['characteristics'].append({'name': char_data['name'], 'uri': result})
            print(f"✓ Created characteristic: {char_data['name']}")
        except Exception as e:
            print(f"✗ Failed to create characteristic {char_data['name']}: {e}")
    
    # Create methods
    print("Creating methods...")
    for method_data in basic_methods:
        try:
            method = MethodCreationDTO(**method_data)
            result = variables_api.create_method(body=method)
            created_concepts['methods'].append({'name': method_data['name'], 'uri': result})
            print(f"✓ Created method: {method_data['name']}")
        except Exception as e:
            print(f"✗ Failed to create method {method_data['name']}: {e}")
    
    # Create units
    print("Creating units...")
    for unit_data in basic_units:
        try:
            unit = UnitCreationDTO(**unit_data)
            result = variables_api.create_unit(body=unit)
            created_concepts['units'].append({'name': unit_data['name'], 'uri': result})
            print(f"✓ Created unit: {unit_data['name']}")
        except Exception as e:
            print(f"✗ Failed to create unit {unit_data['name']}: {e}")
    
    return created_concepts

def create_demo_variables_from_concepts(variables_api, concepts):
    """Create demo variables using available concepts"""
    
    # Convert all concept lists to ensure they're proper lists
    for key in concepts:
        if concepts[key]:
            concepts[key] = list(concepts[key]) if hasattr(concepts[key], '__iter__') and not isinstance(concepts[key], str) else []
    
    # Check if we have enough concepts to create variables
    if (not concepts['entities'] or not concepts['characteristics'] or 
        not concepts['methods'] or not concepts['units']):
        print("\n⚠️ Insufficient concepts available to create variables.")
        response = input("Would you like me to create basic concepts first? (y/n): ")
        if response.lower() == 'y':
            created = create_basic_concepts(variables_api)
            # Refresh concepts
            concepts = discover_available_concepts(variables_api)
            # Convert refreshed concepts to lists too
            for key in concepts:
                if concepts[key]:
                    concepts[key] = list(concepts[key]) if hasattr(concepts[key], '__iter__') and not isinstance(concepts[key], str) else []
        else:
            return [], []
    
    print(f"\n🛠️ Creating demo variables using available concepts...")
    print("-" * 60)
    
    # Get first available concept URIs for demo variables
    entity_uri = concepts['entities'][0].uri if concepts['entities'] else None
    char_uris = [c.uri for c in concepts['characteristics']]
    method_uri = concepts['methods'][0].uri if concepts['methods'] else None
    unit_uris = [u.uri for u in concepts['units']]
    
    # Create demo variables based on available concepts
    demo_variables = []
    
    # Plant height variable (if we have height characteristic and length unit)
    height_char = next((c for c in concepts['characteristics'] if hasattr(c, 'name') and 'height' in c.name.lower()), None)
    length_unit = next((u for u in concepts['units'] if hasattr(u, 'name') and any(word in u.name.lower() for word in ['cm', 'centimeter', 'meter'])), None)
    
    if height_char and length_unit and entity_uri and method_uri:
        demo_variables.append({
            "name": "Plant Height",
            "description": "Height measurement of plant",
            "entity": entity_uri,
            "characteristic": height_char.uri,
            "method": method_uri,
            "unit": length_unit.uri,
            "datatype": "http://www.w3.org/2001/XMLSchema#decimal"
        })
    
    # Temperature variable (if available)
    temp_char = next((c for c in concepts['characteristics'] if hasattr(c, 'name') and 'temp' in c.name.lower()), None)
    temp_unit = next((u for u in concepts['units'] if hasattr(u, 'name') and any(word in u.name.lower() for word in ['celsius', '°c', 'temperature'])), None)
    
    if temp_char and temp_unit and entity_uri and method_uri:
        demo_variables.append({
            "name": "Temperature",
            "description": "Temperature measurement",
            "entity": entity_uri,
            "characteristic": temp_char.uri,
            "method": method_uri,
            "unit": temp_unit.uri,
            "datatype": "http://www.w3.org/2001/XMLSchema#decimal"
        })
    
    # Weight variable (if available)
    weight_char = next((c for c in concepts['characteristics'] if hasattr(c, 'name') and 'weight' in c.name.lower()), None)
    weight_unit = next((u for u in concepts['units'] if hasattr(u, 'name') and any(word in u.name.lower() for word in ['gram', 'kg', 'kilogram'])), None)
    
    if weight_char and weight_unit and entity_uri and method_uri:
        demo_variables.append({
            "name": "Weight",
            "description": "Weight measurement",
            "entity": entity_uri,
            "characteristic": weight_char.uri,
            "method": method_uri,
            "unit": weight_unit.uri,
            "datatype": "http://www.w3.org/2001/XMLSchema#decimal"
        })
    
    # Count variable (if available)
    count_char = next((c for c in concepts['characteristics'] if hasattr(c, 'name') and 'count' in c.name.lower()), None)
    count_unit = next((u for u in concepts['units'] if hasattr(u, 'name') and any(word in u.name.lower() for word in ['count', '#', 'number'])), None)
    
    if count_char and count_unit and entity_uri and method_uri:
        demo_variables.append({
            "name": "Count",
            "description": "Count measurement",
            "entity": entity_uri,
            "characteristic": count_char.uri,
            "method": method_uri,
            "unit": count_unit.uri,
            "datatype": "http://www.w3.org/2001/XMLSchema#integer"
        })
    
    # Generic fallback variables using first available concepts
    if not demo_variables and concepts['entities'] and concepts['characteristics'] and concepts['methods'] and concepts['units']:
        for i in range(min(3, len(concepts['characteristics']), len(concepts['units']))):
            char = concepts['characteristics'][i]
            unit = concepts['units'][i]
            demo_variables.append({
                "name": f"Demo Variable {i+1}",
                "description": f"Demo variable using {getattr(char, 'name', 'unknown characteristic')}",
                "entity": concepts['entities'][0].uri,
                "characteristic": char.uri,
                "method": concepts['methods'][0].uri,
                "unit": unit.uri,
                "datatype": "http://www.w3.org/2001/XMLSchema#decimal"
            })
    
    # Now create the variables
    created_variables = []
    failed_variables = []
    
    for i, var_data in enumerate(demo_variables, 1):
        try:
            variable = VariableCreationDTO(**var_data)
            result = variables_api.create_variable(body=variable)
            
            created_variables.append({
                'name': var_data['name'],
                'uri': result,
                'datatype': var_data['datatype']
            })
            
            print(f"✓ [{i:2d}] Created: {var_data['name']}")
            print(f"    URI: {result}")
            
        except Exception as e:
            failed_variables.append({
                'name': var_data['name'],
                'error': str(e)
            })
            print(f"✗ [{i:2d}] Failed: {var_data['name']}")
            print(f"    Error: {e}")
    
    return created_variables, failed_variables

def main():
    """Main function to create demo variables"""
    
    # Configuration - Update these values for your OpenSilex instance
    HOST = "http://48.209.64.78:28081/sandbox/rest"  # Change to your OpenSilex host
    IDENTIFIER = "admin@opensilex.org"   # Change to your username/email
    PASSWORD = "admin"                   # Change to your password
    
    print("OpenSilex Smart Demo Variables Creator")
    print("=" * 50)
    
    # Get connection details if provided via command line
    if len(sys.argv) > 1:
        HOST = sys.argv[1]
    if len(sys.argv) > 2:
        IDENTIFIER = sys.argv[2]
    if len(sys.argv) > 3:
        PASSWORD = sys.argv[3]
    
    print(f"Host: {HOST}")
    print(f"User: {IDENTIFIER}")
    
    # Connect to OpenSilex
    client = connect_to_opensilex(HOST, IDENTIFIER, PASSWORD)
    if not client:
        sys.exit(1)
    
    # Create variables API instance
    variables_api = opensilexClientToolsPython.VariablesApi(client)
    
    # Discover available concepts
    concepts = discover_available_concepts(variables_api)
    
    # Display what's available
    display_available_concepts(concepts)
    
    # Create demo variables
    created, failed = create_demo_variables_from_concepts(variables_api, concepts)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Successfully created: {len(created)} variables")
    print(f"Failed to create: {len(failed)} variables")
    
    if created:
        print("\n✓ Successfully created variables:")
        for var in created:
            print(f"  - {var['name']}")
    
    if failed:
        print("\n✗ Failed to create variables:")
        for var in failed:
            print(f"  - {var['name']}: {var['error']}")
    
    print(f"\nDemo variables creation completed!")
    
    if len(created) > 0:
        print("You can now use these variables in your experiments and data collection!")
    else:
        print("No variables were created. Check the error messages above for details.")

if __name__ == "__main__":
    main()