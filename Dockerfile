FROM python:3.8

# Initial setup
RUN apt-get update && apt-get upgrade -y

# Install system utils
RUN apt-get install -y apt-utils software-properties-common
RUN apt-get install -y iputils-ping nmap netcat
RUN apt-get install -y vim wget curl git

# Install TOR
RUN apt-get install -y tor
RUN tor --version

# Install privoxy
RUN apt-get install -y privoxy
RUN privoxy --version

# Python Dependencies
RUN pip install requests==2.25.1
RUN pip install fastapi==0.63.0
RUN pip install uvicorn==0.13.3
RUN pip install injectable==3.4.4
RUN pip install beautifulsoup4==4.9.3
RUN pip install user-agent==0.1.10
RUN pip install simplestr==0.5.0
RUN pip install tekleo-common-utils==0.0.0.2
RUN pip install omoide-cache==0.1.2
RUN pip install stem==1.8.0
RUN pip install aiohttp==3.8.1

# Copy app
RUN mkdir /tor-flood-attack-service
COPY . /tor-flood-attack-service
WORKDIR /tor-flood-attack-service
RUN chmod a+x run.sh

# Run
CMD './run.sh'
