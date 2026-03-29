# nlops

Natural language infrastructure management. Talk to your servers.

## what it does

nlops lets you manage Docker containers and remote servers using plain English. Instead of context-switching between CLIs, dashboards, and docs, you just type what you want.

```
> restart my nginx container
> show me disk usage on the server
> what containers are running?
> pull the latest postgres image
> check memory usage
```

## stack

- **Backend** — FastAPI + LangChain + Ollama (or Claude API)
- **Frontend** — React + Vite
- **Discord bot** — discord.py
- **Tools** — Docker SDK, Paramiko (SSH), Proxmox API

## setup

### requirements

- Python 3.11+
- Node 18+
- Docker
- Ollama running locally (`ollama pull qwen2.5:7b`)

### install

```bash
# backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# fill in your .env
```

```bash
# frontend
cd frontend
npm install
```

### config

```env
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen2.5:7b

SSH_HOST=your-server-ip
SSH_USER=your-username
SSH_PASSWORD=yourpassword

# optional
PROXMOX_HOST=your-proxmox-ip
PROXMOX_USER=root@pam
PROXMOX_PASSWORD=yourpassword

DISCORD_TOKEN=your-discord-token
```

### run

```bash
# backend
cd backend
uvicorn main:app --reload

# frontend
cd frontend
npm run dev

# discord bot (optional)
cd backend
python bot.py
```

Open [http://localhost:5173](http://localhost:5173)

## tools

| category | tools |
|----------|-------|
| docker | list containers, start/stop/restart, get logs, stats, list images, pull image, run container |
| ssh | run command, disk usage, memory, top processes, public IP |
| system | ping host, systemctl status/restart, git pull, nginx reload |
| proxmox | list/start/stop/restart VMs, VM status, list nodes |

## discord

Add the bot to your server and use `/ops` to run commands:

```
/ops list my containers
/ops restart nginx
/ops check disk usage
```

The bot status updates every 30 seconds with live CPU, RAM, and disk stats from your server.

## project structure

```
nlops/
├── backend/
│   ├── main.py          # FastAPI server
│   ├── agent.py         # LangChain agent loop
│   ├── bot.py           # Discord bot
│   ├── tools/
│   │   ├── docker_tools.py
│   │   ├── ssh_tools.py
│   │   └── proxmox_tools.py
│   ├── .env.example
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   └── App.css
    └── package.json
```