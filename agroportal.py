#!/usr/bin/env python3
"""
OpenSilex Agroportal API Connection Example

This script demonstrates how to connect to OpenSilex and use the Agroportal API
to access agricultural ontologies and search for terms.
"""

import opensilexClientToolsPython
from opensilexClientToolsPython.api.agroportal_api_api import AgroportalAPIApi
from opensilexClientToolsPython.models.agroportal_ontologies_config_dto import AgroportalOntologiesConfigDTO
from pprint import pprint

def connect_to_opensilex_and_agroportal():
    """
    Complete example of connecting to OpenSilex and using the Agroportal API
    """
    
    # Configuration - update these values for your OpenSilex instance
    identifier = "admin@opensilex.org"  # Your username/email
    password = "admin"                  # Your password
    host = "http://20.13.0.253:28081/sandbox/rest"  # Your OpenSilex host URL
    
    try:
        # Step 1: Create and authenticate API client
        print("=== Connecting to OpenSilex ===")
        client = opensilexClientToolsPython.ApiClient()
        
        # Connect to OpenSilex web service (handles authentication automatically)
        client.connect_to_opensilex_ws(
            identifier=identifier,
            password=password,
            host=host
        )
        print("✓ Successfully connected to OpenSilex!")
        
        # Step 2: Create Agroportal API instance
        print("\n=== Creating Agroportal API Instance ===")
        agroportal_api = AgroportalAPIApi(client)
        print("✓ Agroportal API instance created!")
        
        # Step 3: Test connection with ping
        print("\n=== Testing Agroportal Connection ===")
        try:
            ping_result = agroportal_api.ping_agroportal(timeout=5000)
            print(f"✓ Agroportal server ping: {ping_result}")
        except Exception as e:
            print(f"⚠ Ping failed (this might be normal): {e}")
        
        # Step 4: Get available ontologies
        print("\n=== Getting Available Ontologies ===")
        try:
            ontologies = agroportal_api.get_agroportal_ontologies()
            print(f"✓ Found {len(ontologies)} ontologies:")
            
            # Display first few ontologies
            for i, onto in enumerate(ontologies[:5]):
                print(f"  {i+1}. {onto.name} ({onto.acronym})")
            
            if len(ontologies) > 5:
                print(f"  ... and {len(ontologies) - 5} more")
                
        except Exception as e:
            print(f"⚠ Could not retrieve ontologies: {e}")
        
        # Step 5: Search for specific terms
        print("\n=== Searching for Terms ===")
        try:
            # Example: Search for "plant" terms
            search_results = agroportal_api.search_through_agroportal(
                name="plant"  # Search term
            )
            
            print(f"✓ Found {len(search_results)} terms matching 'plant':")
            
            # Display first few results
            for i, term in enumerate(search_results[:3]):
                print(f"\n  {i+1}. {term.name}")
                print(f"     ID: {term.id}")
                print(f"     Ontology: {term.ontology_name}")
                if term.definitions:
                    print(f"     Definition: {term.definitions[0][:100]}...")
                if term.synonym:
                    print(f"     Synonyms: {', '.join(term.synonym[:3])}")
                
        except Exception as e:
            print(f"⚠ Search failed: {e}")
        
        # Step 6: Search within specific ontologies
        print("\n=== Searching Within Specific Ontologies ===")
        try:
            # Example: Search for "leaf" in specific ontologies
            specific_search = agroportal_api.search_through_agroportal(
                name="leaf",
                ontologies=["PO", "TO"]  # Plant Ontology, Trait Ontology
            )
            
            print(f"✓ Found {len(specific_search)} 'leaf' terms in PO and TO ontologies:")
            
            for i, term in enumerate(specific_search[:2]):
                print(f"\n  {i+1}. {term.name} ({term.ontology_name})")
                if term.definitions:
                    print(f"     Definition: {term.definitions[0][:80]}...")
                    
        except Exception as e:
            print(f"⚠ Specific ontology search failed: {e}")
        
        return agroportal_api
        
    except opensilexClientToolsPython.rest.ApiException as e:
        print(f"✗ API Exception: {e}")
        print(f"Status: {e.status}, Reason: {e.reason}")
        return None
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return None

