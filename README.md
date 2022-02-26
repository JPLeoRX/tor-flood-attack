# Configuration
Before launching this I highly suggest you to get familiar with how things can be adjusted in this script.

### Targets
Target settings - all target URLs are hard-coded in `main.py` in `LIST_OF_URLS` variable:
```python
...
# A list of urls that need to be attacked
# Please note that all of them are either "http" or "https"
LIST_OF_URLS = [
    ...
]
...
```

### Performance
There are 2 places that have major performance settings. 

First and foremost - how many containers with this script you want to run at the same time. This is configured in `docker-compose.yml` under `replicas` field. Pretty straight forward - lower to run less replicas of this container, increase if you feel like your PC can handle it.
```yaml
version: "3.9"
services:
  tor-flood-attack:
    build:
      context: .
      dockerfile: Dockerfile
    deploy:
      replicas: 16
      restart_policy:
        condition: any
```

Now for more in-depth tweaking - go to `main.py`, and look for these variables:
```python
...
# How many cycles (epochs) of attacks should be performed
# This value can be ignored, you can control the attack by stopping docker-compose at any time
NUMBER_OF_EPOCHS = 10

# How many URLs from your list will be attacked in parallel
PARALLEL_LIST_OF_URLS_WORKERS = 2

# Min/max values that determine how many requests can be simultaneously sent to a single URL
PARALLEL_SINGLE_URL_MIN_REQUESTS = 150
PARALLEL_SINGLE_URL_MAX_REQUESTS = 400

# How many requests on the same URL will be processed in parallel
PARALLEL_SINGLE_URL_WORKERS = 50

# Should we use tor?
# The default values is True, and we will print out warnings if you disable it
# Use at your own risk, only if you know what you're doing
ENABLE_TOR = True
...
```

This setup has a potential to really warn up your hardware, please lower the settings if you're not sure what stress your PC can handle. For a modest PC it'll look like this:
```python
...
NUMBER_OF_EPOCHS = 10
PARALLEL_LIST_OF_URLS_WORKERS = 1
PARALLEL_SINGLE_URL_MIN_REQUESTS = 20
PARALLEL_SINGLE_URL_MAX_REQUESTS = 100
PARALLEL_SINGLE_URL_WORKERS = 10
...
```

```yaml
...
services:
  tor-flood-attack:
    deploy:
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
