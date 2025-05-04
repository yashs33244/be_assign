import requests
import base64
import json
import time
from typing import Dict, Any


BASE_URL = "http://localhost:8000"
session_id = None


def print_response(response):
    """Print response in a readable format"""
    try:
        data = response.json()
        # Don't print the screenshot data to keep the output clean
        if "screenshot" in data:
            data["screenshot"] = "... base64 data ..."
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")
    except:
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")


def start_session() -> str:
    """Start a browser session and return the session ID"""
    global session_id
    
    url = f"{BASE_URL}/session/start"
    payload = {
        "browser": "chromium",
        "headless": True,
        "viewport_width": 1280,
        "viewport_height": 720
    }
    
    print(f"\n=== Starting session ===")
    response = requests.post(url, json=payload)
    print_response(response)
    
    data = response.json()
    session_id = data.get("sessionId")
    return session_id


def navigate_to_url(session_id: str, url: str):
    """Navigate to a URL"""
    api_url = f"{BASE_URL}/action/goto"
    payload = {
        "sessionId": session_id,
        "url": url
    }
    
    print(f"\n=== Navigating to {url} ===")
    response = requests.post(api_url, json=payload)
    print_response(response)
    return response.json()


def click_element(session_id: str, locator: Dict[str, Any]):
    """Click on an element"""
    api_url = f"{BASE_URL}/action/click"
    payload = {
        "sessionId": session_id,
        "locator": locator
    }
    
    print(f"\n=== Clicking on element {locator} ===")
    response = requests.post(api_url, json=payload)
    print_response(response)
    return response.json()


def fill_element(session_id: str, locator: Dict[str, Any], value: str):
    """Fill a form field"""
    api_url = f"{BASE_URL}/action/fill"
    payload = {
        "sessionId": session_id,
        "locator": locator,
        "value": value
    }
    
    print(f"\n=== Filling element {locator} with '{value}' ===")
    response = requests.post(api_url, json=payload)
    print_response(response)
    return response.json()


def close_session(session_id: str):
    """Close the browser session"""
    url = f"{BASE_URL}/session/close"
    payload = {
        "sessionId": session_id
    }
    
    print(f"\n=== Closing session {session_id} ===")
    response = requests.post(url, json=payload)
    print_response(response)
    return response.status_code


def save_screenshot(base64_data: str, filename: str):
    """Save a base64-encoded screenshot to a file"""
    with open(filename, "wb") as f:
        f.write(base64.b64decode(base64_data))
    print(f"Screenshot saved to {filename}")


def main():
    """Main test function"""
    try:
        # Start a session
        session_id = start_session()
        if not session_id:
            print("Failed to start session")
            return
        
        # Navigate to Google
        result = navigate_to_url(session_id, "https://www.google.com")
        if result.get("status") == "success":
            save_screenshot(result["screenshot"], "google.png")
        
        # Fill the search field
        fill_element(session_id, "input[name='q']", "Playwright automation")
        
        # Click the search button using structured locator
        click_element(session_id, {"role": "button", "name": "Google Search"})
        
        # Wait a bit to see the results
        time.sleep(2)
        
        # Navigate to another site
        navigate_to_url(session_id, "https://example.com")
        
        # Finally, close the session
        close_session(session_id)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        # Try to close the session if it exists
        if session_id:
            close_session(session_id)


if __name__ == "__main__":
    main() 