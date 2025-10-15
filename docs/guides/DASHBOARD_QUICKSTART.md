# SmartOrchestrator Dashboard - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies (1 minute)

```bash
cd agentflow-src
pip install -r agentflow/requirements.txt
```

This installs: Flask, Flask-CORS, structlog

### Step 2: Generate Test Data (30 seconds)

```bash
python test_dashboard_integration.py --mode multiple
```

This creates sample metrics with 3 test tasks.

### Step 3: Start Dashboard (5 seconds)

```bash
./start_dashboard.sh
```

OR manually:

```bash
python dashboard_server.py
```

### Step 4: Open Browser

Navigate to: **http://localhost:5000**

---

## 📊 What You'll See

### Dashboard Overview

```
╔════════════════════════════════════════════════════════╗
║  SmartOrchestrator Metrics Dashboard        [●Connected]║
╠════════════════════════════════════════════════════════╣
║                                                         ║
║  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ ║
║  │   💰     │  │   📊     │  │   📈     │  │   ✅   │ ║
║  │ $0.0234  │  │    15    │  │ $0.0016  │  │  93%   │ ║
║  │Total Cost│  │Tot Tasks │  │ Avg Cost │  │Success │ ║
║  └──────────┘  └──────────┘  └──────────┘  └────────┘ ║
║                                                         ║
║  ┌─────────────────────────────┐ ┌──────────────────┐ ║
║  │ Cost Over Time (Line Chart) │ │ Cost by Provider│ ║
║  │                              │ │   (Pie Chart)   │ ║
║  │  ^                           │ │                  │ ║
║  │  │  /\    /\                 │ │  anthropic: 60% │ ║
║  │  │ /  \  /  \  /\            │ │  deepseek:  30% │ ║
║  │  │/    \/    \/  \           │ │  grok:      10% │ ║
║  │  └─────────────────>         │ │                  │ ║
║  └─────────────────────────────┘ └──────────────────┘ ║
║                                                         ║
║  Recent Tasks                                           ║
║  ┌─────────────────────────────────────────────────┐  ║
║  │Time      Provider   Op    In   Out   Cost  Lat │  ║
║  │14:30:01  anthropic  plan  1.2K 567  $0.012 1.2s│  ║
║  │14:29:55  deepseek   valid 890  234  $0.003 0.8s│  ║
║  │14:29:48  anthropic  specs 2.1K 890  $0.018 2.1s│  ║
║  └─────────────────────────────────────────────────┘  ║
╚════════════════════════════════════════════════════════╝
```

---

## 💻 Using in Your Code

### Basic Usage

```python
from agentflow.orchestration import SmartOrchestratorWithLogging

# 1. Initialize with metrics
orchestrator = SmartOrchestratorWithLogging(
    provider='anthropic',
    enable_metrics=True,
    log_level='INFO'
)

# 2. Execute your tasks
plan = orchestrator.analyze_and_plan(
    task="Build a REST API",
    capabilities=["Python", "FastAPI"],
    context={"complexity": "medium"}
)

# 3. Save metrics (dashboard auto-updates)
orchestrator.save_metrics()
```

### Advanced Usage

```python
# With fallback and model selection
orchestrator = SmartOrchestratorWithLogging(
    provider='deepseek',           # Start cheap
    enable_fallback=True,          # Auto-fallback on errors
    enable_model_selection=True,   # Smart model routing
    enable_metrics=True            # Track everything
)

# Execute multiple tasks
tasks = ["Task 1", "Task 2", "Task 3"]
for task in tasks:
    plan = orchestrator.analyze_and_plan(task, caps, ctx)
    # ... execute plan ...
    orchestrator.save_metrics()  # Update dashboard

# Get cost summary
summary = orchestrator.get_cost_summary()
print(f"Total cost: ${summary['total_cost']:.6f}")
```

---

## 🎯 Key Features

### Real-time Metrics
- **Cost Tracking**: Accurate to 6 decimal places
- **Token Usage**: Input and output tokens
- **Success Rate**: Task completion percentage
- **Provider Breakdown**: Cost per AI provider

### Visual Analytics
- **Cost Timeline**: Line chart showing cost trends
- **Provider Distribution**: Pie chart of cost breakdown
- **Recent Tasks**: Table with 10 latest operations

### Auto-Updates
- Refreshes every **5 seconds**
- No page reload needed
- Live status indicator

---

## 📁 Project Structure

```
agentflow-src/
├── dashboard_server.py          # Flask API (start this)
├── dashboard/
│   ├── templates/
│   │   └── dashboard.html      # UI
│   └── static/
│       ├── dashboard.js        # Logic
│       └── dashboard.css       # Styles
├── test_dashboard_integration.py  # Test script
├── start_dashboard.sh          # Quick launcher
└── logs/
    └── orchestrator_metrics.json  # Data source
```

