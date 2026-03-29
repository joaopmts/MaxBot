# MaxBot — Tennis Court Reservation Bot

Automated bot for booking tennis courts, built with Python and Playwright, packaged in Docker. Designed to be scheduled via **Synology Task Scheduler** on a NAS.

## Overview

On each run, the bot performs the following actions automatically:

- Logs into the booking website
- Calculates the next Friday and selects the date
- Tries to book **Court 1 (Saibro 1)** at **07:00** and **08:00**
- If Court 1 is unavailable, falls back to **Court 3 (Saibro 3)**
- Adds an additional player (Rafaela Garcia) to each reservation
- If a slot is unavailable, reports **who booked it** in the log
- Saves confirmation screenshots to `/screenshots`
- Saves execution logs to `/logs`

---

## Booking Logic

```
Try Court 1 at 07:00
├── Success → Try Court 1 at 08:00 → Done
└── Fail → Try Court 3 at 07:00
            ├── Success → Try Court 3 at 08:00
            │             Log who booked Court 1
            └── Fail → Log who booked Court 1 and Court 3
```

---

## Project Structure

```
.
├── reserva_final.py        # Main automation script
├── Dockerfile              # Docker image with Playwright
├── docker-compose.yml      # Alternative local run configuration
├── .env                    # Credentials (do not commit)
├── screenshots/            # Confirmation screenshots saved here
└── logs/                   # Execution logs saved here
```

---

## Requirements

- Docker installed on the host (NAS or local machine)
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

### 3. Create the required folders

```bash
mkdir screenshots logs
```

### 4. Build the image

```bash
sudo docker build -t reserva-tenis .
```

### 5. Create the persistent container

```bash
sudo docker create --name reserva-tenis \
  --env-file .env \
  -v $(pwd)/screenshots:/app/screenshots \
  reserva-tenis
```

### 6. Run manually

```bash
sudo docker start -a reserva-tenis
```

---

## Scheduling on a Synology NAS

To run the bot automatically every week:

1. Open DSM and go to **Control Panel > Task Scheduler**
2. Create a new task of type **User-defined script**
3. Set the trigger to run weekly (e.g. every Thursday morning, to book Friday slots)
4. In the script field, enter:

```bash
/bin/bash -c 'LOG=/volume1/docker/reserva-tenis/logs/$(date +%Y%m%d_%H%M%S).log && docker start -a reserva-tenis 2>&1 | tee $LOG'
```

5. Enable **Send run details by email** to receive the full execution log after each run

> Adjust the path to match where the project is stored on your NAS.

---

## Updating the Bot

After any change to `reserva_final.py`, rebuild the image and recreate the container:

```bash
sudo docker build -t reserva-tenis .
sudo docker rm reserva-tenis
sudo docker create --name reserva-tenis \
  --env-file .env \
  -v /volume1/docker/reserva-tenis/screenshots:/app/screenshots \
  reserva-tenis
```

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
logs/
```

---

## Troubleshooting

**Slot shown as unavailable but court is free:** The availability check uses `button[aria-label]` state. If the site layout changes, update the selectors in `reserva_final.py`.

**Occupant shown as "nao encontrado":** The slot may genuinely be unbooked, or the bookings page took too long to load. The bot will still continue normally.

**Screenshots not saved:** Make sure the `screenshots/` folder exists and the volume is mounted correctly in the `docker create` command.

**Task not running on NAS:** Verify the container exists (`docker ps -a`) and check the DSM task logs for error details.

**Login error:** Double-check that `TENNIS_EMAIL` and `TENNIS_SENHA` in your `.env` file are correct and have no extra spaces.

**After updating the script, changes have no effect:** The script is baked into the Docker image at build time. Always run `docker build` followed by `docker rm` and `docker create` after any change.
