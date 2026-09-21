import os
import sys
import json
import requests
from dotenv import load_dotenv

# Load .env
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

def test_api(endpoint, params=None):
    api_key = os.getenv("RAILWAY_API_KEY")
    api_host = os.getenv("RAILWAY_API_HOST", "irctc1.p.rapidapi.com")
    base_url = os.getenv("RAILWAY_API_BASE_URL", f"https://{api_host}/api/v3")
    
    if not api_key:
        print("ERROR: RAILWAY_API_KEY not found in .env")
        return
        
    url = f"{base_url}/{endpoint}"
    
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": api_host
    }
    
    print(f"Testing Endpoint: {endpoint}")
    print(f"URL: {url}")
    print(f"Params: {params}")
    print("Sending request...")
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"\n--- HTTP Status: {response.status_code} ---")
        
        try:
            data = response.json()
            # Sanitize response if needed
            print(json.dumps(data, indent=2))
        except ValueError:
            print("Response is not JSON:")
            print(response.text[:500])
            
    except Exception as e:
        print(f"Request failed: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_api.py <endpoint> [key=value key=value]")
        print("Example: python test_api.py searchStation searchRules=cstm")
        sys.exit(1)
        
    endpoint = sys.argv[1]
    params = {}
    if len(sys.argv) > 2:
        for arg in sys.argv[2:]:
            if '=' in arg:
                k, v = arg.split('=', 1)
                params[k] = v
                
    test_api(endpoint, params)