---

## 🔧 Configuration

### Change Refresh Interval

Edit `dashboard/static/dashboard.js`:
```javascript
const REFRESH_INTERVAL = 3000;  // 3 seconds instead of 5
```

### Change Server Port

Edit `dashboard_server.py`:
```python
app.run(port=5001)  # Use port 5001
```

### Custom Metrics Location

```python
# In your code
orchestrator.save_metrics('custom/path/metrics.json')

# In dashboard_server.py
METRICS_FILE = Path('custom/path/metrics.json')
```

---

## 🐛 Troubleshooting

### "No tasks yet" message

**Problem**: Dashboard shows no data

**Solution**:
```bash
# Generate test data first
python test_dashboard_integration.py --mode basic
```

### Port 5000 in use

**Problem**: `Address already in use`

**Solution**:
```bash
# Kill existing process
lsof -ti:5000 | xargs kill -9

# Or use different port
# Edit dashboard_server.py → app.run(port=5001)
```

### Metrics not updating

**Problem**: Dashboard not showing new data

**Solution**:
```python
# Make sure to call save_metrics() after each task
orchestrator.save_metrics()
```

**Check**:
```bash
# Verify file exists and is recent
ls -lh logs/orchestrator_metrics.json
```

### API errors

**Problem**: 404 or 500 errors

**Solution**:
```bash
# Check Flask logs
python dashboard_server.py

# Test API manually
curl http://localhost:5000/api/health
curl http://localhost:5000/api/metrics
```

---

## 📊 API Reference

| Endpoint | Method | Description | Example |
|----------|--------|-------------|---------|
| `/` | GET | Dashboard HTML | Open in browser |
| `/api/metrics` | GET | Overview stats | Total cost, tasks, success rate |
| `/api/costs` | GET | Provider costs | Cost breakdown by provider |
| `/api/tasks` | GET | Recent tasks | Last 50 tasks with details |
| `/api/timeline` | GET | Cost over time | Minute-by-minute cost data |
| `/api/health` | GET | Health check | Server status |

### Example API Call

```bash
# Get current metrics
curl http://localhost:5000/api/metrics | jq

# Expected response:
{
  "total_cost": 0.024356,
  "total_tasks": 15,
  "success_rate": 93.33,
  "avg_cost_per_task": 0.001624,
  "uptime_seconds": 3600.5,
  "timestamp": "2025-10-12T14:30:00"
}
```

---

## 🎨 Customization

### Add Custom Metrics

Edit `dashboard_server.py`:
```python
@app.route('/api/custom')
def get_custom():
    # Your custom metrics logic
    return jsonify({
        'metric': value
    })
```

Update `dashboard.js`:
```javascript
async function fetchCustomData() {
    const response = await fetch('/api/custom');
    const data = await response.json();
    // Display your data
}
```

### Change Theme Colors

Edit `dashboard/static/dashboard.css`:
```css
:root {
    --primary: #your-color;
    --success: #your-color;
    /* ... more colors ... */
}
```

---

## 🚀 Production Deployment

### Using Gunicorn (Recommended)

```bash
# Install gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 dashboard_server:app

# With logging
gunicorn -w 4 -b 0.0.0.0:5000 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  dashboard_server:app
```

### Using systemd Service

Create `/etc/systemd/system/dashboard.service`:
```ini
[Unit]
Description=SmartOrchestrator Dashboard
After=network.target

[Service]
User=youruser
WorkingDirectory=/path/to/agentflow-src
ExecStart=/usr/bin/python3 dashboard_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable dashboard
sudo systemctl start dashboard
```

---

## 📚 Documentation

- **Full Guide**: `README_DASHBOARD.md` (600+ lines)
- **Summary**: `DASHBOARD_SUMMARY.md`
- **Quick Start**: This file

---

## ⚡ Performance Tips

1. **Batch save metrics** - Don't save after every operation
2. **Adjust refresh rate** - 10s instead of 5s for slower systems
3. **Limit chart points** - Keep MAX_CHART_POINTS at 20
4. **Use Gunicorn** - Better performance than Flask dev server

---

## 🎯 Success Checklist

- [ ] Dependencies installed
- [ ] Test script runs successfully
- [ ] Dashboard server starts
- [ ] Browser shows metrics
- [ ] Charts display data
- [ ] Recent tasks table populated
- [ ] Auto-refresh works (watch timestamp)

---

**That's it! You're ready to monitor SmartOrchestrator costs in real-time.**

For detailed documentation, see `README_DASHBOARD.md`.
