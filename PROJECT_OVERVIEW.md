# Hephaestus Project Overview

## What is Hephaestus?

Hephaestus is a **semi-structured agentic framework** that enables AI workflows to write their own instructions as agents discover what needs to be done. Unlike traditional frameworks that require predefined branching logic for every scenario, Hephaestus allows agents to dynamically create new tasks based on their discoveries.

### The Core Innovation

**Traditional workflows:** Predict every scenario upfront → rigid plan → breaks when reality diverges

**Hephaestus approach:** Define work types → agents discover → workflow adapts in real-time

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Hephaestus System                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │   Phase 1    │──────▶   Phase 2    │──────▶   Phase 3    │ │
│  │  Analysis    │◀──────│Implementatn │◀──────│ Validation  │ │
│  └──────────────┘      └──────────────┘      └──────────────┘ │
│         │                     │                      │          │
│         └─────────────────────┼──────────────────────┘          │
│                               ▼                                  │
│                    ┌─────────────────────┐                      │
│                    │   Task Queue        │                      │
│                    │   (SQLite + Qdrant) │                      │
│                    └─────────────────────┘                      │
│                               │                                  │
│         ┌─────────────────────┼──────────────────────┐          │
│         ▼                     ▼                      ▼          │
│  ┌──────────┐          ┌──────────┐          ┌──────────┐     │
│  │ Agent 1  │          │ Agent 2  │          │ Agent 3  │     │
│  │ (tmux)   │          │ (tmux)   │          │ (tmux)   │     │
│  └──────────┘          └──────────┘          └──────────┘     │
│         │                     │                      │          │
│         └─────────────────────┼──────────────────────┘          │
│                               ▼                                  │
│                    ┌─────────────────────┐                      │
│                    │  Guardian Monitor   │                      │
│                    │  (Coherence Check)  │                      │
│                    └─────────────────────┘                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Frontend UI       │
                    │   (React + Vite)    │
                    │   - Kanban Board    │
                    │   - Agent Monitor   │
                    │   - Logs Viewer     │
                    └─────────────────────┘
```

## Directory Structure

```
Hephaestus/
├── src/                          # Core orchestration stack
│   ├── agents/                   # Agent lifecycle management
│   │   ├── agent_manager.py     # Spawns and manages agents
│   │   └── prompts/             # Agent prompt templates
│   ├── memory/                   # RAG system (Qdrant)
│   │   ├── rag_system.py        # Vector store operations
│   │   └── vector_store.py      # Qdrant client wrapper
│   ├── mcp/                      # FastAPI MCP server
│   │   ├── server.py            # Main MCP endpoint
│   │   └── routes/              # API routes
│   ├── monitoring/               # Guardian & Conductor
│   │   ├── guardian.py          # Coherence monitoring
│   │   └── conductor.py         # Agent coordination
│   ├── core/                     # Shared utilities
│   │   ├── database.py          # SQLAlchemy models
│   │   ├── queue_service.py     # Task queue
│   │   └── llm_interface.py     # Multi-provider LLM
│   ├── phases/                   # Phase system
│   │   └── phase_manager.py     # Phase coordination
│   ├── validation/               # Task/result validation
│   └── workflow/                 # Workflow engine
│
├── frontend/                     # React dashboard
│   ├── src/
│   │   ├── components/          # UI components
│   │   ├── pages/               # Page layouts
│   │   └── hooks/               # React hooks
│   ├── package.json
│   └── vite.config.ts
│
├── example_workflows/            # Example workflow implementations
│   ├── prd_to_software/         # PRD → Software builder
│   │   ├── phases.py            # Phase definitions
│   │   └── board_config.py      # Kanban configuration
│   └── swebench_solver/         # SWEBench issue solver
│       ├── phases.py
│       └── board_config.py
│
├── tests/                        # Comprehensive test suite
│   ├── integration/             # Integration tests
│   ├── mcp_integration/         # MCP protocol tests
│   ├── sdk/                     # SDK tests
│   └── unit/                    # Unit tests
│
├── scripts/                      # Utility scripts
│   ├── init_db.py              # Initialize SQLite database
│   ├── init_qdrant.py          # Initialize Qdrant collections
│   ├── clean_qdrant.py         # Clean vector store
│   ├── bootstrap_project.py     # Bootstrap new project
│   └── verify_setup.py         # Verify installation
│
├── website/                      # Docusaurus documentation site
│   └── docs/                    # Documentation markdown files
│       ├── getting-started/
│       ├── guides/
│       ├── core/
│       ├── features/
│       ├── sdk/
│       └── troubleshooting/
│
├── config/                       # Configuration files
│   └── agent_config.yaml        # Agent-specific configs
│
├── examples/                     # Example files
│   ├── PRD.md                   # Example PRD
│   └── sub_agents/              # Sub-agent definitions
│
├── .claude/                      # Claude Code agents
│   └── agents/                  # Custom sub-agents
│
├── run_server.py                # Start MCP backend server
├── run_monitor.py               # Start Guardian monitor
├── run_example.py               # Run PRD workflow example
├── run_swebench_workflow.py     # Run SWEBench solver
├── check_setup_macos.py         # Validate installation
├── hephaestus_config.yaml       # Main configuration
├── requirements.txt             # Python dependencies
└── pyproject.toml              # Poetry configuration
```

## How Hephaestus Works

### 1. Phase System

Workflows are organized into **logical phase types** that represent different kinds of work:

- **Phase 1 (Analysis)**: Understanding, planning, investigation
- **Phase 2 (Implementation)**: Building, fixing, optimizing  
- **Phase 3 (Validation)**: Testing, verification, quality checks

**Key insight:** Agents can spawn tasks in ANY phase based on discoveries, creating a branching tree that adapts to what they find.

### 2. Agent Lifecycle

```
1. Task Created → Queue
2. Agent Spawned in tmux session
3. Agent receives:
   - Phase instructions
   - Task description
   - Available MCP tools
   - RAG context from Qdrant
