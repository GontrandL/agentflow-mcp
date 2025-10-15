# SmartOrchestrator Metrics Dashboard

Real-time monitoring dashboard for SmartOrchestrator cost tracking and performance metrics.

![Dashboard Screenshot](https://via.placeholder.com/800x400?text=SmartOrchestrator+Dashboard)

## Features

- **Real-time Metrics**: Auto-refreshes every 5 seconds
- **Cost Tracking**: Accurate cost monitoring by provider and operation
- **Visual Analytics**: Interactive charts for cost trends and provider breakdown
- **Task History**: Detailed table of recent tasks with token usage and latency
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark Mode**: Automatic dark mode based on system preferences

## Quick Start

### 1. Install Dependencies

```bash
cd agentflow-src
pip install -r agentflow/requirements.txt
```

This installs:
- Flask 3.0.0 (web server)
- Flask-CORS 4.0.0 (API access)
- structlog 24.1.0 (structured logging)

### 2. Run the Dashboard

```bash
python dashboard_server.py
```

The dashboard will be available at: **http://localhost:5000**

### 3. Use SmartOrchestrator with Metrics

```python
from agentflow.orchestration import SmartOrchestratorWithLogging

# Initialize with metrics tracking enabled
orchestrator = SmartOrchestratorWithLogging(
    provider='anthropic',
    enable_metrics=True,
    log_level='INFO',
    log_file='logs/orchestrator.log'
)

# Your orchestration code...
plan = orchestrator.analyze_and_plan(task, capabilities, context)

# Save metrics to disk (dashboard reads from here)
orchestrator.save_metrics('logs/orchestrator_metrics.json')
```

## Dashboard Overview

### Overview Cards

Display key metrics at a glance:

| Metric | Description |
|--------|-------------|
| **Total Cost** | Cumulative cost across all tasks |
| **Total Tasks** | Number of tasks executed |
| **Average Cost/Task** | Mean cost per task |
| **Success Rate** | Percentage of successful tasks |

### Charts

1. **Cost Over Time**: Line chart showing cost trends per minute
2. **Cost by Provider**: Pie chart breaking down costs by AI provider

### Recent Tasks Table

Detailed information about the last 10 tasks:

- Timestamp
- Provider (color-coded badge)
- Operation type
- Input/Output tokens
- Cost ($)
- Latency (ms)

## API Endpoints

The dashboard server exposes several REST API endpoints:

### GET /api/metrics

Overview metrics including total cost, tasks, and success rate.

**Response:**
```json
{
  "total_cost": 0.024356,
  "total_tasks": 15,
  "success_count": 14,
  "failure_count": 1,
  "success_rate": 93.33,
  "avg_cost_per_task": 0.001624,
  "uptime_seconds": 3600.5,
  "timestamp": "2025-10-12T14:30:00"
}
```

### GET /api/costs

Cost breakdown by provider.

**Response:**
```json
{
  "providers": [
    {
      "name": "anthropic",
      "count": 10,
      "tokens": 15234,
      "cost": 0.018500
    },
    {
      "name": "deepseek",
      "count": 5,
      "tokens": 8900,
      "cost": 0.005856
    }
  ],
  "total_cost": 0.024356,
  "timestamp": "2025-10-12T14:30:00"
}
```

### GET /api/tasks

Recent task history with details.

**Response:**
```json
{
  "tasks": [
    {
      "timestamp": "2025-10-12T14:29:55",
      "provider": "anthropic",
      "model": "claude-sonnet-4-5",
      "operation": "analyze_and_plan",
      "input_tokens": 1234,
      "output_tokens": 567,
      "cost": 0.012345,
      "latency_ms": 1250.5
    }
  ],
  "count": 1,
  "timestamp": "2025-10-12T14:30:00"
}
```

### GET /api/timeline

Time-series data for cost chart (grouped by minute).

**Response:**
```json
{
  "timeline": [
    {
      "time": "2025-10-12 14:28",
      "cost": 0.008234,
      "count": 5
    },
    {
      "time": "2025-10-12 14:29",
      "cost": 0.012122,
      "count": 7
    }
  ],
  "timestamp": "2025-10-12T14:30:00"
}
```

### GET /api/health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-12T14:30:00"
}
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Dashboard (Browser)                   │
│  ┌────────────┐  ┌────────────┐  ┌───────────────┐     │
│  │ Overview   │  │   Charts   │  │  Tasks Table  │     │
│  │   Cards    │  │            │  │               │     │
│  └────────────┘  └────────────┘  └───────────────┘     │
└────────────────────┬────────────────────────────────────┘
                     │ AJAX (5s interval)
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Flask API Server (Port 5000)                │
│  ┌────────────────────────────────────────────────┐    │
│  │  /api/metrics  /api/costs  /api/tasks          │    │
│  │  /api/timeline /api/health                     │    │
│  └────────────────────────────────────────────────┘    │
└────────────────────┬────────────────────────────────────┘
                     │ Read JSON
                     ▼
┌─────────────────────────────────────────────────────────┐
│           logs/orchestrator_metrics.json                 │
│  (Generated by SmartOrchestratorWithLogging)            │
└─────────────────────────────────────────────────────────┘
```

## File Structure

```
agentflow-src/
├── dashboard_server.py              # Flask API server
├── dashboard/
│   ├── templates/
│   │   └── dashboard.html          # Dashboard UI
│   └── static/
│       ├── dashboard.js            # JavaScript logic
│       └── dashboard.css           # Styling
├── agentflow/
│   └── orchestration/
│       ├── smart_orchestrator.py           # Base orchestrator
│       ├── smart_orchestrator_logging.py   # Enhanced version
│       ├── metrics.py                      # Metrics tracking
│       └── logging_config.py               # Structured logging
└── logs/
    └── orchestrator_metrics.json   # Metrics data file
