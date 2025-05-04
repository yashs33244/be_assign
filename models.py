from pydantic import BaseModel, Field, field_validator
from typing import Dict, Optional, Union, List, Any


class StartSessionRequest(BaseModel):
    browser: str = Field(..., description="Browser type ('chromium', 'firefox', 'webkit')")
    headless: bool = Field(True, description="Whether to run browser in headless mode")
    viewport_width: Optional[int] = Field(None, description="Viewport width in pixels")
    viewport_height: Optional[int] = Field(None, description="Viewport height in pixels")
    device_scale_factor: Optional[float] = Field(None, description="Device scale factor")
    
    @field_validator('browser')
    @classmethod
    def validate_browser(cls, v):
        if v.lower() not in ['chromium', 'firefox', 'webkit']:
            raise ValueError(f'Browser type must be one of: chromium, firefox, webkit. Got: {v}')
        return v.lower()


class StartSessionResponse(BaseModel):
    sessionId: str


class CloseSessionRequest(BaseModel):
    sessionId: str


class StructuredLocator(BaseModel):
    role: str
    name: str


class ActionRequest(BaseModel):
    sessionId: str
    locator: Union[str, StructuredLocator]


class GotoRequest(BaseModel):
    sessionId: str
    url: str


class ClickRequest(ActionRequest):
    force: Optional[bool] = Field(False, description="Force click the element")
    delay: Optional[int] = Field(None, description="Delay before click in milliseconds")
    button: Optional[str] = Field('left', description="Mouse button: 'left', 'right', 'middle'")
    
    @field_validator('button')
    @classmethod
    def validate_button(cls, v):
        if v not in ['left', 'right', 'middle']:
            raise ValueError(f'Button must be one of: left, right, middle. Got: {v}')
        return v


class HoverRequest(ActionRequest):
    force: Optional[bool] = Field(False, description="Force hover")
    position: Optional[Dict[str, int]] = Field(None, description="Hover position, e.g. {'x': 10, 'y': 20}")


class FillRequest(ActionRequest):
    value: str = Field(..., description="Text to fill in the input")
    force: Optional[bool] = Field(False, description="Force fill")


class TypeRequest(ActionRequest):
    text: str = Field(..., description="Text to type")
    delay: Optional[int] = Field(None, description="Delay between key presses in milliseconds")


class PressRequest(ActionRequest):
    key: str = Field(..., description="Key to press, e.g. 'Enter', 'Tab', 'a', etc.")


class CheckRequest(ActionRequest):
    force: Optional[bool] = Field(False, description="Force check")


class UncheckRequest(ActionRequest):
    force: Optional[bool] = Field(False, description="Force uncheck")


class SelectOptionRequest(ActionRequest):
    values: List[Union[str, Dict[str, str]]] = Field(..., description="Values to select")


class SuccessResponse(BaseModel):
    status: str = "success"
    screenshot: str = Field(..., description="Base64-encoded PNG screenshot")


class ErrorResponse(BaseModel):
    status: str = "error"
    error: str
    screenshot: Optional[str] = Field(None, description="Base64-encoded PNG screenshot") 