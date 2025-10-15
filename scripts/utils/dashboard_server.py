"""
Real-time Metrics Dashboard Server for SmartOrchestrator

Flask API server that provides real-time metrics and cost tracking
for SmartOrchestrator operations.
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from flask import Flask, jsonify, render_template, send_from_directory
from flask_cors import CORS

# Add agentflow to path
sys.path.insert(0, str(Path(__file__).parent / 'agentflow'))

app = Flask(__name__,
            static_folder='dashboard/static',
            template_folder='dashboard/templates')
CORS(app)

# Global metrics storage (in production, use Redis or similar)
METRICS_STORE = {
    'tasks': [],
    'costs': [],
    'providers': {},
    'session_start': time.time(),
    'total_tasks': 0,
    'total_cost': 0.0,
    'success_count': 0,
    'failure_count': 0
}

# Metrics file path
METRICS_FILE = Path('logs/orchestrator_metrics.json')


def load_metrics_from_file() -> Dict[str, Any]:
    """Load metrics from disk if available"""
    if METRICS_FILE.exists():
        try:
            with open(METRICS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading metrics: {e}")
            return {}
    return {}


def update_metrics_store():
    """Update global metrics store from file"""
    file_metrics = load_metrics_from_file()

    if not file_metrics:
        return

    # Update aggregated data
    METRICS_STORE['total_tasks'] = file_metrics.get('total_tasks', 0)
    METRICS_STORE['success_count'] = file_metrics.get('successful_tasks', 0)
    METRICS_STORE['failure_count'] = file_metrics.get('failed_tasks', 0)
    METRICS_STORE['total_cost'] = file_metrics.get('total_cost', 0.0)
    METRICS_STORE['session_start'] = file_metrics.get('session_start', time.time())

    # Update provider breakdown
    model_usage = file_metrics.get('model_usage', {})
    METRICS_STORE['providers'] = model_usage

    # Extract task history (from orchestrator stats if available)
    if 'orchestrator' in file_metrics and 'task_costs' in file_metrics['orchestrator']:
        METRICS_STORE['tasks'] = file_metrics['orchestrator']['task_costs']


@app.route('/')
def index():
    """Serve dashboard HTML"""
    return render_template('dashboard.html')


@app.route('/api/metrics')
def get_metrics():
    """
    Get current metrics overview

    Returns:
        JSON with current system stats
    """
    update_metrics_store()

    # Calculate uptime
    uptime_seconds = time.time() - METRICS_STORE['session_start']

    # Calculate success rate
    total_tasks = METRICS_STORE['total_tasks']
    success_rate = (
        (METRICS_STORE['success_count'] / total_tasks * 100)
        if total_tasks > 0 else 0.0
    )

    # Calculate average cost per task
    avg_cost = (
        METRICS_STORE['total_cost'] / total_tasks
        if total_tasks > 0 else 0.0
    )

    return jsonify({
        'total_cost': round(METRICS_STORE['total_cost'], 6),
        'total_tasks': total_tasks,
        'success_count': METRICS_STORE['success_count'],
        'failure_count': METRICS_STORE['failure_count'],
        'success_rate': round(success_rate, 2),
        'avg_cost_per_task': round(avg_cost, 6),
        'uptime_seconds': round(uptime_seconds, 1),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/costs')
def get_costs():
    """
    Get cost breakdown by provider

    Returns:
        JSON with per-provider cost details
    """
    update_metrics_store()

    providers = METRICS_STORE['providers']

    # Format provider data
    provider_data = []
    for provider_name, stats in providers.items():
        provider_data.append({
            'name': provider_name,
            'count': stats.get('count', 0),
            'tokens': stats.get('tokens', 0),
            'cost': round(stats.get('cost', 0.0), 6)
        })

    # Sort by cost descending
    provider_data.sort(key=lambda x: x['cost'], reverse=True)

    return jsonify({
        'providers': provider_data,
        'total_cost': round(METRICS_STORE['total_cost'], 6),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/tasks')
def get_tasks():
    """
    Get recent task history

    Returns:
        JSON with recent task details
    """
    update_metrics_store()

    # Get last 50 tasks
    recent_tasks = METRICS_STORE['tasks'][-50:]

    # Format task data
    formatted_tasks = []
    for task in recent_tasks:
        formatted_tasks.append({
            'timestamp': datetime.fromtimestamp(task['timestamp']).isoformat(),
            'provider': task['provider'],
            'model': task['model'],
            'operation': task['operation'],
            'input_tokens': task['input_tokens'],
            'output_tokens': task['output_tokens'],
            'cost': round(task['total_cost'], 6),
            'latency_ms': round(task.get('latency_ms', 0), 2)
        })

    return jsonify({
        'tasks': formatted_tasks,
        'count': len(formatted_tasks),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/timeline')
def get_timeline():
    """
    Get cost timeline data for chart

    Returns:
        JSON with time-series cost data
    """
    update_metrics_store()

    tasks = METRICS_STORE['tasks']

    # Group by minute
    timeline = []
    if tasks:
        current_minute = None
        minute_cost = 0.0
        minute_count = 0

        for task in tasks:
            task_time = datetime.fromtimestamp(task['timestamp'])
            task_minute = task_time.strftime('%Y-%m-%d %H:%M')

            if current_minute is None:
                current_minute = task_minute

            if task_minute == current_minute:
                minute_cost += task['total_cost']
                minute_count += 1
            else:
                timeline.append({
                    'time': current_minute,
                    'cost': round(minute_cost, 6),
                    'count': minute_count
                })
                current_minute = task_minute
                minute_cost = task['total_cost']
                minute_count = 1

        # Add last minute
        if current_minute:
            timeline.append({
                'time': current_minute,
                'cost': round(minute_cost, 6),
                'count': minute_count
            })

    return jsonify({
        'timeline': timeline,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    # Ensure logs directory exists
    Path('logs').mkdir(exist_ok=True)

    print("""
╔══════════════════════════════════════════════════════════╗
║    SmartOrchestrator Metrics Dashboard                  ║
║                                                          ║
║    Dashboard: http://localhost:5000                     ║
║    API Docs:  http://localhost:5000/api/health         ║
║                                                          ║
║    Auto-refreshes every 5 seconds                       ║
╚══════════════════════════════════════════════════════════╝
    """)

    app.run(debug=True, port=5000, host='0.0.0.0')
