import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000" 

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

def invite_teammate(access_token, enterprise_id, invitation_data):
    """Invite a teammate to an enterprise"""
    url = f"{BASE_URL}/enterprises/{enterprise_id}/invite"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(url, headers=headers, json=invitation_data)
    return response.json(), response.status_code

def invite_multiple_teammates(access_token, enterprise_id, invitations):
    """Invite multiple teammates to an enterprise"""
    url = f"{BASE_URL}/enterprises/{enterprise_id}/invite-multiple"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {"invitations": invitations}
    response = requests.post(url, headers=headers, json=data)
    return response.json(), response.status_code

def accept_invitation(token):
    """Accept an invitation to join an enterprise"""
    url = f"{BASE_URL}/enterprises/accept-invitation"
    params = {"token": token}
    response = requests.get(url, params=params)
    return response.json(), response.status_code

def run_enterprise_tests():
    print("--- Running Enterprise Management Tests ---")
    
    # Test data
    current_year = datetime.now().year
    
    # 1. Register owner user
    print("\n1. Registering a new user as enterprise owner...")
    owner_data = {
        "email": "enterprise_owner@example.com",
        "username": "enterprise_owner",
        "password": "Password@123",
        "first_name": "John",
        "last_name": "Owner"
    }
    response, status_code = register_user(owner_data)
    print(f"Response: {response}, Status Code: {status_code}")
    
    # 2. Login owner
    print("\n2. Logging in the owner...")
    owner_login_data = {
        "username": "enterprise_owner",
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
        "name": "Test Enterprise",
        "email": "test.enterprise@example.com",
        "type": "business",
        "default_tax_year": current_year,
        "country": "United States",
        "city": "New York",
        "description": "A test enterprise",
        "website": "https://testenterprise.com"
    }
    
    enterprise_response, status_code = create_enterprise(owner_token, enterprise_data)
    print(f"Response: {enterprise_response}, Status Code: {status_code}")
    
    if status_code != 201:
        print("Failed to create enterprise. Exiting tests.")
        return
    
    enterprise_id = enterprise_response.get("id")
    print(f"Created enterprise ID: {enterprise_id}")
    
    # 4. Register staff user
    print("\n4. Registering a new user as staff member...")
    staff_data = {
        "email": "staff_member@example.com",
        "username": "staff_member",
        "password": "Password@123",
        "first_name": "Jane",
        "last_name": "Staff"
    }
    response, status_code = register_user(staff_data)
    print(f"Response: {response}, Status Code: {status_code}")
    
    # 5. Invite staff to enterprise
    print("\n5. Inviting staff to enterprise...")
    invitation_data = {
        "email": "staff_member@example.com",
        "role": "assistant"
    }
    
    invitation_response, status_code = invite_teammate(owner_token, enterprise_id, invitation_data)
    print(f"Response: {invitation_response}, Status Code: {status_code}")

    # 5b. Invite multiple teammates to enterprise
    print("\n5b. Inviting multiple teammates to enterprise...")
    multiple_invitations = [
        {"email": "staff1@example.com", "role": "assistant"},
        {"email": "staff2@example.com", "role": "assistant"},
        {"email": "staff3@example.com", "role": "assistant"}
    ]
    multi_invite_response, multi_invite_status = invite_multiple_teammates(owner_token, enterprise_id, multiple_invitations)
    print(f"Response: {multi_invite_response}, Status Code: {multi_invite_status}")
    
    # Can not truly test accepting invite

if __name__ == "__main__":
    run_enterprise_tests()
