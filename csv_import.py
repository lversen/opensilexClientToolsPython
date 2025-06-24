#!/usr/bin/env python3
"""
OpenSilex CSV Data Import Program

This program creates example CSV data and imports it via the OpenSilex API.
The CSV format matches the expected structure shown in the interface.
"""

import csv
import io
import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import opensilexClientToolsPython
from opensilexClientToolsPython.api import data_api
from opensilexClientToolsPython.rest import ApiException


class OpenSilexCSVImporter:
    """Class to handle CSV data import to OpenSilex via API"""
    
    def __init__(self, base_url: str, username: str, password: str):
        """
        Initialize the OpenSilex API client
        
        Args:
            base_url: OpenSilex server base URL
            username: Username for authentication
            password: Password for authentication
        """
        self.base_url = base_url
        self.username = username
        self.password = password
        self.token = None
        self.api_client = None
        self.data_api_instance = None
        
    def authenticate_alternative(self) -> bool:
        """
        Alternative authentication method using OpenSilex client directly
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            # Try using the security API for authentication
            from opensilexClientToolsPython.api import security_api
            
            configuration = opensilexClientToolsPython.Configuration()
            configuration.host = self.base_url
            
            api_client = opensilexClientToolsPython.ApiClient(configuration)
            security_api_instance = security_api.SecurityApi(api_client)
            
            # Create authentication request
            from opensilexClientToolsPython.models import AuthenticationDTO
            auth_request = AuthenticationDTO(
                identifier=self.username,
                password=self.password
            )
            
            print(f"Trying alternative authentication...")
            result = security_api_instance.authenticate(body=auth_request)
            
            if hasattr(result, 'token'):
                self.token = result.token
                print(f"Alternative auth successful! Token: {self.token[:20]}...")
                
                # Set up API client with token
                configuration.access_token = self.token
                self.api_client = opensilexClientToolsPython.ApiClient(configuration)
                self.api_client.default_headers['Authorization'] = f"Bearer {self.token}"
                self.data_api_instance = data_api.DataApi(self.api_client)
                
                return True
            else:
                print("Alternative authentication failed - no token in response")
                return False
                
        except Exception as e:
            print(f"Alternative authentication error: {e}")
            return False
    
    def authenticate(self) -> bool:
        """
        Authenticate with OpenSilex API and get access token
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            # Authentication endpoint
            auth_url = f"{self.base_url}/security/authenticate"
            auth_data = {
                "identifier": self.username,
                "password": self.password
            }
            
            print(f"Authenticating with: {auth_url}")
            response = requests.post(auth_url, json=auth_data)
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"Auth response keys: {response_data.keys()}")
                
                # Handle OpenSilex response format with metadata/result structure
                self.token = None
                
                # First check if token is in result field
                if 'result' in response_data and response_data['result']:
                    result = response_data['result']
                    print(f"Result type: {type(result)}, Content: {result}")
                    
                    # If result is a string, it might be the token
                    if isinstance(result, str):
                        self.token = result
                    # If result is a dict, look for token-like keys
                    elif isinstance(result, dict):
                        token_keys = ['access_token', 'token', 'bearer', 'jwt']
                        for key in token_keys:
                            if key in result:
                                self.token = result[key]
                                break
                
                # Fallback: check top level for token keys
                if not self.token:
                    token_keys = ['access_token', 'token', 'bearer', 'jwt']
                    for key in token_keys:
                        if key in response_data:
                            self.token = response_data[key]
                            break
                
                if self.token:
                    # Safely display token (check if it's a string first)
                    if isinstance(self.token, str) and len(self.token) > 20:
                        token_display = self.token[:20] + "..."
                    else:
                        token_display = str(self.token)
                    print(f"Found token: {token_display}")
                    
                    # Configure API client AFTER getting token
                    configuration = opensilexClientToolsPython.Configuration()
                    configuration.host = self.base_url
                    configuration.access_token = self.token  # Try setting it in configuration
                    
                    self.api_client = opensilexClientToolsPython.ApiClient(configuration)
                    
                    # Also try setting in headers
                    self.api_client.default_headers['Authorization'] = f"Bearer {self.token}"
                    
                    self.data_api_instance = data_api.DataApi(self.api_client)
                    
                    print("Authentication successful!")
                    return True
                else:
                    print(f"No token found in response. Full response: {response_data}")
                    return False
                
            else:
                print(f"Authentication failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    def create_example_csv_data(self) -> str:
        """
        Create example CSV data matching the expected format
        
        Returns:
            str: CSV content as string
        """
        # Define the CSV headers based on the expected format
        headers = [
            "Experiment",
            "Target", 
            "Device",
            "Date",
            "Uri:variable1",
            "Uri:variable2", 
            "Uri:variable3",
            "Annotation"
        ]
        
        # Generate example data rows
        example_data = []
        base_date = datetime.now() - timedelta(days=30)
        
        experiments = [
            "http://opensilex.test/experiment/exp001",
            "http://opensilex.test/experiment/exp002"
        ]
        
        targets = [
            "http://opensilex.test/scientific-object/plant001",
            "http://opensilex.test/scientific-object/plant002", 
            "http://opensilex.test/scientific-object/plant003"
        ]
        
        devices = [
            "http://opensilex.test/device/sensor001",
            "http://opensilex.test/device/sensor002"
        ]
        
        variables = {
            "Uri:variable1": "http://opensilex.test/variable/height",
            "Uri:variable2": "http://opensilex.test/variable/weight", 
            "Uri:variable3": "http://opensilex.test/variable/temperature"
        }
        
        # Generate 20 example measurements
        for i in range(20):
            measurement_date = base_date + timedelta(days=i)
            date_str = measurement_date.strftime("%Y-%m-%d")
            
            row = [
                experiments[i % len(experiments)],
                targets[i % len(targets)],
                devices[i % len(devices)],
                date_str,
                f"{15.5 + (i * 0.5):.1f}",  # Height values
                f"{2.3 + (i * 0.1):.1f}",   # Weight values  
                f"{22.0 + (i * 0.3):.1f}",  # Temperature values
                f"Measurement {i+1} - Automated data collection"
            ]
            example_data.append(row)
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        # Write headers
        writer.writerow(headers)
        
        # Write data rows
        for row in example_data:
            writer.writerow(row)
            
        csv_content = output.getvalue()
        output.close()
        
        return csv_content
    
    def save_csv_to_file(self, csv_content: str, filename: str = "example_data.csv") -> str:
        """
        Save CSV content to file
        
        Args:
            csv_content: CSV data as string
            filename: Output filename
            
        Returns:
            str: Path to saved file
        """
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            file.write(csv_content)
        
        print(f"CSV data saved to: {filename}")
        return filename
    
    def test_api_connection(self) -> bool:
        """
        Test API connection with a simple call
        
        Returns:
            bool: True if API is accessible, False otherwise
        """
        try:
            # Try to get used variables to test the connection
            result = self.data_api_instance.get_used_variables()
            print("API connection test successful!")
            return True
        except ApiException as e:
            print(f"API connection test failed: {e}")
            print(f"Status code: {e.status}")
            print(f"Reason: {e.reason}")
            return False
        except Exception as e:
            print(f"API connection error: {e}")
            return False
    
    def import_csv_data_direct(self, 
                             csv_file_path: str, 
                             provenance_uri: str,
                             experiment_uri: Optional[str] = None) -> Dict:
        """
        Import CSV data using direct HTTP request as fallback
        
        Args:
            csv_file_path: Path to CSV file
            provenance_uri: Provenance URI for the data
            experiment_uri: Optional experiment URI
            
        Returns:
            Dict: API response with validation results
        """
        try:
            import_url = f"{self.base_url}/core/data/import"
            
            # Prepare headers
            headers = {
                'Authorization': f'Bearer {self.token}'
            }
            
            # Prepare form data
            data = {
                'provenance': provenance_uri
            }
            
            if experiment_uri:
                data['experiment'] = experiment_uri
            
            # Prepare file upload
            with open(csv_file_path, 'rb') as file:
                files = {
                    'file': ('example_data.csv', file, 'text/csv')
                }
                
                print(f"Direct API call to: {import_url}")
                print(f"Data: {data}")
                print(f"Headers: {headers}")
                
                response = requests.post(
                    import_url, 
                    data=data, 
                    files=files, 
                    headers=headers
                )
            
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {response.headers}")
            
            if response.status_code in [200, 201]:
                result_data = response.json()
                print(f"Direct import successful!")
                print(f"Response: {result_data}")
                
                return {
                    "success": True,
                    "response": result_data,
                    "status_code": response.status_code
                }
            else:
                print(f"Direct import failed: {response.status_code}")
                print(f"Response text: {response.text}")
                
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }
                
        except Exception as e:
            print(f"Direct import error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def import_csv_data(self, 
                       csv_file_path: str, 
                       provenance_uri: str,
                       experiment_uri: Optional[str] = None) -> Dict:
        """
        Import CSV data via OpenSilex API
        
        Args:
            csv_file_path: Path to CSV file
            provenance_uri: Provenance URI for the data
            experiment_uri: Optional experiment URI
            
        Returns:
            Dict: API response with validation results
        """
        try:
            print(f"Attempting to import CSV: {csv_file_path}")
            print(f"Provenance URI: {provenance_uri}")
            print(f"Experiment URI: {experiment_uri}")
            print(f"Using token: {self.token[:20] if self.token else 'None'}...")
            
            # Read the CSV file as binary data for proper upload
            with open(csv_file_path, 'rb') as file:
                file_content = file.read()
            
            print(f"File size: {len(file_content)} bytes")
            
            # Try the import with binary file content
            result = self.data_api_instance.import_csv_data(
                provenance=provenance_uri,
                file=file_content,
                experiment=experiment_uri
            )
            
            print("CSV import successful!")
            print(f"Result type: {type(result)}")
            
            # Handle different response formats
            objects_imported = 0
            validation_token = None
            
            if hasattr(result, 'nb_object_imported'):
                objects_imported = result.nb_object_imported
                print(f"Objects imported: {objects_imported}")
            
            if hasattr(result, 'validation_token') and result.validation_token:
                validation_token = result.validation_token
                print(f"Validation token: {validation_token}")
            
            # Check for validation errors
            if hasattr(result, 'missing_headers') and result.missing_headers:
                print(f"Missing headers: {result.missing_headers}")
            
            if hasattr(result, 'datatype_errors') and result.datatype_errors:
                print(f"Datatype errors: {result.datatype_errors}")
            
            # Print all attributes for debugging
            print(f"Result attributes: {[attr for attr in dir(result) if not attr.startswith('_')]}")
                
            return {
                "success": True,
                "objects_imported": objects_imported,
                "validation_token": validation_token,
                "result": result
            }
            
        except ApiException as e:
            print(f"API Exception during import: {e}")
            print(f"Status code: {e.status}")
            print(f"Reason: {e.reason}")
            if hasattr(e, 'body'):
                print(f"Body: {e.body}")
            return {
                "success": False,
                "error": str(e),
                "status_code": e.status
            }
        except Exception as e:
            print(f"Error during import: {e}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_provenance(self, name: str, description: str) -> Optional[str]:
        """
        Create a provenance for the data import
        
        Args:
            name: Provenance name
            description: Provenance description
            
        Returns:
            Optional[str]: Provenance URI if successful
        """
        # This would typically involve calling the provenance API
        # For this example, we'll return a mock URI
        provenance_uri = f"http://opensilex.test/provenance/{name.lower().replace(' ', '_')}"
        print(f"Using provenance URI: {provenance_uri}")
        return provenance_uri


def main():
    """
    Main function to demonstrate CSV import process
    """
    # Configuration - Update these values for your OpenSilex instance
    config = {
        "base_url": "http://20.13.0.253:28081/sandbox/rest",  # Your current server
        "username": "admin@opensilex.org",                    # Update with your username
        "password": "admin"                                   # Update with your password
    }
    
    # Alternative common configurations:
    # Local development:
    # config = {
    #     "base_url": "http://localhost:8080/rest",
    #     "username": "admin@opensilex.org",
    #     "password": "admin"
    # }
    # 
    # Alternative local port:
    # config = {
    #     "base_url": "http://localhost:8666/rest",
    #     "username": "admin",
    #     "password": "admin"
    # }
    
    # Initialize the importer
    importer = OpenSilexCSVImporter(
        base_url=config["base_url"],
        username=config["username"], 
        password=config["password"]
    )
    
    print("OpenSilex CSV Data Import Program")
    print("=" * 40)
    
    # Step 1: Create example CSV data
    print("\n1. Creating example CSV data...")
    csv_content = importer.create_example_csv_data()
    
    # Step 2: Save CSV to file
    print("\n2. Saving CSV data to file...")
    csv_file = importer.save_csv_to_file(csv_content)
    
    # Display sample of CSV content
    print("\nSample CSV content:")
    print("-" * 20)
    lines = csv_content.split('\n')
    for i, line in enumerate(lines[:5]):  # Show first 5 lines
        print(line)
    if len(lines) > 5:
        print(f"... and {len(lines) - 5} more rows")
    
    # Step 3: Authenticate with API
    print("\n3. Authenticating with OpenSilex API...")
    if not importer.authenticate():
        print("Authentication failed. Please check your credentials and server URL.")
        print("Make sure your OpenSilex server is running and accessible.")
        return
    
    # Skip API connection test for now and go straight to import
    print("\n3.5. Skipping API connection test (proceeding directly to import)...")
    
    # Step 4: Create/specify provenance
    print("\n4. Setting up provenance...")
    provenance_uri = importer.create_provenance(
        name="CSV Import Example",
        description="Example data imported via CSV API"
    )
    
    # Step 5: Import CSV data
    print("\n5. Importing CSV data via API...")
    result = importer.import_csv_data(
        csv_file_path=csv_file,
        provenance_uri=provenance_uri,
        experiment_uri="http://opensilex.test/experiment/exp001"  # Optional
    )
    
    # If the API client method failed, try direct HTTP request
    if not result["success"]:
        print("\n5.1. API client method failed, trying direct HTTP request...")
        result = importer.import_csv_data_direct(
            csv_file_path=csv_file,
            provenance_uri=provenance_uri,
            experiment_uri="http://opensilex.test/experiment/exp001"
        )
    
    # Step 6: Display results
    print("\n6. Import Results:")
    print("-" * 20)
    if result["success"]:
        print(f"✓ Import completed successfully!")
        if "objects_imported" in result:
            print(f"✓ Objects imported: {result['objects_imported']}")
        if "validation_token" in result and result["validation_token"]:
            print(f"✓ Validation token: {result['validation_token']}")
        if "response" in result:
            print(f"✓ Server response: {result['response']}")
        if "status_code" in result:
            print(f"✓ HTTP status: {result['status_code']}")
    else:
        print(f"✗ Import failed: {result['error']}")
        if "status_code" in result:
            print(f"  Status code: {result['status_code']}")
    
    print("\nProgram completed!")


if __name__ == "__main__":
    main()