def configure_agroportal_for_opensilex(agroportal_api):
    """
    Example of how to configure Agroportal for different entity types in OpenSilex
    """
    print("\n=== Configuring Agroportal for OpenSilex ===")
    
    # Create configuration for different ontology types
    agroportal_config = AgroportalOntologiesConfigDTO(
        entity_ontologies=["PO", "NCBITAXON"],      # Plant Ontology, NCBI Taxonomy
        trait_ontologies=["TO", "PATO"],            # Trait Ontology, Phenotype Quality
        method_ontologies=["OBI", "MIAPPE"],        # Ontology for Biomedical Investigations
        unit_ontologies=["UO", "PECO"]              # Units Ontology, Plant Environment
    )
    
    print("✓ Agroportal configuration created for:")
    print(f"  - Entity ontologies: {agroportal_config.entity_ontologies}")
    print(f"  - Trait ontologies: {agroportal_config.trait_ontologies}")
    print(f"  - Method ontologies: {agroportal_config.method_ontologies}")
    print(f"  - Unit ontologies: {agroportal_config.unit_ontologies}")
    
    return agroportal_config

def search_ontology_terms_by_category(agroportal_api):
    """
    Example of searching for terms by different categories
    """
    print("\n=== Searching by Categories ===")
    
    categories = {
        "Plant Parts": ["leaf", "root", "stem", "flower"],
        "Measurements": ["height", "width", "weight", "temperature"],
        "Species": ["wheat", "maize", "rice", "tomato"]
    }
    
    for category, terms in categories.items():
        print(f"\n--- {category} ---")
        for term in terms:
            try:
                results = agroportal_api.search_through_agroportal(name=term)
                print(f"  {term}: {len(results)} results")
            except Exception as e:
                print(f"  {term}: Search failed - {e}")

# Quick start example for basic usage
def quick_start_example():
    """
    Minimal example to get started with Agroportal API
    """
    print("\n" + "=" * 30)
    print("QUICK START EXAMPLE")
    print("=" * 30)
    
    # Replace with your OpenSilex details
    host = "http://20.13.0.253:28081/sandbox/rest"
    username = "admin@opensilex.org" 
    password = "admin"
    
    try:
        # 1. Connect to OpenSilex
        client = opensilexClientToolsPython.ApiClient()
        client.connect_to_opensilex_ws(username, password, host)
        
        # 2. Create Agroportal API instance
        agroportal = AgroportalAPIApi(client)
        
        # 3. Search for terms
        results = agroportal.search_through_agroportal(name="plant")
        print(f"Found {len(results)} plant-related terms")
        
        # 4. Get ontologies
        ontologies = agroportal.get_agroportal_ontologies()
        print(f"Available ontologies: {len(ontologies)}")
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    """
    Main function demonstrating Agroportal API usage
    """
    print("OpenSilex Agroportal API Connection Demo")
    print("=" * 50)
    
    # Connect and get API instance
    agroportal_api = connect_to_opensilex_and_agroportal()
    
    if agroportal_api:
        # Configure for OpenSilex
        config = configure_agroportal_for_opensilex(agroportal_api)
        
        # Search by categories
        search_ontology_terms_by_category(agroportal_api)
        
        print("\n" + "=" * 50)
        print("✓ Demo completed successfully!")
        print("\nNext steps:")
        print("1. Modify the configuration values for your OpenSilex instance")
        print("2. Explore specific ontologies relevant to your research")
        print("3. Integrate ontology terms into your variable definitions")
        
    else:
        print("\n✗ Demo failed - check your connection settings")
    
    # Show quick start example
    quick_start_example()

if __name__ == "__main__":
    main()