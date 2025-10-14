# APC-MCP Quickstart Guide

**Time to first run**: < 5 minutes ⚡

---

## Prerequisites

- ✅ Python 3.10+ (`python3 --version`)
- ✅ Node.js 18+ (`node --version`)
- ✅ Docker + Docker Compose (`docker compose version`)
- ✅ Make (`make --version`)

---

## Setup (< 2 minutes)

```bash
# 1. Navigate to apc-mcp directory
cd /home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src/apc-mcp

# 2. Copy environment template
cp .env.example .env

# 3. Start PostgreSQL + pgvector + Adminer (in background)
make up

# Wait for database to be healthy (~10 seconds)
# Check logs: make logs

# 4. Setup Python environment (creates .venv, installs deps)
make psetup

# 5. Setup Node environment (npm install)
make nsetup
```

**Expected output**:
```
[OK] Python env ready. Activate with: source python/.venv/bin/activate
[OK] Node deps installed. Run dev with: npm run dev
```

---

## Test Python Runtime (< 1 minute)

```bash
# Run Python MCP stub (simulates CRC validation)
make py-dev
```

**Expected output**:
```
[MCP Stub] Final state: SOFT
```

**What happened**:
1. ✅ Event bus initialized
2. ✅ State machine started (state = OK)
3. ✅ CRC signal emitted (drift = 0.12 > 0.10 threshold)
4. ✅ State transitioned: OK → SOFT
5. ✅ Nudge emitted ("Focus drift detected")

**Code executed**: `apc_runtime/event_bus.py` + `state_machine.py`

---

## Test Node Launcher (< 1 minute)

```bash
# Run Node launcher (TypeScript with tsx watch)
make node-dev
```

**Expected output**:
```
[APC Launcher] Starting...
[APC Launcher] State after drift: SOFT
```

**What happened**:
1. ✅ Event bus initialized (Node EventEmitter)
2. ✅ State machine started (state = OK)
3. ✅ CRC signal emitted (drift = 0.12)
4. ✅ State transitioned: OK → SOFT
5. ✅ Tool policy enforced (test_run allowed, timeout validated)

**Code executed**: `node/src/index.ts` + `runtime/` + `launcher/middleware/`

---

## Test PostgreSQL + pgvector (< 1 minute)

```bash
# Access Adminer (database UI)
# Open in browser: http://localhost:8080

# Credentials (from .env):
# System: PostgreSQL
# Server: db
# Username: apc_user
# Password: apc_pass
# Database: apc
```

**Verify**:
1. ✅ PostgreSQL is running
2. ✅ `vector` extension is installed
3. ✅ `expectation_vectors` table exists (created by pgvector_dao.py on first use)

---

## Quick Commands

```bash
# Start services
make up

# Stop services
make down

# View logs
make logs

# Access database UI
make db
# Opens http://localhost:8080

# Python MCP stub
make py-dev

# Node launcher (watch mode)
make node-dev

# Lint Node code
make lint

# Format Node code
make fmt
```

---

## Verify Everything Works

Run all 3 components simultaneously:

**Terminal 1** (Database):
```bash
cd apc-mcp
make up
make logs
```

**Terminal 2** (Python MCP):
```bash
cd apc-mcp
make py-dev
```

**Terminal 3** (Node Launcher):
```bash
cd apc-mcp
make node-dev
```

**Expected**:
- ✅ PostgreSQL healthy (Terminal 1 logs show "database system is ready")
- ✅ Python MCP transitions state to SOFT (Terminal 2 output)
- ✅ Node launcher transitions state to SOFT (Terminal 3 output)

---

## Troubleshooting

### Python venv not activating

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

### Node deps not installing

```bash
cd node
npm install
```

### Docker not starting

```bash
# Check Docker is running
docker ps

# Check logs
docker compose logs db

# Restart
docker compose down
docker compose up -d
```

### Port conflicts

```bash
# If port 5432 (PostgreSQL) is in use
# Edit .env and change PGPORT to 5433
# Edit docker-compose.yml: "5433:5432"

# If port 8080 (Adminer) is in use
# Edit docker-compose.yml: "8081:8080"
```

---

## Next Steps

Once everything works:

1. **Explore the code**:
   - `python/src/apc_runtime/` - Python components
   - `node/src/runtime/` - TypeScript runtime
   - `node/src/launcher/` - Launcher + middleware

2. **Read the docs**:
   - `README.md` - Project overview
   - `docs/DESIGN_DECISIONS_FINAL.md` - Architecture decisions
   - `docs/PHASE_1_COMPLETION_REPORT.md` - What's been built

3. **Start Phase 2**:
   - Implement PRE gate (SessionMonitor CRC validation)
   - Setup pgvector schema (expectation_vectors table)
   - Test drift detection with real data

---

## Success Metrics

After quickstart, you should have:

- ✅ PostgreSQL + pgvector running (http://localhost:8080)
- ✅ Python venv with apc_runtime installed
- ✅ Node deps installed (typescript, tsx, pg, etc.)
- ✅ All scripts executable and working
- ✅ Event bus + state machine working in both Python and Node
- ✅ Tool policy enforcement working

**Time spent**: < 5 minutes total ⚡

---

**Ready for Phase 2 implementation! 🚀**
