from fastapi import FastAPI, HTTPException, status
import uvicorn
import base64
from typing import Dict, List

# Import session manager
import session_manager
from models import (
    StartSessionRequest, StartSessionResponse, CloseSessionRequest,
    GotoRequest, ClickRequest, HoverRequest, FillRequest, TypeRequest,
    PressRequest, CheckRequest, UncheckRequest, SelectOptionRequest,
    SuccessResponse, ErrorResponse, StructuredLocator
)

app = FastAPI(title="Playwright Action API",
              description="REST API for Playwright browser automation actions")


@app.get("/")
async def root():
    """Root endpoint with basic information about the API."""
    return {
        "message": "Playwright Action API",
        "docs": "/docs",
        "endpoints": [
            {"path": "/session/start", "method": "POST", "description": "Start a new browser session"},
            {"path": "/session/close", "method": "POST", "description": "Close an active browser session"},
            {"path": "/action/goto", "method": "POST", "description": "Navigate to a URL"},
            {"path": "/action/click", "method": "POST", "description": "Click on an element"},
            {"path": "/action/hover", "method": "POST", "description": "Hover over an element"},
            {"path": "/action/fill", "method": "POST", "description": "Fill a form field"},
            {"path": "/action/type", "method": "POST", "description": "Type text"},
            {"path": "/action/press", "method": "POST", "description": "Press a key"},
            {"path": "/action/check", "method": "POST", "description": "Check a checkbox"},
            {"path": "/action/uncheck", "method": "POST", "description": "Uncheck a checkbox"},
            {"path": "/action/select_option", "method": "POST", "description": "Select an option"}
        ]
    }


