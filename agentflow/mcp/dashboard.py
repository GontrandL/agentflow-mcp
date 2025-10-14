# SECTION 1: Implementing the DashboardManager Class

"""
Here's the complete implementation of the `DashboardManager` class with all the specified requirements:
"""

import threading
from typing import Dict, Any, Optional, List

class DashboardManager:
    def __init__(self):
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def add_task(self, task_id: str, task_name: str, task_details: Dict[str, Any]) -> None:
        """Add a new task to the dashboard."""
        if not isinstance(task_id, str) or not task_id:
            raise ValueError("task_id must be a non-empty string")
        if not isinstance(task_name, str) or not task_name:
            raise ValueError("task_name must be a non-empty string")
        if not isinstance(task_details, dict):
            raise ValueError("task_details must be a dictionary")

        with self._lock:
            if task_id in self._tasks:
                raise ValueError(f"Task with id '{task_id}' already exists")
            
            self._tasks[task_id] = {
                'name': task_name,
                'details': task_details,
                'status': 'pending',
                'progress': 0.0,
                'logs': []
            }

    def update_task(self, task_id: str, status: Optional[str] = None, 
                    progress: Optional[float] = None, details: Optional[Dict[str, Any]] = None) -> None:
        """Update an existing task's properties."""
        valid_statuses = {"pending", "in_progress", "completed"}
        
        with self._lock:
            if task_id not in self._tasks:
                raise KeyError(f"Task with id '{task_id}' does not exist")

            task = self._tasks[task_id]
            
            if status is not None:
                if status not in valid_statuses:
                    raise ValueError(f"status must be one of {valid_statuses}")
                task['status'] = status
            
            if progress is not None:
                if not isinstance(progress, (int, float)) or not (0 <= progress <= 1):
                    raise ValueError("progress must be a float between 0 and 1")
                task['progress'] = float(progress)
            
            if details is not None:
                if not isinstance(details, dict):
                    raise ValueError("details must be a dictionary")
                task['details'] = details

    def log(self, task_id: str, message: str) -> None:
        """Add a log message to a task."""
        if not isinstance(message, str) or not message:
            raise ValueError("message must be a non-empty string")

        with self._lock:
            if task_id not in self._tasks:
                raise KeyError(f"Task with id '{task_id}' does not exist")
            
            self._tasks[task_id]['logs'].append(message)

    def get_status(self, task_id: str) -> Dict[str, Any]:
        """Get the status, progress, and logs of a task."""
        with self._lock:
            if task_id not in self._tasks:
                raise KeyError(f"Task with id '{task_id}' does not exist")
            
            task = self._tasks[task_id]
            return {
                'name': task['name'],
                'status': task['status'],
                'progress': task['progress'],
                'details': task['details'],
                'logs': task['logs'].copy()  # Return a copy to prevent external modification
            }

"""
Key features of this implementation:

1. **Thread Safety**: Uses a threading.Lock to ensure all operations are atomic and thread-safe.
2. **Input Validation**: Thorough validation for all input parameters with appropriate error messages.
3. **Error Handling**: Raises ValueError for invalid inputs and KeyError for non-existent tasks.
4. **Type Hints**: Uses Python type hints for better code clarity and IDE support.
5. **Data Structure**: Maintains tasks in a dictionary with a well-defined structure.
6. **Immutable Returns**: Returns a copy of logs to prevent external modification of internal state.
7. **PEP 8 Compliance**: Follows Python style guidelines for naming and formatting.

The class handles all specified edge cases and provides the required functionality in a thread-safe manner. The implementation is ready for direct use as shown in the example usage.
"""

# SECTION 2: Creating the FastAPI App

