import requests
import base64
import json
import time
import os
from typing import Dict, Any, Optional


BASE_URL = "http://localhost:8000"
session_id = None

# Create screenshots directory if it doesn't exist
SCREENSHOTS_DIR = "screenshots"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


def save_screenshot(screenshot_base64: str, action_name: str, success: bool):
    """Save a base64 encoded screenshot to disk"""
    if not screenshot_base64:
        return
    
    status = "success" if success else "error"
    filename = f"{SCREENSHOTS_DIR}/{time.strftime('%Y%m%d_%H%M%S')}_{action_name}_{status}.png"
    
    try:
        with open(filename, "wb") as f:
            f.write(base64.b64decode(screenshot_base64))
        print(f"Screenshot saved to {filename}")
    except Exception as e:
        print(f"Error saving screenshot: {str(e)}")


def print_response(response, action_name="unknown"):
    """Print response in a readable format and save screenshot if present"""
    try:
        data = response.json()
        
        # Save screenshot if it exists in the response
        if "screenshot" in data:
            success = data.get("status") == "success"
            save_screenshot(data["screenshot"], action_name, success)
            
            # Don't print the screenshot data to keep the output clean
            data_to_print = data.copy()
            data_to_print["screenshot"] = "... base64 data ..."
        else:
            data_to_print = data
            
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(data_to_print, indent=2)}")
        print("=" * 50)
        
        return data
    except:
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        print("=" * 50)
        return None


def test_start_session() -> Optional[str]:
    """Test the start_session endpoint"""
    print("\n\n=== Testing /session/start ===")
    
    url = f"{BASE_URL}/session/start"
    payload = {
        "browser": "chromium",
        "headless": True,
        "viewport_width": 1280,
        "viewport_height": 720
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    try:
        response = requests.post(url, json=payload)
        data = print_response(response, "session_start")
        if data and "sessionId" in data:
            return data["sessionId"]
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


def test_goto(session_id: str) -> bool:
    """Test the goto endpoint"""
    print("\n\n=== Testing /action/goto ===")
    
    url = f"{BASE_URL}/action/goto"
    payload = {
        "sessionId": session_id,
        "url": "https://playwright.dev"
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    try:
        response = requests.post(url, json=payload)
        data = print_response(response, "goto")
        return response.status_code == 200 and data.get("status") == "success"
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def test_click(session_id: str) -> bool:
    """Test the click endpoint with a string locator"""
    print("\n\n=== Testing /action/click with string locator ===")
    
    url = f"{BASE_URL}/action/click"
    payload = {
        "sessionId": session_id,
        "locator": "text=Get Started",
        "force": False,
        "button": "left"
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    try:
        response = requests.post(url, json=payload)
        data = print_response(response, "click_string")
        return response.status_code == 200 and data.get("status") == "success"
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def test_click_structured(session_id: str) -> bool:
    """Test the click endpoint with a structured locator"""
    print("\n\n=== Testing /action/click with structured locator ===")
    
    url = f"{BASE_URL}/action/click"
    payload = {
        "sessionId": session_id,
        "locator": {
            "role": "link",
            "name": "Docs"
        },
        "force": False
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    try:
        response = requests.post(url, json=payload)
        data = print_response(response, "click_structured")
        return response.status_code == 200 and data.get("status") == "success"
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def test_hover(session_id: str) -> bool:
    """Test the hover endpoint"""
    print("\n\n=== Testing /action/hover ===")
    
    url = f"{BASE_URL}/action/hover"
    payload = {
        "sessionId": session_id,
        "locator": "text=API",
        "force": False
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    try:
        response = requests.post(url, json=payload)
        data = print_response(response, "hover")
        return response.status_code == 200 and data.get("status") == "success"
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def test_fill(session_id: str) -> bool:
    """Test the fill endpoint"""
    print("\n\n=== Testing /action/fill ===")
    
    # First navigate to a page with a search box
    goto_url = f"{BASE_URL}/action/goto"
    goto_payload = {
        "sessionId": session_id,
        "url": "https://www.google.com"
    }
    try:
        goto_response = requests.post(goto_url, json=goto_payload)
        print_response(goto_response, "goto_google")
        time.sleep(2)  # Wait for navigation to complete
        
        # Now test the fill action
        url = f"{BASE_URL}/action/fill"
        payload = {
            "sessionId": session_id,
            "locator": "textarea[name='q']",
            "value": "Playwright testing",
            "force": False
        }
        
        print(f"Request: {json.dumps(payload, indent=2)}")
        response = requests.post(url, json=payload)
        data = print_response(response, "fill")
        return response.status_code == 200 and data.get("status") == "success"
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def test_type(session_id: str) -> bool:
    """Test the type endpoint"""
    print("\n\n=== Testing /action/type ===")
    
    try:
        # Clear the search box first
        fill_url = f"{BASE_URL}/action/fill"
        fill_payload = {
            "sessionId": session_id,
            "locator": "textarea[name='q']",
            "value": "",
            "force": False
        }
        fill_response = requests.post(fill_url, json=fill_payload)
        print_response(fill_response, "clear_field")
        time.sleep(1)  # Wait for action to complete
        
        # Now test the type action
        url = f"{BASE_URL}/action/type"
        payload = {
            "sessionId": session_id,
            "locator": "textarea[name='q']",
            "text": "Playwright API",
            "delay": 100
        }
        
        print(f"Request: {json.dumps(payload, indent=2)}")
        response = requests.post(url, json=payload)
        data = print_response(response, "type")
        return response.status_code == 200 and data.get("status") == "success"
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def test_press(session_id: str) -> bool:
    """Test the press endpoint"""
    print("\n\n=== Testing /action/press ===")
    
    url = f"{BASE_URL}/action/press"
    payload = {
        "sessionId": session_id,
        "locator": "textarea[name='q']",
        "key": "Enter"
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    try:
        response = requests.post(url, json=payload)
        data = print_response(response, "press")
        return response.status_code == 200 and data.get("status") == "success"
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def test_close_session(session_id: str) -> bool:
    """Test the close_session endpoint"""
    print("\n\n=== Testing /session/close ===")
    
    url = f"{BASE_URL}/session/close"
    payload = {
        "sessionId": session_id
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    try:
        response = requests.post(url, json=payload)
        data = print_response(response, "session_close")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def run_all_tests():
    """Run all API tests"""
    print("🎭 Starting Playwright Action API Tests 🎭")
    
    # Start a session
    session_id = test_start_session()
    if not session_id:
        print("❌ Failed to start a session. Aborting tests.")
        return
    
    print(f"✅ Session started with ID: {session_id}")
    
    try:
        # Wait for the browser to fully initialize
        time.sleep(3)
        
        # Run all action tests
        goto_success = test_goto(session_id)
        time.sleep(3)
        
        if goto_success:
            test_click(session_id)
            time.sleep(3)
            
            test_click_structured(session_id)
            time.sleep(3)
            
            test_hover(session_id)
            time.sleep(3)
        
        # Reset with a new page for form testing
        test_fill(session_id)
        time.sleep(3)
        
        test_type(session_id)
        time.sleep(3)
        
        test_press(session_id)
        time.sleep(3)
    finally:
        # Always try to close the session
        test_close_session(session_id)
    
    print("🎉 All tests completed!")
    print(f"Screenshots saved in the '{SCREENSHOTS_DIR}' directory")


if __name__ == "__main__":
    run_all_tests() 