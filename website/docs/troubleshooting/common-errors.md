# Common Errors and Solutions

This guide covers the most common errors you'll encounter when using Hephaestus and how to fix them quickly.

## Installation & Setup Issues

### Python Version Error
**Error:**
```
ERROR: Python version 3.9 is not supported. Hephaestus requires Python 3.10 or higher.
```

**Solution:**
Install Python 3.10 or higher:
```bash
# macOS with Homebrew
brew install python@3.10

# Ubuntu/Debian
sudo apt update && sudo apt install python3.10 python3.10-venv

# Verify version
python3 --version
```

### Missing Dependencies
**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
ModuleNotFoundError: No module named 'qdrant_client'
```

**Solution:**
Install Python dependencies:
```bash
# Using pip
pip install -r requirements.txt

# Or using poetry (recommended)
poetry install

# Verify installation
python -c "import fastapi; import qdrant_client; print('Dependencies OK')"
```

### Qdrant Connection Failed
**Error:**
```
QdrantException: Could not connect to Qdrant at http://localhost:6333
Connection refused
```

**Solution:**
Start Qdrant vector store:
```bash
# Using Docker (recommended)
docker run -d -p 6333:6333 qdrant/qdrant

# Or using docker-compose
docker-compose up -d

# Verify Qdrant is running
curl http://localhost:6333/health
# Should return: {"status":"ok"}
```

## Configuration Issues

### API Key Not Found
**Error:**
```
Error: OPENAI_API_KEY environment variable is required
KeyError: 'OPENAI_API_KEY'
```

**Solution:**
1. Create `.env` file in project root (copy from `.env.example`):
```bash
cp .env.example .env
```

2. Add your API keys to `.env`:
```bash
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=sk-or-v1-...  # Optional but recommended
ANTHROPIC_API_KEY=sk-ant-...     # Optional
```

3. Verify environment variables are loaded:
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OpenAI Key:', os.getenv('OPENAI_API_KEY')[:10] if os.getenv('OPENAI_API_KEY') else 'NOT FOUND')"
```

### Invalid Configuration File
**Error:**
```
yaml.scanner.ScannerError: mapping values are not allowed here
ValidationError: Invalid configuration in hephaestus_config.yaml
```

**Solution:**
1. Check YAML syntax - ensure proper indentation (use spaces, not tabs):
```yaml
llm:
  embedding_model: "text-embedding-3-large"  # Correct indentation
  primary_llm:
    provider: "openrouter"
```

2. Validate your config file:
```bash
python -c "import yaml; yaml.safe_load(open('hephaestus_config.yaml'))"
```

3. Use example configs as reference:
```bash
# Copy example config
cp examples/azure_config_example.yaml hephaestus_config.yaml
# Edit with your settings
```

### Working Directory Not Set
**Error:**
```
Error: Working directory not found: None
FileNotFoundError: PRD.md not found in working directory
```

**Solution:**
Configure your working directory in `hephaestus_config.yaml`:
```yaml
paths:
  project_root: "/absolute/path/to/your/project"

git:
  main_repo_path: "/absolute/path/to/your/project"
```

**Important:**
- Use **absolute paths**, not relative paths
- Directory must be a git repository: `cd /path/to/project && git init`
- Must have at least one commit: `git commit --allow-empty -m "Initial"`

## Database Issues

### Database Locked
**Error:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
Another process is using the database:
```bash
# Find processes using the database
lsof hephaestus.db

# Kill the processes if needed
pkill -f "python.*hephaestus"

# Or restart the server
python run_server.py
```

### Database Schema Mismatch
**Error:**
```
OperationalError: no such table: workflows
sqlalchemy.exc.ProgrammingError: no such column: tasks.phase_id
```

**Solution:**
Initialize or migrate the database:
```bash
# Initialize fresh database
python scripts/init_db.py

# If using Qdrant
python scripts/init_qdrant.py

# Run migrations if needed
alembic upgrade head
```

## MCP Server Issues

### MCP Server Not Found
**Error:**
```
Error: MCP server 'hephaestus' not found
Tool 'create_task' not available
```

