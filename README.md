# Project: Seasonal Point Tracker Bot

This project provides a complete, containerized application ecosystem for running a seasonal, points-based tracking system via a Discord bot. It's designed for communities, such as gaming guilds, that want to reward members for participating in activities over a set period (a "season").

The system is built around a powerful backend API and a user-friendly Discord bot that handles all user interaction.

## Core Features

- **User Registration & Verification:** Users register with the bot, and an admin must verify them before they can participate.
- **Seasonal Gameplay:** Admins can create seasons with a defined start and end date.
- **Points System:** Users make "submissions" (e.g., of in-game items) via the bot, which are translated into points for the current season.
- **Ranks & Prizes:** Users can achieve ranks by reaching point thresholds within a season, earning them prizes like special Discord roles.
- **Admin Management:** A "root admin" is defined for initial setup, with the ability to grant admin privileges to other verified users.
- **Optional Direct API Access:** Approved users can be granted direct, programmatic access to the API via secure JWTs.

---

## Technology & Architecture

The application uses a modern, microservice-inspired architecture, with each component running in its own isolated Docker container.

- **Orchestration:** Docker & Docker Compose
- **Reverse Proxy / SSL:** Caddy Server (for automatic HTTPS)
- **Backend API:** Python with FastAPI
- **Database ORM:** SQLAlchemy (with `asyncio` support)
- **Database:** MariaDB
- **Discord Bot:** Python (using `py-cord`)
- **Networking:** A DDNS service (like DuckDNS) is used to give the server a stable domain name.

---

## Setup Instructions

Follow these steps to get the entire application stack running.

### 1. Prerequisites

You must have **Docker** and **Docker Compose** installed on your hosting machine.

### 2. Create Configuration Files

This project uses `.env.example` files as templates. You must copy each one and rename it (removing the `.example` suffix), then fill in your own secrets. The application will not start without these files.

1.  Copy `.env.db.example` to **`.env.db`**
2.  Copy `.env.api.example` to **`.env.api`**
3.  Copy `.env.bot.example` to **`.env.bot`**

### 3. Fill in Environment Variables

Now, open the newly created `.env` files and add your specific values.

**In `.env.db`:**

MariaDB credentials

MARIADB_ROOT_PASSWORD=your_super_secret_root_password
MARIADB_DATABASE=app_db
MARIADB_USER=app_user
MARIADB_PASSWORD=your_secret_db_password

**In `.env.api`:**

API configuration

Use the mysql+asyncmy driver format for SQLAlchemy

DATABASE_URL=mysql+asyncmy://app_user:your_secret_db_password@db:3306/app_db
BOT_API_KEY=generate_a_very_long_and_random_secret_string_here
JWT_SECRET_KEY=generate_another_separate_secret_string_for_jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200 # 30 days

> **Note:** The `BOT_API_KEY` and `JWT_SECRET_KEY` should be long, random, and completely different from each other.

**In `.env.bot`:**

Bot configuration

DISCORD*BOT_TOKEN=your_discord_bot_token_from_developer_portal
ROOT_ADMIN_ID=your_personal_discord_user_id
API_URL=https://your-domain.duckdns.org
BOT_API_KEY=use_the_same_long_secret_string_as_in*.env.api

### 4. Configure the Web Server

Open the `Caddyfile` and replace the placeholder domain with your actual DDNS domain.

Replace with your domain

your-domain.duckdns.org {
reverse_proxy api:8000
}

### 5. Build and Run the Application

With all your configuration files in place, you can now launch the entire stack with a single command:

```bash
docker-compose up --build
```

This command will:

    Pull the base images for MariaDB and Caddy.

    Build the custom Docker images for your API and Bot.

    Create the Docker network and volumes.

    Start all four containers in the correct order.

To run the stack in the background (detached mode), use:

```bash
docker-compose up --build -d
```