```

## Configuration

### Environment Variables

No environment variables required for the dashboard itself. However, SmartOrchestrator requires API keys:

```bash
export ANTHROPIC_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"
export DEEPSEEK_API_KEY="your-key-here"
```

### Dashboard Settings

Edit `dashboard_server.py` to customize:

```python
# Refresh interval (milliseconds)
REFRESH_INTERVAL = 5000  # Default: 5 seconds

# Max chart data points
MAX_CHART_POINTS = 20    # Default: 20 points

# Server port
app.run(port=5000)       # Default: 5000
```

## Usage Examples

### Example 1: Basic Monitoring

```python
from agentflow.orchestration import SmartOrchestratorWithLogging

# Start dashboard server (in separate terminal)
# python dashboard_server.py

# Initialize orchestrator
orchestrator = SmartOrchestratorWithLogging(
    provider='anthropic',
    enable_metrics=True
)

# Execute tasks
for task in tasks:
    plan = orchestrator.analyze_and_plan(task, capabilities, context)
    # ... execute plan ...

    # Save metrics after each task
    orchestrator.save_metrics()
```

### Example 2: Multi-Provider Tracking

```python
# Initialize with fallback enabled
orchestrator = SmartOrchestratorWithLogging(
    provider='deepseek',
    enable_fallback=True,  # Will try grok, gpt-mini, anthropic on failure
    enable_metrics=True
)

# Dashboard will show costs for all providers used
```

### Example 3: Custom Metrics Location

```python
orchestrator = SmartOrchestratorWithLogging(
    provider='anthropic',
    log_file='custom/path/orchestrator.log'
)

# Save to custom location
orchestrator.save_metrics('custom/path/metrics.json')

# Update dashboard_server.py to read from custom path
METRICS_FILE = Path('custom/path/metrics.json')
```

## Performance

- **Dashboard Load Time**: <1 second
- **API Response Time**: <50ms (typical)
- **Memory Footprint**: ~50MB (Flask server)
- **Update Latency**: 5 seconds (configurable)

## Browser Support

- Chrome 90+ ✅
- Firefox 88+ ✅
- Safari 14+ ✅
- Edge 90+ ✅
- Mobile browsers ✅

## Troubleshooting

### Dashboard shows "No tasks yet"

1. Ensure SmartOrchestrator is running and saving metrics:
   ```python
   orchestrator.save_metrics('logs/orchestrator_metrics.json')
   ```

2. Check that the metrics file exists:
   ```bash
   ls -la logs/orchestrator_metrics.json
   ```

3. Verify file permissions (must be readable by dashboard server)

### API returns empty data

1. Check Flask server logs for errors
2. Verify metrics file is valid JSON:
   ```bash
   cat logs/orchestrator_metrics.json | python -m json.tool
   ```

### Dashboard not updating

1. Check browser console for JavaScript errors (F12)
2. Verify API endpoints are accessible:
   ```bash
   curl http://localhost:5000/api/health
   ```

3. Check network tab in browser DevTools

### Port 5000 already in use

Change the port in `dashboard_server.py`:
```python
app.run(port=5001)  # Use different port
```

## Development

### Running in Debug Mode

```bash
# Enable Flask debug mode
export FLASK_DEBUG=1
python dashboard_server.py
```

### Testing API Endpoints

```bash
# Test metrics endpoint
curl http://localhost:5000/api/metrics | jq

# Test costs endpoint
curl http://localhost:5000/api/costs | jq

# Test tasks endpoint
curl http://localhost:5000/api/tasks | jq
```

### Modifying Charts

Edit `dashboard/static/dashboard.js` to customize Chart.js options:

```javascript
// Change chart colors
const CHART_COLORS = {
    primary: 'rgba(59, 130, 246, 0.8)',
    success: 'rgba(34, 197, 94, 0.8)',
    // ... add your colors
};

// Modify chart configuration
costChart = new Chart(ctx, {
    type: 'line',
    options: {
        // ... your custom options
    }
});
```

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 dashboard_server:app
```

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY agentflow-src /app
RUN pip install -r agentflow/requirements.txt

EXPOSE 5000

CMD ["python", "dashboard_server.py"]
```

### Behind Nginx

```nginx
server {
    listen 80;
    server_name dashboard.example.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Security Considerations

1. **Authentication**: Add authentication for production deployments
2. **CORS**: Configure CORS properly for your domain
3. **HTTPS**: Use HTTPS in production (via Nginx/reverse proxy)
4. **Rate Limiting**: Add rate limiting for API endpoints
5. **Input Validation**: Dashboard reads from file, but validate API inputs

## Contributing

Improvements welcome! Key areas:

- Add authentication/authorization
- Real-time WebSocket updates
- Export metrics to CSV/Excel
- Custom date range filtering
- Alert thresholds and notifications
- Compare multiple sessions

## License

Same as parent project (AutoCoder-Next).

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Flask/Chart.js documentation
3. Open an issue in the repository

---

**Built with**: Flask, Chart.js, vanilla JavaScript
**No frameworks required**: Simple, clean, fast