"""
Next, we'll create a FastAPI app with endpoints for serving HTML and streaming Server-Sent Events (SSE) updates.
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from datetime import datetime
import time
import asyncio
import logging

app = FastAPI()

# HTML endpoint
@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SSE Events Demo</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            #events {
                border: 1px solid #ccc;
                padding: 20px;
                border-radius: 5px;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div id="events">Waiting for events...</div>
        <script>
            const eventSource = new EventSource('/events');
            eventSource.onmessage = function(e) {
                const data = JSON.parse(e.data);
                document.getElementById('events').innerText = data.timestamp;
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# SSE endpoint
@app.get("/events")
async def stream_events(request: Request):
    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    logging.info("Client disconnected, stopping SSE stream")
                    break
                
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                data = {"timestamp": timestamp}
                yield f"data: {data}\\n\\n"
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logging.info("SSE stream cancelled")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"}
    )

"""
This FastAPI app has two endpoints:
1. `/` - Serves a basic HTML page that listens for SSE events
2. `/events` - Streams timestamp updates every second
"""

# SECTION 3: Generating Embedded HTML with Dark Theme

"""
We'll now generate an HTML snippet with a GitHub-style dark theme, including progress bars and live logs.
"""

html_snippet = """
<div class="github-dark-container">
  <div class="progress-container">
    <div class="progress-bar determinate" style="width: 75%">
      <span class="progress-label">Processing... 75%</span>
    </div>
    <div class="progress-bar indeterminate">
      <span class="progress-label">Initializing...</span>
    </div>
  </div>
  <div class="logs">
    <div class="log info">[14:30:22] INFO: Task started</div>
    <div class="log warn">[14:30:23] WARN: High CPU usage</div>
    <div class="log error">[14:30:24] ERROR: Failed to load module</div>
    <div class="log info">[14:30:25] INFO: Retrying operation</div>
    <div class="log info">[14:30:26] INFO: Connection established</div>
    <div class="log warn">[14:30:27] WARN: High memory consumption</div>
    <div class="log info">[14:30:28] INFO: Processing data</div>
    <div class="log placeholder">No new logs yet...</div>
  </div>
</div>

