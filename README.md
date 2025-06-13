# ETL Project

Pull current-conditions data from **OpenWeatherMap**, tidy it with **pandas**, and load it into **PostgreSQL** on an hourly schedule.  
The pipeline is orchestrated by **Apache Airflow** and ships with a one-command Docker Compose stack for local runs.

## Prerequisites

| Tool | Why you need it | Minimum version |
|------|-----------------|-----------------|
| **Docker Engine** | Runs the containerised stack (Airflow, Postgres, pgAdmin). | 20.x |
| **Docker Compose** | Orchestrates the multi-container setup defined in `docker-compose.yaml`. | v2 plugin (shipped with Docker Desktop ≥ 4.x) |
| **Git** | To clone this repository. | Any modern version |

> **Already have Docker & Compose?** Great—no re-install needed.  
> If you’re new to Docker, download **Docker Desktop** (Win/Mac) or follow the [Docker Engine install guide](https://docs.docker.com/engine/install/) for Linux. Airflow and Postgres are pulled as images when you run `docker compose up`, so nothing else needs local installation.


## Installation

1. Obtain an API Key from [OpenWeather](https://openweathermap.org/)

2. Clone the repository and cd into root folder
```bash
git clone https://github.com/brian-vu-nguyen/weather-etl.git
cd weather-etl
```

3. Copy docker-compose.yaml.example
> Remove .example

*OR* start from scratch:
``` bash
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/3.0.2/docker-compose.yaml' 
```


## Configure
1. Provide your API Key
```bash
echo "API_KEY=<your-openweather-api-key>" > .env          # used by extract.py
```

2. Configure docker-compose.yaml & .env (credentials, usernames, passwords, ports, volumes)

3. Add files to .gitignore (create file if it doesn't exist)
```bash
echo -e ".env\ndocker-compose.yaml\n" >> .gitignore
```

4. Spin-up stack
```bash
docker compose up -d          # brings up airflow-{web, scheduler, worker}, postgres, pgadmin
docker compose ps             # view stack details
```

5. Log in to Airflow & Postgres GUI
```bash
open http://localhost:8080    # user: airflow / pw: airflow  (default)
open http://localhost:5432    # pg_default_email: <your-default-email> / pg_default_pw: <your-default-pw>
```

6. Add Airflow Variables & Connections 

7. Flip the “weather_etl_pipeline” DAG switch to **On**


## Docker Cheatsheet

Below are some common docker commands that you'll likely run:

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

Networks
```bash
docker network ls                  # list
docker network create etl-net      # bridge by default
docker run --network etl-net ...
docker network inspect etl-net
docker network rm etl-net
```

House-Keeping
```bash
docker system df                 # space usage
docker system prune -f           # remove dangling data
docker image prune -a            # remove unused images
docker container prune           # remove stopped containers
```

Docker Compose (v2 syntax: `docker compose ...`)
```bash
docker compose up -d             # start in background
docker compose logs -f           # stream logs
docker compose exec <svc> bash   # shell into service
docker compose down -v           # stop & remove (incl. volumes)
docker compose build             # rebuild services
```

Troubleshooting / Inspect
```bash
docker inspect <object_id>        # full JSON metadata
docker top <container_id>         # running processes
docker stats                      # live CPU/MEM per container
docker events                     # real-time daemon events
```

Copying Files
```bash
docker cp <container>:<path> ./localdir
docker cp ./localfile <container>:/target
```

Save / Load / Export
```bash
docker save <image>:tag -o file.tar       # image → archive
docker load -i file.tar                   # archive → image
docker export <container_id> > rootfs.tar # container FS → tar
docker import rootfs.tar myimage:latest   # tar → image
```

Version & Context
```bash
docker version            # client & server versions
docker context ls         # list contexts (e.g., remote daemons)
docker context use <ctx>
```