**Solution:**
Configure MCP servers in Claude Code:
```bash
# Add Hephaestus MCP server
claude mcp add hephaestus "cd /path/to/Hephaestus && python -m src.mcp.server"

# Add Qdrant MCP server
claude mcp add qdrant "cd /path/to/Hephaestus && python qdrant_mcp_openai.py"

# Verify servers are configured
claude mcp list

# Should show:
# - hephaestus
# - qdrant
```

### MCP Server Crashes
**Error:**
```
Error: MCP server terminated unexpectedly
Connection to MCP server lost
```

**Solution:**
1. Check if backend server is running:
```bash
curl http://localhost:8000/health
```

2. Start backend server if not running:
```bash
python run_server.py
```

3. Check MCP server logs:
```bash
# MCP servers log to their working directory
tail -f logs/backend.log
```

4. Test MCP server directly:
```bash
# Test Hephaestus MCP
python -c "from src.mcp import server; print('MCP OK')"

# Test Qdrant MCP
python qdrant_mcp_openai.py --help
```

## Agent Issues

### Agent Not Spawning
**Error:**
```
WARNING: No agents available to handle task
Task stuck in 'pending' status
```

**Solution:**
1. Check if tmux is installed and working:
```bash
tmux -V
# Should show: tmux 3.x or higher
```

2. Verify backend can spawn agents:
```bash
# Check backend logs
tail -f logs/backend.log | grep -i "spawn"

# Should see: "Spawning agent in tmux session..."
```

3. Check tmux sessions:
```bash
tmux list-sessions
# Should show agent sessions like: agent-abc123-xyz789
```

4. Attach to agent session to debug:
```bash
tmux list-sessions  # Get session name
tmux attach -t agent-abc123-xyz789
# Press Ctrl+b then d to detach without killing
```

### Agent Authorization Failed
**Error:**
```
HTTP 403: Agent not authorized for this task
Agent not found in database
```

**Solution:**
Agents must use their exact UUID from the initial prompt:
```python
# WRONG - using placeholder
agent_id = "agent-mcp"

# CORRECT - using actual UUID from prompt
agent_id = "6a062184-e189-4d8d-8376-89da987b9996"
```

Validate your agent ID:
```bash
curl http://localhost:8000/validate_agent_id/YOUR-AGENT-ID
```

### Monitor Killing Agents
**Error:**
```
WARNING: Agent session terminated by monitor
Orphaned agent session detected
```

**Solution:**
System includes 120-second grace period for new agents. If still happening:

1. Check monitor is running properly:
```bash
tail -f logs/monitor.log
```

2. Verify monitoring interval is reasonable:
```yaml
# In hephaestus_config.yaml or .env
MONITORING_INTERVAL_SECONDS=60  # Default
```

3. Check database latency:
```bash
# Should return quickly
sqlite3 hephaestus.db "SELECT COUNT(*) FROM agents;"
```

## Workflow Issues

### Tasks Stuck in Pending
**Error:**
```
Task has been in 'pending' status for 10 minutes
No progress on workflow
```

**Solution:**
1. Check if agents are available:
```bash
curl http://localhost:8000/agent_status
```

2. Check task assignment:
```bash
curl http://localhost:8000/task_progress
```

3. Verify queue service is running:
```bash
# Check backend logs for queue errors
tail -f logs/backend.log | grep -i queue
```

4. Manually assign task if needed:
```python
from src.sdk import HephaestusSDK
sdk = HephaestusSDK(...)
sdk.assign_task(task_id, agent_id)
```

### Phase Instructions Not Working
**Error:**
```
Agent ignoring phase guidelines
Guardian not steering agent
Agent performing wrong type of work
```

**Solution:**
1. Check phase definition has clear instructions:
```python
phase = Phase(
    id=1,
    name="Investigation",
    instructions="""
    MANDATORY STEPS:
    1. Read the bug report carefully
    2. Reproduce the bug
    3. Document exact error messages
    
    SUCCESS CRITERIA:
    - Bug is reproducible
    - Error captured in logs
    """,
)
```

2. Verify Guardian is running:
```bash
tail -f logs/monitor.log | grep -i guardian
```

3. Check steering is enabled:
```yaml
# In hephaestus_config.yaml
monitoring:
  enable_steering: true
  steering_threshold: 0.7
```

### Git Worktree Errors
**Error:**
```
fatal: not a valid object name: 'HEAD'
GitCommandError: Cannot create worktree
fatal: '/path' is not a git repository
```

