# ETL Project

Pull current-conditions data from **OpenWeatherMap**, tidy it with **pandas**, and load it into **PostgreSQL** on an hourly schedule.  
The pipeline is orchestrated by **Apache Airflow** and ships with a one-command Docker Compose stack for local runs.


## Installation & Setup

Quick-start (local)\
> **Prereqs :** Docker ≥ 20 .x and Docker Compose v2, plus an OpenWeatherMap API key from https://openweathermap.org/

Clone the repository and cd into root folder
```bash
git clone https://github.com/brian-vu-nguyen/weather-etl.git
cd weather-etl
```

Provide your API Key
```bash
echo "API_KEY=<your-openweather-api-key>" > .env          # used by extract.py
```

Setup docker their 'Get Started' guide

Configure docker-compose.yaml.example (copy and remove .example)\
   or start from scratch with below:
``` bash
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/3.0.2/docker-compose.yaml' 
```

Configure .env (credentials, usernames, passwords, ports, volumes)
- See '.env.example'

Spin-up stack
```bash
docker compose up -d          # brings up airflow-{web, scheduler, worker}, postgres, pgadmin
docker compose ps             # view stack details
```

Log in to Airflow & Postgres GUI
open http://localhost:8080    # user: airflow / pw: airflow  (default)
open http://localhost:5432    # pg_default_email: <your-default-email> / pg_default_pw: <your-default-pw>

Flip the “weather_etl_pipeline” DAG switch to **On**


## Docker Cheatsheet
Images
```bash
docker pull <name>:<tag>                       # Pull image; docker pull python:3.12-slim
docker images                                  # List local images; or: docker image ls
docker build -t <repo>/<image>:<tag> .         # Build from Dockerfile
docker tag <image>:<old> <repo>/<image>:<new>  # Tag / retag images
docker rmi <image_id|name:tag>                 # Remove image
```

Containers (single-host runtime)
```bash
docker run -d --name <alias> -p 8080:80 <image>  # run a container
docker run -it --rm <image> bash                 # interactive run
docker ps                                        # list running
docker ps -a                                     # list all (incl. exited)
docker start <id>                                # start a container
docker stop <id>                                 # stop a container
docker logs -f <id>                              # attach to stdout
docker exec -it <id> bash                        # exec into a shell
```

Volumnes & Bind Mounts
```bash
docker volume create pgdata
docker run -v pgdata:/var/lib/postgresql/data postgres:16
docker run -v $(pwd)/src:/app python:3.12
docker volume ls
docker volume inspect pgdata
docker volume rm pgdata
```

Docker Compose (v2 syntax: docker compose ...)
```bash
docker compose up -d             # start in background
docker compose logs -f           # stream logs
docker compose exec <svc> bash   # shell into service
docker compose down -v           # stop & remove (incl. volumes)
docker compose build             # rebuild services
```