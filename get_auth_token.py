import opensilexClientToolsPython
from pprint import pprint

def get_opensilex_token(identifier, password, host):
    """
    Authenticate with OpenSILEX and return the access token.
    
    Args:
        identifier (str): User identifier, email or URI
        password (str): User password  
        host (str): OpenSILEX host URL
        
    Returns:
        str: Access token if successful, None if failed
    """
    try:
        # Create API client instance
        pythonClient = opensilexClientToolsPython.ApiClient()
        print(f"Attempting to connect to: {host}")
        print(f"Using identifier: {identifier}")
        
        # Connect to OpenSILEX web service
        pythonClient.connect_to_opensilex_ws(
            identifier=identifier,
            password=password,
            host=host
        )
        
        # Access the token from the client default headers
        # The token is stored in default_headers after successful authentication
        auth_header = pythonClient.default_headers.get('Authorization')
        
        if auth_header:
            # Remove 'Bearer ' prefix if present
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
            else:
                token = auth_header
            print("Authentication successful!")
            print(f"Access token: {token}")
            return token
        else:
            print("Authentication failed: No token received")
            print("Available headers:", pythonClient.default_headers.keys())
            return None
            
    except opensilexClientToolsPython.rest.ApiException as e:
        print(f"API Exception during authentication: {e}")
        print(f"Status code: {e.status}")
        print(f"Reason: {e.reason}")
        if hasattr(e, 'body'):
            print(f"Response body: {e.body}")
        return None
    except Exception as e:
        print(f"Exception during authentication: {e}")
        print(f"Exception type: {type(e).__name__}")
        return None

def main():
    """
    Main function to demonstrate token retrieval
    """
    # Configuration - update these values for your OpenSILEX instance
    identifier = "admin@opensilex.org"
    password = "admin" 
    host = "http://48.209.64.78:28081/sandbox/rest"
    
    print("=== OpenSILEX Authentication Test ===")
    print(f"Host: {host}")
    print(f"Identifier: {identifier}")
    print("=" * 40)
    
    # Get the authentication token
    token = get_opensilex_token(identifier, password, host)
    
    if token:
        print("\n✓ Token successfully obtained!")
        print("You can now use this token for API calls.")
        print(f"Token length: {len(token)} characters")
        
        # Example: Create a variables API instance with the authenticated client
        try:
            pythonClient = opensilexClientToolsPython.ApiClient()
            pythonClient.connect_to_opensilex_ws(
                identifier=identifier,
                password=password,
                host=host
            )
            
            # Now you can use any API with the authenticated client
            variables_api = opensilexClientToolsPython.VariablesApi(pythonClient)
            print("\n✓ Variables API instance created successfully!")
            print("You can now call variables_api methods without needing to pass authorization manually.")
            
        except Exception as e:
            print(f"\n✗ Error creating Variables API: {e}")
        
    else:
        print("\n✗ Failed to obtain token.")
        print("\nTroubleshooting tips:")
        print("1. Check if the host URL is correct and reachable")
        print("2. Verify your username/email and password")
        print("3. Ensure the OpenSILEX instance is running")
        print("4. Check if there are any network/firewall issues")

if __name__ == "__main__":
    main()