**Solution:**
1. Initialize git in working directory:
```bash
cd /path/to/project
git init
git add .
git commit -m "Initial commit"
```

2. Verify git configuration:
```bash
git config user.name
git config user.email

# If not set:
git config user.name "Your Name"
git config user.email "you@example.com"
```

3. Check worktree path permissions:
```bash
# Ensure directory is writable
ls -la /tmp/hephaestus_worktrees

# Create if missing
mkdir -p /tmp/hephaestus_worktrees
```

## Performance Issues

### Slow LLM Responses
**Error:**
```
Task taking too long
Agents waiting for LLM responses
Timeout errors from LLM provider
```

**Solution:**
Use faster LLM provider (OpenRouter with Cerebras):
```yaml
# In hephaestus_config.yaml
llm:
  primary_llm:
    provider: "openrouter"
    model: "gpt-oss:120b"
    base_url: "https://openrouter.ai/api/v1"
```

This provides 1000+ tokens/sec vs ~100 tokens/sec for standard OpenAI.

### High Memory Usage
**Error:**
```
MemoryError: Out of memory
System becomes unresponsive
```

**Solution:**
1. Limit concurrent agents:
```python
# In SDK initialization
sdk = HephaestusSDK(
    ...,
    max_concurrent_agents=3  # Reduce from default 5
)
```

2. Clear Qdrant cache periodically:
```bash
python scripts/clean_qdrant.py
```

3. Monitor system resources:
```bash
# Check memory usage
htop

# Check Docker containers
docker stats
```

## Frontend Issues

### Frontend Won't Start
**Error:**
```
Error: Cannot find module 'vite'
npm ERR! Missing script: "dev"
```

**Solution:**
Install frontend dependencies:
```bash
cd frontend
npm install
npm run dev
```

### Frontend Can't Connect to Backend
**Error:**
```
Network Error: Failed to fetch
CORS error
Connection refused to localhost:8000
```

**Solution:**
1. Verify backend is running:
```bash
curl http://localhost:8000/health
```

2. Check API URL in frontend config:
```typescript
// frontend/src/config.ts
export const API_URL = "http://localhost:8000"
```

3. Check CORS settings in backend:
```python
# src/mcp/server.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    ...
)
```

## Verification Commands

Quick health check for entire system:

```bash
#!/bin/bash
echo "🔍 Hephaestus System Health Check"
echo "=================================="

# Python version
echo -n "Python: "
python3 --version

# Backend
echo -n "Backend: "
curl -s http://localhost:8000/health && echo "✅ OK" || echo "❌ FAILED"

# Qdrant
echo -n "Qdrant: "
curl -s http://localhost:6333/health && echo "✅ OK" || echo "❌ FAILED"

# Database
echo -n "Database: "
[ -f hephaestus.db ] && echo "✅ EXISTS" || echo "❌ MISSING"

# Frontend
echo -n "Frontend: "
curl -s http://localhost:5173 > /dev/null && echo "✅ OK" || echo "❌ NOT RUNNING"

# Tmux
echo -n "Tmux: "
tmux -V && echo "✅ OK" || echo "❌ NOT INSTALLED"

# MCP Servers
echo -n "MCP Servers: "
claude mcp list 2>&1 | grep -q hephaestus && echo "✅ OK" || echo "❌ NOT CONFIGURED"

echo "=================================="
```

Save this as `check_health.sh` and run it to diagnose issues quickly.

## Getting More Help

If your issue isn't covered here:

1. **Check logs:**
   - Backend: `logs/backend.log`
   - Guardian: `logs/monitor.log`
   - Agent sessions: `tmux attach -t agent-xxx`

2. **Run validation script:**
   ```bash
   python check_setup_macos.py
   ```

3. **Search documentation:**
   - [Quick Start Guide](../getting-started/quick-start.md)
   - [Agent Issues](./agent-issues.md)
   - [Best Practices](../guides/best-practices.md)

4. **Community support:**
   - [GitHub Discussions](https://github.com/Ido-Levi/Hephaestus/discussions)
   - [Discord Server](https://discord.gg/FyrC4fpS)
   - [Issue Tracker](https://github.com/Ido-Levi/Hephaestus/issues)

5. **Enable debug logging:**
   ```bash
   export LOG_LEVEL=DEBUG
   python run_server.py
   ```
