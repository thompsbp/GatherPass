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

> **Note:** If you haven't already set up your Discord bot then please see the instructions below.

DISCORD_BOT_TOKEN=your_discord_bot_token_from_developer_portal
ROOT_ADMIN_ID=your_personal_discord_user_id
API_URL=https://your-domain.duckdns.org
BOT_API_KEY=use_the_same_long_secret_string_as_in\*.env.api

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

1. Pull the base images for MariaDB and Caddy.
2. Build the custom Docker images for your API and Bot.
3. Create the Docker network and volumes.
4. Start all four containers in the correct order.

To run the stack in the background (detached mode), use:

```bash
docker-compose up --build -d
```

## Discord Application & Bot Setup Guide

Follow these steps to create the Discord application, get the required credentials, and invite the bot to your server.

### 1. Create the Application

First, you need to create a new application in the Discord Developer Portal.

1.  Go to the [Discord Developer Portal](https://discord.com/developers/applications) and log in.
2.  Click the **New Application** button in the top-right corner.
3.  Give your application a name (e.g., "Seasonal Points Bot") and agree to the Discord Developer Terms of Service.
4.  Click **Create**. You'll be taken to your application's main page.

### 2. Create a Bot User and Get the Token

Now you'll add a bot user to the application and get the secret token it will use to log in.

1.  In the left-hand menu, click on the **Bot** tab.
2.  Click the **Add Bot** button. A confirmation pop-up will appear; click **Yes, do it!**.
3.  Under the bot's username, you'll see a section called **TOKEN**. Click the **Reset Token** button.
4.  **This is the only time you will be able to see the full token.** Click the **Copy** button to copy the token.
5.  Paste this token into your `.env.bot.example` file as the value for `DISCORD_BOT_TOKEN`. **Do not share this token with anyone.**

### 3. Configure Bot Permissions (Intents)

Your bot's code needs permission to access certain data from Discord. These are called "Gateway Intents."

1.  Still on the **Bot** page, scroll down to the **Privileged Gateway Intents** section.
2.  Enable the following two intents:
    - **PRESENCE INTENT** (Optional, but good for some features)
    - **SERVER MEMBERS INTENT** (Required for the bot to see member details like names and roles)
3.  Click **Save Changes**.

### 4. Invite the Bot to Your Server

Finally, you need to create an invitation link that grants the bot the correct permissions on your server.

1.  In the left-hand menu, click on the **OAuth2** tab, then select **URL Generator**.
2.  In the **SCOPES** box, check the following:
    - `bot`
    - `applications.commands`
3.  A new **BOT PERMISSIONS** box will appear below. Check the following permissions that your bot will need to function:
    - **Read Messages/View Channels**
    - **Send Messages**
    - **Send Messages in Threads**
    - **Embed Links**
    - **Attach Files**
    - **Manage Roles** (If you plan for the bot to award roles as prizes)
4.  Scroll down to the **Generated URL** box at the bottom of the page and click **Copy**.
5.  Paste this URL into your web browser, select the server you want to add the bot to from the dropdown menu, and click **Continue** and then **Authorize**.

The bot will now appear in your server's member list (likely offline). Once you start your `docker-compose` stack, it will log in and come online, ready to receive commands.
