import requests
import json

BASE_URL = "http://localhost:8000" 

def register_user(user_data):
    url = f"{BASE_URL}/auth/register"
    response = requests.post(url, json=user_data)
    return response.json(), response.status_code

def login_user(login_data):
    url = f"{BASE_URL}/auth/login"
    response = requests.post(url, json=login_data)
    return response.json(), response.status_code

def get_profile(access_token):
    url = f"{BASE_URL}/users/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response.json(), response.status_code

def update_profile(access_token, update_data):
    url = f"{BASE_URL}/users/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.put(url, headers=headers, json=update_data)
    return response.json(), response.status_code

def change_password(access_token, password_data):
    url = f"{BASE_URL}/users/me/change-password"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.put(url, headers=headers, json=password_data)
    return response.json(), response.status_code

def get_user_subscription(access_token):
    url = f"{BASE_URL}/users/me/subscription"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response.json(), response.status_code

def run_profile_tests():
    print("--- Running Profile Endpoint Tests ---")

    # 1. Register a new user
    print("\n1. Registering a new user...")
    user_data = {
        "email": "test_profile@example.com",
        "username": "test_profile_user",
        "password": "Password@123"
    }
    response, status_code = register_user(user_data)
    print(f"Response: {response}, Status Code: {status_code}")

    # 2. Logging in the user
    print("\n2. Logging in the user...")
    login_data = {
        "username": "test_profile_user",
        "password": "Password@123"
    }
    response, status_code = login_user(login_data)
    print(f"Response: {response}, Status Code: {status_code}")

    access_token = response.get("access_token")
    print(f"Access Token: {access_token}")

    # 3. Getting user profile
    print("\n3. Getting user profile...")
    response, status_code = get_profile(access_token)
    print(f"Response: {response}, Status Code: {status_code}")

    # 4. Updating user profile
    print("\n4. Updating user profile...")
    update_data = {
        "email": "updated_profile@example.com",
        "username": "updated_profile_user"
    }
    response, status_code = update_profile(access_token, update_data)
    print(f"Response: {response}, Status Code: {status_code}")

    # 5. Changing user password
    print("\n5. Changing user password...")
    password_data = {
        "old_password": "Password123",
        "new_password": "NewPassword@123"
    }
    response, status_code = change_password(access_token, password_data)
    print(f"Response: {response}, Status Code: {status_code}")

    # 6. Getting user subscription
    print("\n6. Getting user subscription...")
    response, status_code = get_user_subscription(access_token)
    print(f"Response: {response}, Status Code: {status_code}")

if __name__ == "__main__":
    run_profile_tests()

