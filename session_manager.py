import asyncio
import uuid
import base64
from typing import Dict, Optional, Any, Tuple
from playwright.async_api import async_playwright, Playwright, Browser, BrowserContext, Page

# Dictionary to store active sessions
# Format: {session_id: {playwright, browser, context, page}}
sessions: Dict[str, Dict[str, Any]] = {}


async def start_session(browser_type: str, headless: bool = True, **kwargs) -> str:
    """
    Start a new browser session.
    
    Args:
        browser_type: Type of browser ('chromium', 'firefox', or 'webkit')
        headless: Whether to run browser in headless mode
        kwargs: Additional browser configuration parameters
    
    Returns:
        session_id: Unique identifier for the session
    """
    session_id = str(uuid.uuid4())
    
    # Initialize playwright
    playwright = await async_playwright().start()
    
    # Extract viewport settings
    viewport = kwargs.pop('viewport', None)
    
    # Launch browser with only the headless option
    try:
        if browser_type.lower() == "chromium":
            browser = await playwright.chromium.launch(headless=headless)
        elif browser_type.lower() == "firefox":
            browser = await playwright.firefox.launch(headless=headless)
        elif browser_type.lower() == "webkit":
            browser = await playwright.webkit.launch(headless=headless)
        else:
            await playwright.stop()
            raise ValueError(f"Unsupported browser type: {browser_type}")
        
        # Create a new browser context with viewport if specified
        context_options = {}
        if viewport:
            context_options['viewport'] = viewport
        
        context = await browser.new_context(**context_options)
        page = await context.new_page()
        
        # Store session information
        sessions[session_id] = {
            "playwright": playwright,
            "browser": browser,
            "context": context,
            "page": page
        }
        
        return session_id
    except Exception as e:
        # Make sure to clean up if there's an error
        await playwright.stop()
        raise Exception(f"Failed to start session: {str(e)}")


async def close_session(session_id: str) -> bool:
    """
    Close a browser session.
    
    Args:
        session_id: ID of the session to close
        
    Returns:
        True if session was closed successfully, False otherwise
    """
    if session_id not in sessions:
        return False
    
    session = sessions[session_id]
    
    # Close page, context, browser, and stop playwright
    await session["page"].close()
    await session["context"].close()
    await session["browser"].close()
    await session["playwright"].stop()
    
    # Remove session from dictionary
    del sessions[session_id]
    
    return True


async def execute_action(session_id: str, action: str, locator: Any = None, **kwargs) -> Tuple[bool, Optional[bytes]]:
    """
    Execute a Playwright action on a browser session.
    
    Args:
        session_id: ID of the session to use
        action: Name of the Playwright action to execute
        locator: Element locator (string or structured format), optional for page-level actions
        kwargs: Additional parameters for the action
        
    Returns:
        Tuple containing (success, screenshot)
    """
    if session_id not in sessions:
        raise ValueError(f"Session not found: {session_id}")
    
    session = sessions[session_id]
    page = session["page"]
    
    # Handle page-level actions (like goto) that don't require a locator
    if action == "goto":
        try:
            await page.goto(kwargs.get("url", ""), **{k: v for k, v in kwargs.items() if k != "url"})
            screenshot = await page.screenshot()
            return True, screenshot
        except Exception as e:
            return False, await page.screenshot()
    
    # For all other actions that require a locator
    if locator is None:
        raise ValueError(f"Locator is required for action: {action}")
    
    # Handle string vs structured locator format
    element = None
    try:
        if isinstance(locator, str):
            # String locator (CSS, XPath, etc.)
            element = page.locator(locator)
        elif isinstance(locator, dict) and "role" in locator and "name" in locator:
            # Try different locating strategies
            try:
                # First try get_by_role
                element = page.get_by_role(locator["role"], name=locator["name"])
            except Exception:
                # Try by using text selector
                element = page.locator(f'text={locator["name"]}')
                
                # If that fails, try by aria-label
                if not await element.count():
                    element = page.locator(f'[aria-label="{locator["name"]}"]')
                    
                # If all fails, try a more generic approach
                if not await element.count():
                    element = page.locator(f'{locator["role"]}:has-text("{locator["name"]}")')
        else:
            raise ValueError(f"Invalid locator format: {locator}")
    except Exception as e:
        # In case of any locator error, return screenshot with error
        raise ValueError(f"Failed to locate element: {str(e)}")
    
    # Verify that the element exists before taking action
    if await element.count() == 0:
        screenshot = await page.screenshot()
        return False, screenshot
    
    # Execute the requested action
    try:
        if action == "click":
            await element.click(**kwargs)
        elif action == "fill":
            await element.fill(kwargs.get("value", ""), **{k: v for k, v in kwargs.items() if k != "value"})
        elif action == "type":
            await element.type(kwargs.get("text", ""), **{k: v for k, v in kwargs.items() if k != "text"})
        elif action == "hover":
            # Wait for element to be visible before hovering
            await element.wait_for(state="visible", timeout=5000)
            await element.hover(**kwargs)
        elif action == "focus":
            await element.focus(**kwargs)
        elif action == "press":
            await element.press(kwargs.get("key", ""), **{k: v for k, v in kwargs.items() if k != "key"})
        elif action == "check":
            await element.check(**kwargs)
        elif action == "uncheck":
            await element.uncheck(**kwargs)
        elif action == "select_option":
            await element.select_option(kwargs.get("values", []), **{k: v for k, v in kwargs.items() if k != "values"})
        elif action == "upload_file":
            await element.set_input_files(kwargs.get("files", []), **{k: v for k, v in kwargs.items() if k != "files"})
        elif action == "dblclick":
            await element.dblclick(**kwargs)
        else:
            raise ValueError(f"Unsupported action: {action}")
        
        # Capture screenshot
        screenshot = await page.screenshot()
        return True, screenshot
    
    except Exception as e:
        # Return error with screenshot
        return False, await page.screenshot()


def get_active_sessions() -> Dict[str, str]:
    """
    Get information about active sessions.
    
    Returns:
        Dictionary of session_id: browser_type
    """
    result = {}
    for session_id, session in sessions.items():
        result[session_id] = session["browser"].browser_type.name
    return result 