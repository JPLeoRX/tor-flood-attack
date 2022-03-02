# Tor Flood Attack 
This is a tool for orchestrating an HTTP flood attack. We provide a python script that launches parallel requests to target URLs while being covered by TOR or free VPN proxy. We also provide a docker image wrapped over this script, and a scalable docker-compose configuration. 

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
      NUMBER_OF_EPOCHS: 100

      # Min/max values that determine how many requests can be simultaneously sent to a single URL
      # Actual number of requests is always randomly generated, bound between these two numbers
      PARALLEL_SINGLE_URL_MIN_REQUESTS: 200
      PARALLEL_SINGLE_URL_MAX_REQUESTS: 700

      # Should we use TOR proxy or free VPN proxy? (0 - no, 1 - yes)
      # Obviously do not set them both to 1, this will make everything crash
      # Set them both to 0 if you don't want to use any proxy
      #
      # Prefer free VPN proxy when running on servers with low replicas count (less than 5)
      # Also lower parallel single url requests for free vpn
      ENABLE_TOR_PROXY: 1
      ENABLE_FREE_PROXY: 0

      # How often should new proxy identity be generated? Default value - every 6 batches of requests (every 6 URLs)
      # Use 0 or -1 to disable IP change
      TOR_PROXY_IP_CHANGE_FREQUENCY: 6
      FREE_PROXY_IP_CHANGE_FREQUENCY: 6
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
PARALLEL_SINGLE_URL_MIN_REQUESTS: 20
PARALLEL_SINGLE_URL_MAX_REQUESTS: 100
ENABLE_TOR_PROXY: 0
ENABLE_FREE_PROXY: 1
TOR_PROXY_IP_CHANGE_FREQUENCY: 24
FREE_PROXY_IP_CHANGE_FREQUENCY: 24
...
replicas: 2
...
```

Always monitor your hardware, tweak these settings and squeeze the most requests that your network can handle.

# Running
Launching this script is fairly straight forward - clone the repository, navigate to the project's root folder and just run docker-compose.

Clone this repository
```shell script
git clone https://github.com/JPLeoRX/tor-flood-attack.git
cd tor-flood-attack
```

Start the containers with scripts via:
```shell script
docker-compose up --build -d
```

Connect to logs to monitor what's going on inside your containers:
```shell script
docker-compose logs -f -t
```

Or in one command:
```shell script
docker-compose up --build -d && docker-compose logs -f -t
```

To stop and kill all containers:
```shell script
docker-compose down
```

# Side-note: Running with another VPN
If your host machine is already connected to a VPN, with all outgoing traffic forwarded though VPN - all Docker traffic will be forwarded as well. So you don't need to use TOR or free VPN in this container, you can rely on your own host's VPN. 

# Links
In case you’d like to check my other work or contact me:
* [Personal website](https://tekleo.net/)
* [GitHub](https://github.com/jpleorx)
* [PyPI](https://pypi.org/user/JPLeoRX/)
* [DockerHub](https://hub.docker.com/u/jpleorx)
* [Articles on Medium](https://medium.com/@leo.ertuna)
* [LinkedIn (feel free to connect)](https://www.linkedin.com/in/leo-ertuna-14b539187/)