<style>
  .github-dark-container {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background-color: #0d1117;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 16px;
    max-width: 600px;
    margin: 0 auto;
    box-sizing: border-box;
  }

  .progress-container {
    margin-bottom: 16px;
  }

  .progress-bar {
    height: 20px;
    border-radius: 3px;
    margin-bottom: 8px;
    position: relative;
    overflow: hidden;
    background-color: #161b22;
    transition: width 0.3s ease;
  }

  .progress-bar.determinate {
    background-color: #238636;
  }

  .progress-bar.indeterminate {
    background: linear-gradient(90deg, #161b22 0%, #238636 50%, #161b22 100%);
    background-size: 200% 100%;
    animation: indeterminate 2s linear infinite;
  }

  .progress-bar.error {
    background-color: #da3633;
  }

  .progress-label {
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    bottom: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    color: white;
    text-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
  }

  .logs {
    max-height: 200px;
    overflow-y: auto;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px;
    background-color: #161b22;
    font-family: monospace;
    font-size: 13px;
    line-height: 1.5;
  }

  .log {
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .log:last-child {
    margin-bottom: 0;
  }

  .log.info {
    color: #c9d1d9;
  }

  .log.warn {
    color: #d29922;
  }

  .log.error {
    color: #f85149;
  }

  .log.placeholder {
    color: #484f58;
    font-style: italic;
  }

  @keyframes indeterminate {
    0% {
      background-position: 200% 0;
    }
    100% {
      background-position: -200% 0;
    }
  }

  /* Scrollbar styling */
  .logs::-webkit-scrollbar {
    width: 8px;
  }

  .logs::-webkit-scrollbar-track {
    background: #161b22;
  }

  .logs::-webkit-scrollbar-thumb {
    background: #30363d;
    border-radius: 4px;
  }

  .logs::-webkit-scrollbar-thumb:hover {
    background: #484f58;
  }
</style>

<script>
  // This would be replaced with actual log updating logic in a real implementation
  // This is just a demo of auto-scrolling behavior
  document.addEventListener('DOMContentLoaded', function() {
    const logsContainer = document.querySelector('.logs');
    logsContainer.scrollTop = logsContainer.scrollHeight;
    
    // Demo: Add a new log every 3 seconds
    setInterval(() => {
      const now = new Date();
      const timeStr = `[${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}]`;
      
      const placeholder = logsContainer.querySelector('.placeholder');
      if (placeholder) {
        logsContainer.removeChild(placeholder);
      }
      
      const logTypes = ['info', 'warn', 'error'];
      const randomType = logTypes[Math.floor(Math.random() * logTypes.length)];
      const messages = [
        'Processing data chunk',
        'Validating inputs',
        'Writing to database',
        'Network latency detected',
        'Authentication required',
        'Disk space running low',
        'Task completed successfully'
      ];
      const randomMessage = messages[Math.floor(Math.random() * messages.length)];
      
      const logEntry = document.createElement('div');
      logEntry.className = `log ${randomType}`;
      logEntry.textContent = `${timeStr} ${randomType.toUpperCase()}: ${randomMessage}`;
      
      logsContainer.appendChild(logEntry);
      logsContainer.scrollTop = logsContainer.scrollHeight;
    }, 3000);
  });
</script>
"""

"""
This HTML snippet includes:
- GitHub-style dark theme
- Animated determinate and indeterminate progress bars
- Live logs with timestamped entries
- Auto-scrolling functionality
- Demo JavaScript for log updates
"""

# SECTION 4: Integrating DashboardManager with FastAPI App

"""
Finally, we'll integrate the DashboardManager with our FastAPI app and embed our HTML content.
"""

from fastapi import FastAPI, HTTPException
from dashboard_manager import DashboardManager
from fastapi.responses import HTMLResponse
import os

# Create a FastAPI app instance
app = FastAPI()

# Initialize a DashboardManager instance
dashboard = DashboardManager()

# Define a function to load HTML template
def load_html_template(template_path: str) -> str:
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template file not found: {template_path}")
    with open(template_path, 'r') as file:
        return file.read()

# Define a FastAPI route `/dashboard`
@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    try:
        # Get dashboard data from DashboardManager
        data = dashboard.get_output()
        if not data:
            raise HTTPException(status_code=404, detail="Dashboard data not found")
        
        # Load HTML template
        template_path = "templates/dashboard_template.html"
        template = load_html_template(template_path)
        
        # Embed DashboardManager's output into the HTML template
        html_content = template.replace("{{ title }}", "Dashboard").replace("{{ content }}", data)
        
        return HTMLResponse(content=html_content, status_code=200)
    
    except HTTPException as e:
        raise e
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Validate the integration by checking the FastAPI app runs without errors
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# HTML Template Example (templates/dashboard_template.html):
"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 20px;
        }
        .container {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ title }}</h1>
        <div class="dashboard-content">
            {{ content }}
        </div>
    </div>
</body>
</html>
"""

"""
Key Integration Steps:
1. Import necessary modules and initialize DashboardManager
2. Create a function to load HTML templates
3. Define a `/dashboard` endpoint that:
   - Retrieves data from DashboardManager
   - Loads HTML template
   - Embeds dashboard content
   - Handles various error cases
4. Run the FastAPI app with uvicorn
"""

# SECTION 5: Writing Unit Tests

"""
Finally, we'll write unit tests for both the DashboardManager class and FastAPI endpoints.
"""

# test_dashboard_manager.py
"""
Unit tests for the DashboardManager class
"""

import pytest
from your_module import DashboardManager  # Replace with actual import

@pytest.fixture
def dashboard_manager():
    return DashboardManager()

def test_add_task(dashboard_manager):
    # Test adding a task
    dashboard_manager.add_task("task1", "Test Task", {"details": "test"})
    task_status = dashboard_manager.get_status("task1")
    assert task_status['name'] == "Test Task"
    assert task_status['status'] == "pending"

def test_update_task(dashboard_manager):
    # Test updating a task
    dashboard_manager.add_task("task1", "Test Task", {})
    dashboard_manager.update_task("task1", status="in_progress", progress=0.5)
    task_status = dashboard_manager.get_status("task1")
    assert task_status['status'] == "in_progress"
    assert task_status['progress'] == 0.5

# test_endpoints.py
"""
Unit tests for FastAPI endpoints
"""

from fastapi.testclient import TestClient
from your_app import app  # Replace with actual import

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_events_endpoint():
    response = client.get("/events")
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

"""
These tests provide basic coverage for our implementation. You should expand them to handle more edge cases and scenarios specific to your application.
"""

"""
CONCLUSION:
This complete implementation includes:
- A thread-safe DashboardManager class
- FastAPI app with SSE support
- GitHub-style dark theme HTML
- Integration between components
- Basic unit tests

You can now extend this system with additional features and improve the test coverage as needed.
"""