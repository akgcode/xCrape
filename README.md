# xCrape

Monitors Twitter/X for keywords and sends matching tweets to a Telegram channel. Runs on a configurable schedule, deduplicates across runs, and enriches notifications with author metadata.

---

## Prerequisites

| Tool | Windows | macOS |
|------|---------|-------|
| Docker Desktop | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) |
| Git | [git-scm.com](https://git-scm.com) | `brew install git` |

---

## Setup

### 1. Clone the repo

**Windows (Command Prompt / PowerShell)**
```cmd
git clone https://github.com/your-org/xcrape.git
cd xcrape
```

**macOS / Linux**
```bash
git clone https://github.com/your-org/xcrape.git
cd xcrape
```

---

### 2. Create your `.env` file

Copy the example file and fill in your credentials:

**Windows**
```cmd
copy .env.example .env
```

**macOS / Linux**
```bash
cp .env.example .env
```

Then open `.env` and set each value:

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Postgres connection string — use `db` as the host (Docker service name) | `postgresql+asyncpg://xcrape:secret@db:5432/xcrape` |
| `SCRAPEBADGER_API_KEY` | API key from [scrapebadger.com](https://scrapebadger.com) | `sb_live_xxxx` |
| `TELEGRAM_BOT_TOKEN` | Token from [@BotFather](https://t.me/BotFather) on Telegram | `123456:ABC-xxxx` |
| `TELEGRAM_CHAT_ID` | Channel username (with `@`) or numeric chat ID | `@myChannel` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |
| `CONFIG_PATH` | Path to the search config file | `config.yaml` |

> `.env` is listed in `.gitignore` and will never be committed. Never share or commit this file.

---

### 3. Configure keywords

Edit [`config.yaml`](config.yaml) to set what to monitor:

```yaml
search:
  query_type: "Top"   # Top | Latest | People | Photos | Videos
  count: 5            # tweets fetched per keyword per run
  keywords:
    - "gold crypto"
    - "gold mining"
    - "XAUUSD"

scheduler:
  interval_hours: 0.1  # how often to run (0.1 = every 6 minutes)
```

---

### 4. Build and run

**Windows (PowerShell) & macOS**
```bash
docker compose up --build
```

On first run this will:
1. Build the Docker image and install dependencies
2. Start a Postgres container
3. Run `alembic upgrade head` to create the database schema
4. Start the scheduler — tweets matching your keywords will be sent to Telegram

---

## Common Docker commands

| Action | Command |
|--------|---------|
| Start (background) | `docker compose up -d --build` |
| Stop | `docker compose down` |
| View logs | `docker compose logs -f app` |
| Rebuild from scratch | `docker compose build --no-cache` |
| Reset database | `docker compose down -v` then `docker compose up --build` |

---

## Project structure

```
xcrape/
├── src/xcrape/
│   ├── application/       # use cases and DTOs
│   ├── domain/            # entities, value objects, exceptions
│   ├── infrastructure/    # API clients, DB, scheduler
│   └── shared/            # config loader
├── alembic/               # database migrations
├── tests/                 # unit and integration tests
├── config.yaml            # keyword and scheduler config
├── .env.example           # template — copy to .env and fill in
└── docker-compose.yml
```
