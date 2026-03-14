Automated tennis court reservation bot for website, built with Python + Playwright running inside Docker. Designed to be scheduled via **Synology Task Scheduler** on a NAS.

What it does

- Automatically logs into the court booking website
- Calculates the next Friday and selects the date
- Books two consecutive time slots: **07:00** and **08:00**
- Adds an additional player to each reservation
- Saves screenshots of each booking confirmation under `/screenshots`

## Project structure

```
.
├── reserva_final.py       # Main automation script
├── Dockerfile             # Docker image with Playwright
├── docker-compose.yml     # Service configuration
├── .env                   # Credentials (do not commit!)
└── screenshots/           # Confirmation screenshots saved here
```

---

## Requirements

- Docker installed
- A valid account on website

---

## Getting started

### Clone the repository
### Create the `.env` file
### Create the screenshots folder
### Run with Docker Compose

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

To run the bot automatically every week, set up a task in **Synology Task Scheduler**:

1. Open **DSM** → Control Panel → **Task Scheduler**
2. Create a new task of type **User-defined script**
3. Set the trigger to your preferred day and time (e.g. every Thursday morning)
4. In the script field, enter:

```bash
cd /path/to/project && docker compose up --build
```

---

## Tech stack

| Technology | Purpose |
|---|---|
| Python 3 | Main language |
| Playwright | Browser automation |
| Docker | Packaging and execution |
| python-dotenv | Credentials management via `.env` |

---


## Security
- Credentials are loaded from environment variables via `.env`
- The `.env` file **must not** be committed to version control
- Add the following to your `.gitignore`:

```
.env
screenshots/
```
