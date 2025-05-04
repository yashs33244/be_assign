# Playwright Action API

A REST API service that exposes Playwright browser automation actions as HTTP endpoints, supporting multiple browser sessions and returning screenshots after each action.

## Features

- Session management: Start and close browser sessions
- Multiple browser support: Chromium, Firefox, and WebKit
- Multiple concurrent sessions
- Base64-encoded screenshots after each action
- Support for both string selectors and structured locators

## API Endpoints

### Session Management

- `POST /session/start`: Start a new browser session
- `POST /session/close`: Close an active session

### Actions

- `POST /action/goto`: Navigate to a URL
- `POST /action/click`: Click on an element
- `POST /action/hover`: Hover over an element
- `POST /action/fill`: Fill a form field
- `POST /action/type`: Type text
- `POST /action/press`: Press a key
- `POST /action/check`: Check a checkbox
- `POST /action/uncheck`: Uncheck a checkbox
- `POST /action/select_option`: Select an option

## Setup and Installation

### Prerequisites

- Docker and Docker Compose (recommended)
- Python 3.9+ (for local installation)

### Using Docker (Recommended)

1. Clone this repository
2. Run with Docker Compose:

```bash
docker-compose up -d
```

3. Access the API at http://localhost:8000
4. Access the API documentation at http://localhost:8000/docs

### Local Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:

```bash
playwright install
```

4. Run the application:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## Usage Examples

### Start a new session

```bash
curl -X POST http://localhost:8000/session/start \
  -H "Content-Type: application/json" \
  -d '{"browser": "chromium", "headless": true}'
```

Response:

```json
{
  "sessionId": "12345678-1234-5678-1234-567812345678"
}
```

### Navigate to a URL

```bash
curl -X POST http://localhost:8000/action/goto \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "12345678-1234-5678-1234-567812345678", "url": "https://example.com"}'
```

Response:

```json
{
  "status": "success",
  "screenshot": "base64_png_data"
}
```

### Click an element using a string selector

```bash
curl -X POST http://localhost:8000/action/click \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "12345678-1234-5678-1234-567812345678", "locator": "#submit-button"}'
```

### Click an element using a structured locator

```bash
curl -X POST http://localhost:8000/action/click \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "12345678-1234-5678-1234-567812345678", "locator": {"role": "button", "name": "Submit"}}'
```

### Close a session

```bash
curl -X POST http://localhost:8000/session/close \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "12345678-1234-5678-1234-567812345678"}'
```

## Error Handling

The API returns proper error responses when something goes wrong:

```json
{
  "status": "error",
  "error": "Element not found: #non-existent-element",
  "screenshot": "base64_png_data"
}
```
