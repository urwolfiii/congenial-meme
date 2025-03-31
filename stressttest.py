import requests
import json
import random
import string
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://127.0.0.1:5000"

def random_string(length=8):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def register_random_user(username, password):
    url = f"{BASE_URL}/api/register"
    payload = {
        "username": username,
        "password": password
    }
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        # Print registration result for debugging
        # print(f"Register {username}: {data}")
        return data
    except Exception as e:
        return {"error": str(e)}

def login_user(username, password):
    url = f"{BASE_URL}/api/login"
    payload = {
        "username": username,
        "password": password
    }
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        # print(f"Login {username}: {data}")
        return data
    except Exception as e:
        return {"error": str(e)}

def spin_for_user(username, bet_amount=10):
    url = f"{BASE_URL}/api/spin"
    payload = {
        "username": username,
        "bet_amount": bet_amount
    }
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        # print(f"Spin for {username}: {data}")
        return data
    except Exception as e:
        return {"error": str(e)}

def simulate_random_user_activity():
    """
    Simulate a full cycle for a random user:
      - Register with random credentials
      - Log in with those credentials
      - Perform a spin
    """
    username = f"user_{random_string(6)}"
    password = random_string(10)
    
    reg_response = register_random_user(username, password)
    # Continue even if registration fails (could already exist)
    login_response = login_user(username, password)
    
    # Only proceed with spin if login succeeded
    if login_response.get("success"):
        spin_response = spin_for_user(username)
    else:
        spin_response = {"error": "login_failed"}
    
    return {
        "username": username,
        "registration": reg_response,
        "login": login_response,
        "spin": spin_response
    }

def stress_test_random_users(num_requests=200):
    results = []
    with ThreadPoolExecutor(max_workers=num_requests) as executor:
        futures = [executor.submit(simulate_random_user_activity) for _ in range(num_requests)]
        for future in as_completed(futures):
            results.append(future.result())
    return results

if __name__ == '__main__':
    # Run the stress test simulating 200 random user sessions concurrently
    responses = stress_test_random_users(num_requests=2000000000000000000)
    
    # Print out all responses in a pretty JSON format
    print(json.dumps(responses, indent=2))
