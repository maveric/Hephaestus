# Hephaestus Architecture

## System Design Philosophy

Hephaestus implements a **semi-structured agentic framework** that balances structure with flexibility:

- **Structured:** Phase types, task queue, monitoring
- **Flexible:** Agents dynamically create tasks based on discoveries
- **Adaptive:** Workflow builds itself as agents explore

## High-Level Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    User / SDK Client                        │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│              Hephaestus MCP Server (FastAPI)               │
│  - Task Creation & Management                              │
│  - Agent Authentication & Authorization                    │
│  - Ticket Tracking & Kanban Board                         │
│  - Memory & RAG Operations                                │
│  - Agent Communication                                     │
└────────┬───────────────────────┬───────────────────────────┘
         │                       │
         ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│   SQLite DB      │    │  Qdrant Vector   │
│   - Workflows    │    │  - Agent Memory  │
│   - Tasks        │    │  - Discoveries   │
│   - Agents       │    │  - Learnings     │
│   - Tickets      │    │  - Embeddings    │
└──────────────────┘    └──────────────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
         ┌───────────────────────┐
         │   Queue Service       │
         │   - Task Prioritize   │
         │   - Agent Assign      │
         │   - Dependency Track  │
         └───────────┬───────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│  Agent Manager   │    │ Guardian Monitor │
│  - Spawn agents  │    │ - Coherence     │
│  - tmux control  │    │ - Steering      │
│  - Worktree mgmt │    │ - Cleanup       │
└────────┬─────────┘    └──────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────┐
│                    Agent Pool (tmux sessions)              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │  Agent 1    │  │  Agent 2    │  │  Agent 3    │      │
│  │  Phase 1    │  │  Phase 2    │  │  Phase 3    │      │
│  │  + MCP      │  │  + MCP      │  │  + MCP      │      │
│  │  + Worktree │  │  + Worktree │  │  + Worktree │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. MCP Server (`src/mcp/server.py`)

**Purpose:** Central API for all agent operations

**Key Endpoints:**
- `POST /create_task` - Create new task
- `POST /update_task_status` - Update task state
- `POST /save_memory` - Store discovery to Qdrant
- `GET /task_progress` - Query task status
- `POST /api/tickets/*` - Kanban operations
- `POST /broadcast_message` - Inter-agent communication

**Design Decisions:**
- Uses FastAPI for async performance
- Agent authentication via `X-Agent-ID` header
- JSON payload validation with Pydantic
- CORS enabled for frontend access

### 2. Queue Service (`src/core/queue_service.py`)

**Purpose:** Task prioritization and agent assignment

**Algorithm:**
```python
Priority = (
    task.priority_weight * 100 +  # high=3, medium=2, low=1
    phase.id * 10 +                # Earlier phases first
    -created_timestamp             # Older tasks first
)
```

**State Machine:**
```
pending → assigned → in_progress → (done | failed)
                          ↓
                     blocked_on_validation
```

### 3. Agent Manager (`src/agents/agent_manager.py`)

**Purpose:** Spawn and manage agent lifecycle

**Spawning Process:**
1. Create git worktree for isolation
2. Generate agent prompt with:
   - Phase instructions
   - Task description
   - Available tools (MCP)
   - RAG context
3. Spawn tmux session
4. Execute CLI tool (claude/opencode)
5. Register agent in database

**Worktree Isolation:**
```
main_repo/
  └─ main branch

worktrees/
  ├─ agent-abc123/  ← Agent 1 isolated workspace
  ├─ agent-def456/  ← Agent 2 isolated workspace
  └─ agent-ghi789/  ← Agent 3 isolated workspace
```

### 4. Guardian Monitor (`src/monitoring/guardian.py`)

**Purpose:** Ensure agents stay aligned with phase goals

**Monitoring Loop:**
```python
Every 60 seconds:
  1. Fetch all active agents
  2. Get agent output from tmux buffer
  3. Analyze trajectory vs phase instructions (LLM)
  4. Calculate coherence score (0-1)
  5. If score < threshold (0.7):
     - Generate steering message
     - Inject into agent's tmux session
  6. Detect orphaned sessions → cleanup
```

**Coherence Analysis:**
```
LLM Prompt:
  - Phase instructions: "Must implement auth module"
  - Agent output: "Working on database schema..."
  - Question: Is agent following phase guidelines?
  
LLM Response:
  - Coherence: 0.4 (low)
  - Reasoning: "Agent should focus on auth, not database"
  - Recommendation: "Redirect to auth implementation"
```

### 5. Memory System (`src/memory/rag_system.py`)

**Purpose:** Store and retrieve agent discoveries

**Qdrant Collections:**
- `hephaestus_agent_memories` (3072-dim embeddings)

**Memory Types:**
- `error_fix` - Bug fixes and solutions
- `discovery` - New patterns or approaches
- `decision` - Architectural decisions
- `learning` - General learnings
- `codebase_knowledge` - Project-specific knowledge

**Retrieval:**
```python
# Agent queries for context
relevant_memories = rag_system.search(
    query="How to implement JWT authentication?",
    limit=5,
    min_score=0.7
)
# Returns top-5 semantically similar memories
```

### 6. Phase System (`src/phases/`)

**Purpose:** Define workflow structure

**Phase Definition:**
```python
Phase(
    id=1,
    name="Investigation",
    instructions="""
    MANDATORY STEPS:
    1. Reproduce the issue
    2. Identify root cause
    3. Document findings
    
    SUCCESS CRITERIA:
    - Issue is reproducible
    - Root cause identified
    """,
    done_definition="Issue reproduced and documented",
    allowed_tools=["file_read", "shell_exec"],
)
```

