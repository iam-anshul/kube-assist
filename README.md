# Kube-Assist

**An AI agent for Kubernetes operations.** Chat with your cluster in natural language — Kube-Assist deploys workloads, debugs failures, and manages resources by running `kubectl` for you, with human-in-the-loop approval for anything destructive.

> ⚠️ **Status: active development.** Not production-ready yet — see [Roadmap](#roadmap).

## What it does

- **Deploy** — describe what you want ("run nginx with 2 replicas and expose it on port 80") and the agent generates the manifests and applies them.
- **Debug** — ask why a pod is crashing; the agent inspects events, logs, and resource states across the cluster to find the cause.
- **Manage** — day-to-day operations (scaling, restarts, inspecting resources) through conversation instead of memorized `kubectl` incantations.

## How it works

```
User ──▶ FastAPI backend ──▶ Kubernetes Agent (pydantic-ai + Claude)
                │                       │
                │                       ▼ tool call
                │              run_kubectl_command()
                │              (per-project kubeconfig + AWS creds)
                │                       │
                ◀── streamed response ──┘
                │
                ▼
        Summarizer Agent (compresses chat history
        to keep long sessions cheap)
```

1. **Agent core** — a [pydantic-ai](https://ai.pydantic.dev/) `Agent` backed by Anthropic Claude (an OpenAI-backed variant is also included). Its single tool is `run_command`, which executes `kubectl` against the user's cluster.
2. **Safety model** — read/describe operations run freely; **create, update, and delete operations require explicit user permission** before the agent executes them. The system prompt also instructs the agent to reason about blast radius on a live cluster and surface risks to the user.
3. **Summarizer agent** — a second agent watches conversation length and compresses history (sliding-window style, dropping resolved topics) so long debugging sessions don't blow up token costs. It returns a structured verdict (`summary`, `summarisation_required`) via a Pydantic response model.
4. **Multi-tenancy** — users authenticate via [SuperTokens](https://supertokens.com/) (email/password + sessions). Each user has **projects**; each project stores its own cloud credentials and gets its own kubeconfig, generated server-side with `aws eks update-kubeconfig`. Chats, message history, and background task status are persisted per project.
5. **Streaming** — `POST /run-agent` kicks off the agent as a background task and returns a `run_id`; `GET /stream-response` streams the agent's output line-by-line from an async queue as it's produced.

## Tech stack

| Layer | Technology |
|---|---|
| Agent framework | pydantic-ai (Anthropic Claude / OpenAI) |
| API | FastAPI + Uvicorn |
| Auth | SuperTokens (email/password, sessions) |
| Database | PostgreSQL, SQLAlchemy ORM, Alembic migrations |
| Cluster access | kubectl + AWS CLI v2 (bundled in the Docker image), EKS kubeconfig generation |
| Deployment | Docker, docker-compose, GitHub Actions → ECR → DigitalOcean |

## API surface

| Endpoint | Purpose |
|---|---|
| `POST /create-chat` | Create a chat under a project |
| `GET /get-user-chats` | List the user's chats |
| `GET /get-chat` | Fetch a conversation |
| `POST /run-agent` | Run the agent on a message (returns `run_id`) |
| `GET /stream-response` | Stream the agent's output for a `run_id` |
| `/projects/*` | Project CRUD |
| `/kubeconfig/*` | Store cloud credentials, generate EKS kubeconfig |
| `/tasks/*` | Background task status |

Interactive OpenAPI docs are served behind basic auth at `/docs`.

## Getting started

### Prerequisites

- Python 3.12
- PostgreSQL
- A [SuperTokens](https://supertokens.com/) core (managed or self-hosted)
- An Anthropic API key
- AWS credentials with EKS access for the target cluster

### Environment variables

Create a `.env` in `kube-assist-backend/`:

```env
ANTHRIPIC_API_KEY=sk-ant-...          # note: current env var name as spelled in code
DATABASE_CONNECTION_STRING=postgresql://user:pass@host:5432/kubeassist
SUPERTOKENS_CONNECTION_URL=https://...
SUPERTOKENS_API_KEY=...
```

### Run locally

```bash
cd kube-assist-backend
pip install -r ../requirements.txt
alembic upgrade head
python main.py            # serves on :8000
```

### Run with Docker

The image bundles `kubectl` and AWS CLI v2 so the agent can talk to EKS out of the box:

```bash
docker build -t kube-assist .          # Dockerfile.arm for ARM hosts
docker run --env-file kube-assist-backend/.env -p 8000:8000 kube-assist
```

### Deployment

Pushes to `main` that touch `kube-assist-backend/` trigger a GitHub Actions workflow that builds the image, pushes it to ECR, and deploys to a DigitalOcean server over SSH.

## Project structure

```
kube-assist-backend/
├── main.py                          # FastAPI app, SuperTokens init, routers
├── source/
│   ├── kubernetes_agent_anthropic.py  # Claude-backed agent + kubectl tool
│   ├── kubernetes_agent_openai.py     # OpenAI-backed variant
│   ├── summarise_agent.py             # History-compression agent
│   ├── system_prompts.py              # Agent behavior + safety rules
│   ├── command.py                     # kubectl execution with per-project creds
│   ├── routes/                        # chat, projects, kubeconfig, tasks, admin
│   └── database/                      # SQLAlchemy models + session management
└── alembic/                           # Migrations
```

## Roadmap

- [ ] Frontend chat UI
- [ ] Harden command execution (allow-listing, no shell interpolation)
- [ ] Secrets management for cloud credentials at rest
- [ ] Support for non-EKS clusters (GKE, AKS, bare kubeconfig upload)
- [ ] Multi-model configuration via environment

## License

MIT