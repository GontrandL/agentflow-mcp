# Scripts Directory

Utility scripts and runners for AgentFlow MCP development and testing.

## Structure

### runners/
Delegation and worker runner scripts:
- `run_delegation_pool.py` - Pool-based delegation execution
- `delegate_*.py` - Specialized delegation scripts
- `launch_*.sh` - Worker launch scripts
- `spawn_*.sh` - Worker spawn utilities

### utils/
Development utilities:
- `parse_session_tags.py` - Session recovery parser
- `compare_models.py` - Model comparison tool
- `extract_and_validate_workers.py` - Worker validation
- `dashboard_server.py` - Monitoring dashboard
- `quick_start.py` - Quick start utility

### Shell Scripts (root-level)
- `setup.sh` - Initial project setup
- `start_dashboard.sh` - Start monitoring dashboard
- `monitor_mcp.sh` - Monitor MCP servers
- `INSTALL_MCP_SERVERS.sh` - MCP server installation

## MCP Wrappers (in project root)

These files must stay in the project root as they're referenced by MCP configuration:
- `agentflow_mcp_wrapper.sh` - AgentFlow MCP wrapper
- `apc_mcp_wrapper.sh` - APC MCP wrapper

## Usage

### Run Delegation Pool
```bash
python scripts/runners/run_delegation_pool.py
```

### Parse Session for Recovery
```bash
python scripts/utils/parse_session_tags.py SESSION_FILE.md
```

### Compare Models
```bash
python scripts/utils/compare_models.py
```

### Start Dashboard
```bash
bash scripts/start_dashboard.sh
```

## Data Directory

Test results and session data are stored in `../data/`:
- `*.json` - Test results and session recovery data
- `*_tasks.json` - Task definitions

## Archive

Historical scripts are in `../archive/scripts/` for reference.
