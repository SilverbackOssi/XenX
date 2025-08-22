import requests
import os
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "test_logo.png")
print(f"Test image path: {TEST_IMAGE_PATH}")
print(__file__)
print(os.path.dirname(__file__))


def register_user(user_data):
    """Register a new user"""
    url = f"{BASE_URL}/auth/register"
    response = requests.post(url, json=user_data)
    return response.json(), response.status_code

def login_user(login_data):
    """Login a user and get access token"""
    url = f"{BASE_URL}/auth/login"
    response = requests.post(url, json=login_data)
    return response.json(), response.status_code

def create_enterprise(access_token, enterprise_data):
    """Create a new enterprise/firm"""
    url = f"{BASE_URL}/enterprises/create"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(url, headers=headers, json=enterprise_data)
    return response.json(), response.status_code

def upload_logo(access_token, enterprise_id, logo_path):
    """Upload a logo for the enterprise"""
    url = f"{BASE_URL}/enterprises/{enterprise_id}/branding/logo"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Open the image file for uploading
    try:
        with open(logo_path, "rb") as logo_file:
            files = {"logo": (os.path.basename(logo_path), logo_file, "image/png")}
            response = requests.post(url, headers=headers, files=files)
            return response.json(), response.status_code
    except FileNotFoundError:
        print(f"Test file not found: {logo_path}")
        print("Creating a dummy text file for testing...")
        
        # Create a dummy file for testing if the test image doesn't exist
        dummy_path = os.path.join(os.path.dirname(__file__), "dummy_logo.txt")
        with open(dummy_path, "w") as f:
            f.write("This is a dummy file for testing")
        
        with open(dummy_path, "rb") as dummy_file:
            files = {"logo": ("dummy_logo.txt", dummy_file, "text/plain")}
            response = requests.post(url, headers=headers, files=files)
            return response.json(), response.status_code

def delete_logo(access_token, enterprise_id):
    """Delete the enterprise logo"""
    url = f"{BASE_URL}/enterprises/{enterprise_id}/branding/logo"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.delete(url, headers=headers)
    return response.json(), response.status_code

def create_branding(access_token, enterprise_id, branding_data):
    """Set branding information for the enterprise"""
    url = f"{BASE_URL}/enterprises/{enterprise_id}/branding"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(url, headers=headers, json=branding_data)
    return response.json(), response.status_code

def update_branding(access_token, enterprise_id, branding_data):
    """Update branding information for the enterprise"""
    url = f"{BASE_URL}/enterprises/{enterprise_id}/branding"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.patch(url, headers=headers, json=branding_data)
    return response.json(), response.status_code

def get_branding(access_token, enterprise_id):
    """Get branding information for the enterprise"""
    url = f"{BASE_URL}/enterprises/{enterprise_id}/branding"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response.json(), response.status_code

def create_test_image():
    """Create a test image file if it doesn't exist"""
    if not os.path.exists(TEST_IMAGE_PATH):
        try:
            from PIL import Image
            # Create a simple 100x100 red square image
            img = Image.new('RGB', (100, 100), color = (255, 0, 0))
            img.save(TEST_IMAGE_PATH)
            print(f"Created test image at {TEST_IMAGE_PATH}")
            return True
        except ImportError:
            print("PIL not installed. Can't create test image.")
            return False
    return True

def run_branding_tests():
    print("--- Running Enterprise Branding Tests ---")
    
    # Create test image if possible
    has_test_image = create_test_image()
    if not has_test_image:
        print("Warning: No test image available. Logo upload tests may fail.")
    
    # Test data
    current_year = datetime.now().year
    
    # 1. Register owner user
    print("\n1. Registering a new user as enterprise owner...")
    owner_data = {
        "email": "branding_owner@example.com",
        "username": "branding_owner",
        "password": "Password@123",
        "first_name": "Jane",
        "last_name": "Branding"
    }
    response, status_code = register_user(owner_data)
    print(f"Response: {response}, Status Code: {status_code}")
    
    # 2. Login owner
    print("\n2. Logging in the owner...")
    owner_login_data = {
        "username": "branding_owner",
        "password": "Password@123"
    }
    response, status_code = login_user(owner_login_data)
    print(f"Response: {response}, Status Code: {status_code}")
    
    owner_token = response.get("access_token")
    if not owner_token:
        print("Failed to get access token. Exiting tests.")
        return
    
    # 3. Create enterprise
    print("\n3. Creating a new enterprise...")
    enterprise_data = {
        "name": "Branding Test Enterprise",
        "email": "branding.test@example.com",
        "type": "business",
        "default_tax_year": current_year,
        "country": "United States",
        "city": "San Francisco",
        "description": "A test enterprise for branding tests",
        "website": "https://brandingtest.com"
    }
    
    enterprise_response, status_code = create_enterprise(owner_token, enterprise_data)
    print(f"Response: {enterprise_response}, Status Code: {status_code}")
    
    if status_code != 201:
        print("Failed to create enterprise. Exiting tests.")
        return
    
    enterprise_id = enterprise_response.get("id")
    print(f"Created enterprise ID: {enterprise_id}")
    
    # 4. Upload logo
    print("\n4. Uploading logo...")
    logo_response, status_code = upload_logo(owner_token, enterprise_id, TEST_IMAGE_PATH)
    print(f"Response: {logo_response}, Status Code: {status_code}")
    
    # 5. Set branding information
    print("\n5. Setting branding information...")
    branding_data = {
        "primary_color": "#00FF00",
        "accent_color": "#0000FF",
        "footer_text": "© 2025 Test Enterprise. All rights reserved."
    }
    
    branding_response, status_code = create_branding(owner_token, enterprise_id, branding_data)
    print(f"Response: {branding_response}, Status Code: {status_code}")
    
    # 6. Get branding information
    print("\n6. Getting branding information...")
    branding_info, status_code = get_branding(owner_token, enterprise_id)
    print(f"Response: {branding_info}, Status Code: {status_code}")
    
    # 7. Update branding information
    print("\n7. Updating branding information...")
    updated_branding = {
        "primary_color": "#FF0000",
        "footer_text": "Updated footer text"
    }
    
    update_response, status_code = update_branding(owner_token, enterprise_id, updated_branding)
    print(f"Response: {update_response}, Status Code: {status_code}")
    
    # 8. Get updated branding information
    print("\n8. Getting updated branding information...")
    updated_info, status_code = get_branding(owner_token, enterprise_id)
    print(f"Response: {updated_info}, Status Code: {status_code}")
    
    # # 9. Delete logo
    # print("\n9. Deleting logo...")
    # delete_response, status_code = delete_logo(owner_token, enterprise_id)
    # print(f"Response: {delete_response}, Status Code: {status_code}")
    
    # # 10. Verify logo deletion
    # print("\n10. Verifying logo deletion...")
    # final_info, status_code = get_branding(owner_token, enterprise_id)
    # print(f"Response: {final_info}, Status Code: {status_code}")
    # if final_info.get("logo_url") is None:
    #     print("Logo successfully deleted")
    # else:
    #     print("Logo was not deleted properly")

if __name__ == "__main__":
    run_branding_tests()
