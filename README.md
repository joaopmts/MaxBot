# Tennis Court Reservation Bot

Automated bot for booking tennis courts, built with Python and Playwright, packaged in Docker. Designed to be scheduled via **Synology Task Scheduler** on a NAS.

## Overview

On each run, the bot performs the following actions automatically:

- Logs into the booking website
- Calculates the next Friday and selects the date
- Books two consecutive time slots: **07:00** and **08:00**
- Adds an additional player to each reservation
- Saves confirmation screenshots to `/screenshots`

---

## Project Structure

```
.
├── reserva_final.py        # Main automation script
├── Dockerfile              # Docker image with Playwright
├── docker-compose.yml      # Service configuration
├── .env                    # Credentials (do not commit)
└── screenshots/            # Confirmation screenshots saved here
```

---

## Requirements

- Docker and Docker Compose installed
- A valid account on the booking website

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/joaopmts/MaxBot
cd MaxBot
```

### 2. Create the `.env` file

```env
TENNIS_EMAIL=your_email@example.com
TENNIS_SENHA=your_password
```

> Never commit this file. It contains your login credentials.

### 3. Create the screenshots folder

```bash
mkdir screenshots
```

### 4. Run

With Docker Compose:

```bash
docker compose up --build
```

Or directly with Docker:

```bash
docker build -t reserva-tenis .
docker run --env-file .env -v $(pwd)/screenshots:/app/screenshots reserva-tenis
```

---

## Scheduling on a Synology NAS

To run the bot automatically every week:

1. Open DSM and go to **Control Panel > Task Scheduler**
2. Create a new task of type **User-defined script**
3. Set the trigger to run weekly (e.g. every Thursday morning, to book Friday slots)
4. In the script field, enter:

```bash
cd /volume1/path/to/project && docker compose up --build
```

> Adjust the path to match where the project is stored on your NAS.

---

## Tech Stack

| Technology    | Purpose                          |
|---------------|----------------------------------|
| Python 3      | Main language                    |
| Playwright    | Browser automation               |
| Docker        | Packaging and isolated execution |
| python-dotenv | Credential management via .env   |

---

## Security

Credentials are loaded exclusively from environment variables via the `.env` file.

- Never commit `.env` to version control
- Add the following to your `.gitignore`:

```
.env
screenshots/
```

---

## Troubleshooting

**Bot fails to find the slot or court:** The website layout may have changed. Check the CSS selectors and aria-labels in `reserva_final.py`.

**Screenshots not saved:** Make sure the `screenshots/` folder exists and the volume is mounted correctly in Docker.

**Task not running on NAS:** Verify the project path in the scheduler script and check the DSM logs for error details.

**Login error:** Double-check that `TENNIS_EMAIL` and `TENNIS_SENHA` in your `.env` file are correct and have no extra spaces.
