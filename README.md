# ETL Project

Pull current-conditions data from **OpenWeatherMap**, tidy it with **pandas**, and load it into **PostgreSQL** on an hourly schedule.  
The pipeline is orchestrated by **Apache Airflow** and ships with a one-command Docker Compose stack for local runs.


## Installation

Quick-start (local)

> **Prereqs :** Docker ≥ 20 .x and Docker Compose v2, plus an OpenWeatherMap API key from https://openweathermap.org/

1. Clone the repository and cd into root folder
```bash
git clone https://github.com/brian-vu-nguyen/weather-etl.git
cd weather-etl
```
2. Provide your API Key
```bash
echo "API_KEY=<your-openweather-api-key>" > .env          # used by extract.py
```

3. Setup docker and airflow through their 'Get Started' guides.

4. Configure docker-compose.yaml and .env (credentials, usernames, passwords, ports, volumes)

5. Spin-up stack
```bash
docker compose up -d          # brings up airflow-{web, scheduler, worker}, postgres, pgadmin
docker compose ps             # view stack details
```

6. Log in to Airflow & Postgres GUI
open http://localhost:8080    # user: airflow / pw: airflow  (default)
open http://localhost:5432    # pg_default_email: <your-default-email> / pg_default_pw: <your-default-pw>

7. Flip the “weather_etl_pipeline” DAG switch to **On**

## Environment Variables
Copy `.env.example` to `.env` and fill in any secrets or config values.

## Docker Cheatsheet
Images
```bash
docker pull <name>:<tag>                       # Pull image; docker pull python:3.12-slim
docker images                                  # List local images; or: docker image ls
docker build -t <repo>/<image>:<tag> .         # Build from Dockerfile
docker tag <image>:<old> <repo>/<image>:<new>  # Tag / retag images
docker rmi <image_id|name:tag>                 # Remove image
```

Docker Compose (v2 syntax: docker compose ...)
```bash
docker compose up -d             # start in background
docker compose logs -f           # stream logs
docker compose ps                # list services
docker compose exec <svc> bash   # shell into service
docker compose down -v           # stop & remove (incl. volumes)
docker compose build             # rebuild services
```