4. Agent works in isolated worktree
5. Agent creates new tasks as needed
6. Agent updates task status (done/failed)
7. tmux session closes
```

**Agent Isolation:**
- Each agent runs in separate tmux session
- Uses git worktrees for parallel work
- Has own working directory
- Communicates via MCP server

### 3. Task Queue & Coordination

**Queue Service** (`src/core/queue_service.py`):
- Stores tasks in SQLite database
- Prioritizes by: priority → phase → creation time
- Assigns tasks to available agents
- Tracks task dependencies and blocking

**Kanban Tickets** (optional):
- Visual coordination via board UI
- Tickets represent work items
- Move through columns: Backlog → Building → Testing → Done
- Support blocking relationships

### 4. Guardian Monitoring

**Guardian** (`src/monitoring/guardian.py`):
- Monitors agents every 60 seconds (configurable)
- Analyzes trajectory against phase instructions
- Calculates coherence score (0-1)
- Steers agents if drifting (<70% coherence)
- Prevents orphaned sessions

**Steering Example:**
```python
if coherence < 0.7:
    guardian.inject_message(
        agent_id,
        "⚠️ You're deviating from Phase 2 implementation focus. 
        Please complete the authentication module first."
    )
```

### 5. Memory System (RAG)

**Qdrant Vector Store:**
- Stores agent discoveries and learnings
- Semantic search for relevant context
- Memory types: error_fix, discovery, decision, learning
- Automatically retrieved for new tasks

**Workflow:**
1. Agent discovers solution/pattern
2. Saves to memory via MCP `save_memory` tool
3. Future agents query Qdrant for relevant context
4. System provides top-k most relevant memories

### 6. MCP Server Architecture

**FastAPI Server** (`src/mcp/server.py`):
- REST API on port 8000
- Tools exposed via MCP protocol
- Authentication via agent ID headers
- Endpoints:
  - `/create_task` - Spawn new task
  - `/update_task_status` - Mark done/failed
  - `/save_memory` - Store discovery
  - `/api/tickets/*` - Kanban operations
  - `/broadcast_message` - Agent communication

**MCP Clients:**
- `claude_mcp_client.py` - Hephaestus tools for Claude Code
- `qdrant_mcp_openai.py` - Qdrant semantic search

### 7. LLM Configuration

**Multi-provider support** via `src/core/llm_interface.py`:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- OpenRouter (Cerebras, others)
- Azure OpenAI
- Google AI Studio

**Recommended setup:**
```yaml
llm:
  embedding_model: "text-embedding-3-large"  # OpenAI
  primary_llm:
    provider: "openrouter"
    model: "gpt-oss:120b"  # Cerebras - 1000+ tokens/sec
```

## Workflow Example: Building from PRD

**User provides:** PRD.md describing a task management app

**Phase 1 Agent:**
1. Reads PRD
2. Identifies 5 components: Auth, API, Frontend, Database, Workers
3. Creates 5 Phase 2 tasks (one per component)

**Phase 2 Agents (parallel):**
- Agent A: Builds authentication module
- Agent B: Builds REST API
- Agent C: Builds React frontend
- Agent D: Designs database schema
- Agent E: Creates background workers

**Phase 2 Agent B (API):**
1. Completes API implementation
2. Spawns Phase 3 validation task: "Test REST API endpoints"

**Phase 3 Agent:**
1. Tests API endpoints
2. Discovers: "Auth caching pattern is excellent!"
3. Spawns Phase 1 investigation: "Analyze auth caching for reuse"

**New Phase 1 Agent:**
1. Studies auth caching implementation
2. Confirms it's reusable
3. Spawns Phase 2 task: "Apply caching to all API routes"

**Result:** Workflow branched itself based on discovery!

## Key Technologies

### Backend
- **Python 3.10+** - Core language
- **FastAPI** - MCP server framework
- **SQLAlchemy** - Database ORM
- **Qdrant** - Vector database for RAG
- **OpenAI/Anthropic** - LLM APIs

### Frontend
- **React** - UI framework
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **TypeScript** - Type safety

### Infrastructure
- **tmux** - Agent isolation
- **Git worktrees** - Parallel work isolation
- **Docker** - Qdrant deployment
- **SQLite** - Workflow state storage

## Configuration Files

### `hephaestus_config.yaml`
Main configuration file:
```yaml
paths:
  project_root: "/path/to/project"
  
git:
  main_repo_path: "/path/to/project"
  
llm:
  embedding_model: "text-embedding-3-large"
  primary_llm:
    provider: "openrouter"
    model: "gpt-oss:120b"
    
monitoring:
  enable_steering: true
  steering_threshold: 0.7
```

### `.env`
API keys and secrets:
```bash
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=sk-or-v1-...
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_PATH=./hephaestus.db
QDRANT_URL=http://localhost:6333
```

## Data Flow

```
User creates initial task
       ↓
Task added to queue (SQLite)
       ↓
Agent Manager spawns tmux session
       ↓
Agent queries Qdrant for context
       ↓
Agent receives phase instructions + task
       ↓
Agent works in git worktree
       ↓
Agent discovers new work needed
       ↓
Agent creates new task via MCP
       ↓
Agent saves discoveries to Qdrant
       ↓
Agent updates task status
       ↓
Guardian monitors trajectory
       ↓
(Loop continues until workflow complete)
```

## Testing Strategy

**Test Categories:**
- **Unit tests** - Individual components
- **Integration tests** - System interactions
- **MCP integration tests** - Protocol flows
- **SDK tests** - Public SDK interface

**Running tests:**
```bash
# All tests
python tests/run_all_tests.py

# Quick smoke tests
python tests/run_all_tests.py --quick

# Specific test
python tests/test_vector_store.py
```

## Development Workflow

**Starting development:**
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialize database
python scripts/init_db.py

# 3. Start Qdrant
docker run -d -p 6333:6333 qdrant/qdrant

# 4. Initialize Qdrant collections
python scripts/init_qdrant.py

# 5. Configure MCP servers
claude mcp add hephaestus "python -m src.mcp.server"
claude mcp add qdrant "python qdrant_mcp_openai.py"

# 6. Start backend
python run_server.py

# 7. Start monitor (separate terminal)
python run_monitor.py

# 8. Start frontend (separate terminal)
cd frontend && npm install && npm run dev
```

**Running a workflow:**
```bash
# Example workflow
python run_example.py

# SWEBench solver
python run_swebench_workflow.py --path ./workspace --instance-id astropy__astropy-14365
```

## Extension Points

### Adding Custom Phases
Create phase definitions in `example_workflows/`:
```python
from src.phases.phase import Phase

custom_phases = [
    Phase(
        id=1,
        name="Research",
        instructions="...",
        done_definition="...",
    ),
    # ... more phases
]
```

### Adding Custom Sub-Agents
Create markdown files in `.claude/agents/`:
```markdown
# Senior Python Engineer

You are an expert Python developer specializing in...

## Your Responsibilities
1. Write clean, maintainable code
2. Follow PEP 8 style guide
...
```

### Custom Workflow Configuration
```python
from src.sdk import HephaestusSDK

sdk = HephaestusSDK(
    phases=custom_phases,
    workflow_config={
        "enable_tickets": True,
        "board_config": {...},
        "result_validation": {...},
    },
    monitoring_interval=60,
    max_concurrent_agents=5,
)
```

## Performance Considerations

**Optimization tips:**
1. Use OpenRouter with Cerebras for 10x faster responses
2. Limit concurrent agents based on machine resources
3. Clean Qdrant periodically with `scripts/clean_qdrant.py`
4. Monitor tmux session count
5. Use git worktrees instead of cloning

**Resource usage:**
- Each agent: ~200-500MB RAM
- Qdrant: ~1-2GB RAM
- SQLite: Minimal
- Frontend: ~100MB

## Security Considerations

**Best practices:**
1. Never commit API keys to git
2. Use `.env` for secrets
3. Validate agent authorization
4. Sanitize user inputs
5. Limit agent file system access
6. Review generated code before deployment

## Getting Help

**Documentation:**
- Quick Start: `website/docs/getting-started/quick-start.md`
- Troubleshooting: `website/docs/troubleshooting/common-errors.md`
- API Reference: `website/docs/api/`

**Community:**
- Discord: https://discord.gg/FyrC4fpS
- GitHub Discussions: https://github.com/Ido-Levi/Hephaestus/discussions
- Issue Tracker: https://github.com/Ido-Levi/Hephaestus/issues

**Validation:**
```bash
python check_setup_macos.py
```

## License

AGPL-3.0 - See LICENSE file for details.

---

**Hephaestus: Where workflows forge themselves**

*Named after the Greek god of the forge, Hephaestus creates a system where agents craft the workflow as they work.*