@app.post("/session/start", response_model=StartSessionResponse, tags=["Session Management"])
async def start_session(request: StartSessionRequest):
    """
    Start a new browser session.
    
    Creates a new browser instance with the specified configuration.
    """
    try:
        # Prepare viewport settings if provided
        viewport = None
        if request.viewport_width is not None and request.viewport_height is not None:
            viewport = {
                "width": request.viewport_width,
                "height": request.viewport_height
            }
            if request.device_scale_factor is not None:
                viewport["device_scale_factor"] = request.device_scale_factor
        
        # Start the session        
        session_id = await session_manager.start_session(
            browser_type=request.browser,
            headless=request.headless,
            viewport=viewport
        )
        
        return StartSessionResponse(sessionId=session_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Failed to start session: {str(e)}")


@app.post("/session/close", tags=["Session Management"])
async def close_session(request: CloseSessionRequest):
    """
    Close an active browser session.
    """
    try:
        success = await session_manager.close_session(request.sessionId)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f"Session not found: {request.sessionId}")
        return {"status": "success", "message": f"Session {request.sessionId} closed successfully"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Failed to close session: {str(e)}")


@app.post("/action/goto", response_model=SuccessResponse, responses={500: {"model": ErrorResponse}}, tags=["Actions"])
async def goto(request: GotoRequest):
    """
    Navigate to a URL in the specified session.
    """
    try:
        success, screenshot = await session_manager.execute_action(
            session_id=request.sessionId,
            action="goto",
            locator=None,
            url=request.url
        )
        
        if success:
            return SuccessResponse(screenshot=base64.b64encode(screenshot).decode())
        else:
            return ErrorResponse(status="error", error=f"Failed to navigate to {request.url}", 
                                 screenshot=base64.b64encode(screenshot).decode())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Error executing goto action: {str(e)}")


@app.post("/action/click", response_model=SuccessResponse, responses={500: {"model": ErrorResponse}}, tags=["Actions"])
async def click(request: ClickRequest):
    """
    Click on an element identified by the locator.
    """
    try:
        kwargs = {
            "force": request.force,
            "button": request.button
        }
        if request.delay is not None:
            kwargs["delay"] = request.delay
        
        # Convert Pydantic model to dict if it's a structured locator
        locator = request.locator
        if not isinstance(locator, str) and not isinstance(locator, dict):
            # Convert to a dict explicitly if it's a pydantic model
            locator = {"role": locator.role, "name": locator.name}
            
        success, screenshot = await session_manager.execute_action(
            session_id=request.sessionId,
            action="click",
            locator=locator,
            **kwargs
        )
        
        if success:
            return SuccessResponse(screenshot=base64.b64encode(screenshot).decode())
        else:
            return ErrorResponse(status="error", error=f"Failed to click element", 
                                 screenshot=base64.b64encode(screenshot).decode())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Error executing click action: {str(e)}")


@app.post("/action/hover", response_model=SuccessResponse, responses={500: {"model": ErrorResponse}}, tags=["Actions"])
async def hover(request: HoverRequest):
    """
    Hover over an element identified by the locator.
    """
    try:
        kwargs = {"force": request.force}
        if request.position is not None:
            kwargs["position"] = request.position
        
        # Convert Pydantic model to dict if it's a structured locator
        locator = request.locator
        if not isinstance(locator, str) and not isinstance(locator, dict):
            # Convert to a dict explicitly if it's a pydantic model
            locator = {"role": locator.role, "name": locator.name}
            
        success, screenshot = await session_manager.execute_action(
            session_id=request.sessionId,
            action="hover",
            locator=locator,
            **kwargs
        )
        
        if success:
            return SuccessResponse(screenshot=base64.b64encode(screenshot).decode())
        else:
            return ErrorResponse(status="error", error=f"Failed to hover over element", 
                                 screenshot=base64.b64encode(screenshot).decode())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Error executing hover action: {str(e)}")


@app.post("/action/fill", response_model=SuccessResponse, responses={500: {"model": ErrorResponse}}, tags=["Actions"])
async def fill(request: FillRequest):
    """
    Fill a form field with the provided value.
    """
    try:
        # Convert Pydantic model to dict if it's a structured locator
        locator = request.locator
        if not isinstance(locator, str) and not isinstance(locator, dict):
            # Convert to a dict explicitly if it's a pydantic model
            locator = {"role": locator.role, "name": locator.name}
            
        success, screenshot = await session_manager.execute_action(
            session_id=request.sessionId,
            action="fill",
            locator=locator,
            value=request.value,
            force=request.force
        )
        
        if success:
            return SuccessResponse(screenshot=base64.b64encode(screenshot).decode())
        else:
            return ErrorResponse(status="error", error=f"Failed to fill element", 
                                 screenshot=base64.b64encode(screenshot).decode())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Error executing fill action: {str(e)}")


@app.post("/action/type", response_model=SuccessResponse, responses={500: {"model": ErrorResponse}}, tags=["Actions"])
async def type_text(request: TypeRequest):
    """
    Type text into an element identified by the locator.
    """
    try:
        kwargs = {}
        if request.delay is not None:
            kwargs["delay"] = request.delay
        
        # Convert Pydantic model to dict if it's a structured locator
        locator = request.locator
        if not isinstance(locator, str) and not isinstance(locator, dict):
            # Convert to a dict explicitly if it's a pydantic model
            locator = {"role": locator.role, "name": locator.name}
            
        success, screenshot = await session_manager.execute_action(
            session_id=request.sessionId,
            action="type",
            locator=locator,
            text=request.text,
            **kwargs
        )
        
        if success:
            return SuccessResponse(screenshot=base64.b64encode(screenshot).decode())
        else:
            return ErrorResponse(status="error", error=f"Failed to type text", 
                                 screenshot=base64.b64encode(screenshot).decode())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Error executing type action: {str(e)}")


@app.post("/action/press", response_model=SuccessResponse, responses={500: {"model": ErrorResponse}}, tags=["Actions"])
async def press(request: PressRequest):
    """
    Press a key on an element identified by the locator.
    """
    try:
        # Convert Pydantic model to dict if it's a structured locator
        locator = request.locator
        if not isinstance(locator, str) and not isinstance(locator, dict):
            # Convert to a dict explicitly if it's a pydantic model
            locator = {"role": locator.role, "name": locator.name}
            
        success, screenshot = await session_manager.execute_action(
            session_id=request.sessionId,
            action="press",
            locator=locator,
            key=request.key
        )
        
        if success:
            return SuccessResponse(screenshot=base64.b64encode(screenshot).decode())
        else:
            return ErrorResponse(status="error", error=f"Failed to press key", 
                                 screenshot=base64.b64encode(screenshot).decode())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Error executing press action: {str(e)}")


@app.post("/action/check", response_model=SuccessResponse, responses={500: {"model": ErrorResponse}}, tags=["Actions"])
async def check(request: CheckRequest):
    """
    Check a checkbox identified by the locator.
    """
    try:
        # Convert Pydantic model to dict if it's a structured locator
        locator = request.locator
        if not isinstance(locator, str) and not isinstance(locator, dict):
            # Convert to a dict explicitly if it's a pydantic model
            locator = {"role": locator.role, "name": locator.name}
            
        success, screenshot = await session_manager.execute_action(
            session_id=request.sessionId,
            action="check",
            locator=locator,
            force=request.force
        )
        
        if success:
            return SuccessResponse(screenshot=base64.b64encode(screenshot).decode())
        else:
            return ErrorResponse(status="error", error=f"Failed to check element", 
                                 screenshot=base64.b64encode(screenshot).decode())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Error executing check action: {str(e)}")


@app.post("/action/uncheck", response_model=SuccessResponse, responses={500: {"model": ErrorResponse}}, tags=["Actions"])
async def uncheck(request: UncheckRequest):
    """
    Uncheck a checkbox identified by the locator.
    """
    try:
        # Convert Pydantic model to dict if it's a structured locator
        locator = request.locator
        if not isinstance(locator, str) and not isinstance(locator, dict):
            # Convert to a dict explicitly if it's a pydantic model
            locator = {"role": locator.role, "name": locator.name}
            
        success, screenshot = await session_manager.execute_action(
            session_id=request.sessionId,
            action="uncheck",
            locator=locator,
            force=request.force
        )
        
        if success:
            return SuccessResponse(screenshot=base64.b64encode(screenshot).decode())
        else:
            return ErrorResponse(status="error", error=f"Failed to uncheck element", 
                                 screenshot=base64.b64encode(screenshot).decode())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Error executing uncheck action: {str(e)}")


@app.post("/action/select_option", response_model=SuccessResponse, responses={500: {"model": ErrorResponse}}, tags=["Actions"])
async def select_option(request: SelectOptionRequest):
    """
    Select options in a select element identified by the locator.
    """
    try:
        # Convert Pydantic model to dict if it's a structured locator
        locator = request.locator
        if not isinstance(locator, str) and not isinstance(locator, dict):
            # Convert to a dict explicitly if it's a pydantic model
            locator = {"role": locator.role, "name": locator.name}
            
        success, screenshot = await session_manager.execute_action(
            session_id=request.sessionId,
            action="select_option",
            locator=locator,
            values=request.values
        )
        
        if success:
            return SuccessResponse(screenshot=base64.b64encode(screenshot).decode())
        else:
            return ErrorResponse(status="error", error=f"Failed to select option", 
                                 screenshot=base64.b64encode(screenshot).decode())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Error executing select_option action: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 