**Phase Progression:**
- Agents can create tasks in ANY phase
- Creates branching workflow tree
- No fixed sequence enforced

### 7. Ticket System (`src/services/ticket_service.py`)

**Purpose:** Visual coordination via Kanban board

**Board Structure:**
```yaml
columns:
  - id: backlog
    name: Backlog
    order: 0
  - id: in_progress
    name: In Progress
    order: 1
  - id: review
    name: Review
    order: 2
  - id: done
    name: Done
    order: 3
```

**Blocking Relationships:**
```
Ticket A (Frontend)
  ↓ blocked_by
Ticket B (API) ← Must complete first
  ↓ blocked_by
Ticket C (Database) ← Must complete first
```

## Data Models

### Task
```python
class Task:
    id: str                    # UUID
    description: str           # What to do
    phase_id: int             # Which phase
    status: str               # pending/assigned/in_progress/done/failed
    priority: str             # low/medium/high
    agent_id: Optional[str]   # Assigned agent
    created_at: datetime
    ticket_id: Optional[str]  # Optional Kanban ticket
```

### Agent
```python
class Agent:
    id: str                   # UUID
    status: str              # idle/working/terminated
    current_task_id: str     # Active task
    cli_type: str            # claude/opencode/droid/codex
    tmux_session_name: str   # Session identifier
    phase_id: int            # Current phase
    created_at: datetime
```

### Ticket
```python
class Ticket:
    id: str                      # ticket-UUID
    title: str                   # Short description
    description: str             # Detailed info
    status: str                  # Column in board
    ticket_type: str             # bug/feature/task
    priority: str                # low/medium/high/critical
    blocked_by_ticket_ids: List[str]  # Dependencies
    is_blocked: bool             # Computed field
    tags: List[str]              # Categorization
```

## Security Model

### Authentication
- Agent ID passed in `X-Agent-ID` header
- Validated against database
- Each tool call requires valid agent ID

### Authorization
- Agents can only update their own tasks
- No cross-agent task modification
- Tickets require agent ownership or permission

### Isolation
- Agents run in separate tmux sessions
- Git worktrees prevent conflicts
- File system access limited to worktree

## Performance Optimizations

### Database
- Indexes on frequently queried fields
- Connection pooling
- Lazy loading of relationships

### Qdrant
- Batch embedding generation
- Filtered search to reduce candidates
- HNSW index for fast approximate search

### Agent Spawning
- Worktrees instead of full clones (10x faster)
- Reusable prompt templates
- Async MCP operations

### LLM Calls
- OpenRouter with Cerebras (1000+ tokens/sec)
- Prompt caching where applicable
- Batch operations when possible

## Scalability Considerations

**Current Limits:**
- Max concurrent agents: 5-10 (configurable)
- Database: SQLite (single file)
- Qdrant: Single instance

**Scaling Path:**
- Replace SQLite with PostgreSQL
- Distribute Qdrant across nodes
- Horizontal scaling of agents
- Load balance MCP servers

## Monitoring & Observability

**Logging:**
```
logs/
  ├── backend.log    # MCP server logs
  ├── monitor.log    # Guardian logs
  └── agent-*.log    # Per-agent logs (tmux buffers)
```

**Metrics:**
- Task completion rate
- Agent utilization
- Coherence scores over time
- Memory growth rate

**Debugging:**
```bash
# View agent in action
tmux attach -t agent-abc123

# Query database
sqlite3 hephaestus.db "SELECT * FROM tasks WHERE status='in_progress'"

# Check Qdrant
curl http://localhost:6333/collections/hephaestus_agent_memories
```

## Extension Points

### Custom Phases
Implement `Phase` class with custom logic

### Custom Agents
Define sub-agent behaviors in `.claude/agents/`

### Custom Monitoring
Extend `Guardian` class with additional checks

### Custom Tools
Add new MCP endpoints in `src/mcp/routes/`

### Custom LLM Providers
Implement provider in `src/core/llm_interface.py`

## Design Principles

1. **Semi-Structure:** Enough structure to coordinate, enough flexibility to adapt
2. **Agent Autonomy:** Agents decide what tasks to create
3. **Transparency:** All operations logged and traceable
4. **Isolation:** Agents can't interfere with each other
5. **Observability:** Real-time visibility into workflow state
6. **Extensibility:** Easy to add new phases, tools, providers

## Technology Choices

**Why tmux?**
- Lightweight process isolation
- Interactive session management
- Easy to attach for debugging
- Cross-platform support

**Why SQLite?**
- Zero-configuration
- ACID compliance
- Fast for small-medium datasets
- Easy backup (single file)

**Why Qdrant?**
- Built for vector search
- Easy Docker deployment
- Good performance/cost ratio
- Rich filtering capabilities

**Why FastAPI?**
- Async support out of box
- Auto-generated OpenAPI docs
- Pydantic validation
- WebSocket support (future)

## Future Architecture Plans

**Planned Improvements:**
1. WebSocket for real-time agent updates
2. Distributed task queue (Redis/RabbitMQ)
3. Multi-tenant support
4. Workflow templates marketplace
5. Agent performance analytics
6. Cost tracking per workflow

## References

- [Phase System Guide](website/docs/guides/phases-system.md)
- [Guardian Monitoring](website/docs/guides/guardian-monitoring.md)
- [Ticket Tracking](website/docs/guides/ticket-tracking.md)
- [Memory System](website/docs/core/memory-system.md)
- [Queue Management](website/docs/core/queue-and-task-management.md)
