# xCrape

Monitors Twitter/X for keywords and sends matching tweets to a Telegram channel. Runs on a configurable schedule, deduplicates across runs, and enriches notifications with author metadata.

---

## Prerequisites

### Installing Docker Desktop

Docker Desktop bundles everything needed — Docker Engine, Docker Compose, and it will automatically pull the PostgreSQL image when you run the project. You do **not** need to install PostgreSQL separately.

#### Windows

1. Download **Docker Desktop for Windows** from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
2. Run the installer (`Docker Desktop Installer.exe`) and follow the prompts
3. When asked, enable **WSL 2** (recommended) — if prompted to install WSL 2, open PowerShell as Administrator and run:

   ```powershell
   wsl --install
   ```

   Then restart your machine.

4. After installation, launch **Docker Desktop** from the Start menu and wait for it to show "Docker Desktop is running" in the system tray
5. Verify it works:

   ```cmd
   docker --version
   docker compose version
   ```

> **Troubleshooting:** If Docker Desktop fails to start, make sure virtualisation is enabled in your BIOS (look for "Intel VT-x" or "AMD-V") and that Hyper-V or WSL 2 features are turned on in Windows Features.

#### macOS

1. Download **Docker Desktop for Mac** from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) — pick the right chip (Apple Silicon vs Intel)
2. Open the `.dmg` and drag Docker to Applications
3. Launch Docker from Applications and follow the onboarding prompts
4. Verify it works:

   ```bash
   docker --version
   docker compose version
   ```

> **Alternative via Homebrew:** `brew install --cask docker`

---

### What about PostgreSQL?

**You do not need to install PostgreSQL manually.** When you run `docker compose up`, Docker automatically downloads and starts a PostgreSQL 16 container. The database, user, and password are all configured in `docker-compose.yml`.

---

### Manual PostgreSQL installation (without Docker)

Only needed if you are running xCrape on a server without Docker.

#### Windows (manual PostgreSQL)

1. Download the installer from [postgresql.org/download/windows](https://www.postgresql.org/download/windows/)
2. Run the installer, set a password for the `postgres` superuser, and leave the port as `5432`
3. Open **pgAdmin** or **SQL Shell (psql)** from the Start menu and create the database:

   ```sql
   CREATE USER xcrape WITH PASSWORD 'secret';
   CREATE DATABASE xcrape OWNER xcrape;
   ```

4. Update `DATABASE_URL` in your `.env` to use `localhost` instead of `db`:

   ```text
   DATABASE_URL=postgresql+asyncpg://xcrape:secret@localhost:5432/xcrape
   ```

#### macOS (manual PostgreSQL)

1. Install via Homebrew:

   ```bash
   brew install postgresql@16
   brew services start postgresql@16
   ```

2. Create the database:

   ```bash
   psql postgres -c "CREATE USER xcrape WITH PASSWORD 'secret';"
   psql postgres -c "CREATE DATABASE xcrape OWNER xcrape;"
   ```

3. Update `DATABASE_URL` in your `.env`:

   ```text
   DATABASE_URL=postgresql+asyncpg://xcrape:secret@localhost:5432/xcrape
   ```

4. Run migrations manually (requires Python + dependencies installed):

   ```bash
   alembic upgrade head
   ```

---

### Installing Git

| Platform | Steps                                                                              |
|----------|------------------------------------------------------------------------------------|
| Windows  | Download from [git-scm.com](https://git-scm.com) and run the installer            |
| macOS    | `brew install git` or `xcode-select --install` for Xcode Command Line Tools       |

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

Copy the example file and fill in your credentials.

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
| --- | --- | --- |
| `DATABASE_URL` | Postgres connection string — use `db` as host (Docker service name) | `postgresql+asyncpg://xcrape:secret@db:5432/xcrape` |
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

| Action               | Command                                                    |
|----------------------|------------------------------------------------------------|
| Start (background)   | `docker compose up -d --build`                             |
| Stop                 | `docker compose down`                                      |
| View logs            | `docker compose logs -f app`                               |
| Rebuild from scratch | `docker compose build --no-cache`                          |
| Reset database       | `docker compose down -v` then `docker compose up --build`  |

---

## Project structure

```text
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
