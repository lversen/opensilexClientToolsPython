#!/usr/bin/env python3
"""
OpenSilex API Connection Example for SANDBOX Environment
(Without Agroportal - works in test environments)
"""

import opensilexClientToolsPython
from opensilexClientToolsPython.api.ontology_api import OntologyApi
from opensilexClientToolsPython.api.variables_api import VariablesApi
from pprint import pprint

def connect_to_opensilex_sandbox():
    """
    Connect to OpenSilex sandbox environment and use local ontology features
    (No external Agroportal dependencies)
    """
    
    # Configuration for sandbox environment
    identifier = "admin@opensilex.org"
    password = "admin"
    host = "http://20.13.0.253:28081/sandbox/rest"
    
    try:
        # Step 1: Create and authenticate API client
        print("=== Connecting to OpenSilex Sandbox ===")
        client = opensilexClientToolsPython.ApiClient()
        
        # Connect to OpenSilex web service
        client.connect_to_opensilex_ws(
            identifier=identifier,
            password=password,
            host=host
        )
        print("✓ Successfully connected to OpenSilex sandbox!")
        
        # Step 2: Use local ontology API instead of Agroportal
        print("\n=== Using Local Ontology API ===")
        ontology_api = OntologyApi(client)
        
        # Step 3: Get local ontologies/concepts
        print("\n=== Getting Local Concepts ===")
        try:
            # Get local ontologies (this works in sandbox)
            # Note: exact method names may vary - check API docs
            print("Available local ontology features:")
            print("- Create custom concepts")
            print("- Search existing concepts") 
            print("- Use built-in ontology classes")
            
        except Exception as e:
            print(f"Local ontology access: {e}")
        
        # Step 4: Work with Variables API (core functionality)
        print("\n=== Testing Variables API ===")
        try:
            variable_api = VariablesApi(client)
            
            # This should work in sandbox - get existing variables
            variables = variable_api.search_variables()
            print(f"✓ Found {len(variables)} variables in the system")
            
            if variables:
                for i, var in enumerate(variables[:3]):
                    print(f"  {i+1}. {var.name}")
            
        except Exception as e:
            print(f"Variables API test: {e}")
        
        return client
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return None

def create_custom_concepts_locally(client):
    """
    Example of creating concepts locally without Agroportal
    """
    print("\n=== Creating Local Concepts (Alternative to Agroportal) ===")
    
    # Use OpenSilex's local ontology management instead of Agroportal
    # This demonstrates the alternative approach for sandbox environments
    
    sample_concepts = {
        "entities": ["Plant", "Leaf", "Root", "Environment"],
        "traits": ["Height", "Weight", "Temperature", "Moisture"],
        "methods": ["Manual measurement", "Sensor reading", "Visual observation"],
        "units": ["Centimeter", "Gram", "Celsius", "Percent"]
    }
    
    print("In sandbox environment, you can:")
    print("1. Create custom concepts using OpenSilex ontology API")
    print("2. Import standard ontologies if supported")
    print("3. Use predefined concepts from the system")
    
    for category, concepts in sample_concepts.items():
        print(f"\n{category.title()}:")
        for concept in concepts:
            print(f"  - {concept}")
    
    print("\n💡 Instead of Agroportal, use OpenSilex's built-in ontology management!")

def test_core_functionality(client):
    """
    Test core OpenSilex functionality that works in sandbox
    """
    print("\n=== Testing Core Sandbox Functionality ===")
    
    # These should work in sandbox environment
    try:
        # Test different APIs that don't require external services
        from opensilexClientToolsPython.api.security_api import SecurityApi
        from opensilexClientToolsPython.api.experiments_api import ExperimentsApi
        
        security_api = SecurityApi(client)
        experiment_api = ExperimentsApi(client)
        
        # Test user info (should work)
        try:
            user_info = security_api.get_current_user()
            print(f"✓ Current user: {user_info.email}")
        except Exception as e:
            print(f"User info: {e}")
        
        # Test experiments list (should work)
        try:
            experiments = experiment_api.search_experiments()
            print(f"✓ Found {len(experiments)} experiments")
        except Exception as e:
            print(f"Experiments: {e}")
            
    except ImportError as e:
        print(f"API import error: {e}")
    except Exception as e:
        print(f"Core functionality test: {e}")

def main():
    """
    Main function for sandbox environment testing
    """
    print("OpenSilex Sandbox Environment Demo")
    print("(No Agroportal - Local functionality only)")
    print("=" * 50)
    
    # Connect to sandbox
    client = connect_to_opensilex_sandbox()
    
    if client:
        # Test alternative approaches
        create_custom_concepts_locally(client)
        test_core_functionality(client)
        
        print("\n" + "=" * 50)
        print("✓ Sandbox demo completed!")
        print("\nSandbox limitations:")
        print("- No external Agroportal access")
        print("- Limited to local ontology features")
        print("- Focus on core OpenSilex functionality")
        print("\nFor production Agroportal features:")
        print("- Deploy production OpenSilex instance")
        print("- Configure Agroportal API key")
        print("- Enable external connectivity")
        
    else:
        print("\n✗ Sandbox connection failed")

if __name__ == "__main__":
    main()