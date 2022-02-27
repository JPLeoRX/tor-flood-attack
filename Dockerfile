FROM ubuntu:20.04
ENV TZ=UTC

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

# Install Python 3.8 & Pip 3
WORKDIR /
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get install -y python3.8
RUN echo "alias python='python3.8'" >> ~/.bashrc
RUN echo "alias python3='python3.8'" >> ~/.bashrc
RUN apt-get install -y python3-pip
RUN echo "alias pip='pip3'" >> ~/.bashrc

# Python Dependencies
RUN pip3 install requests==2.25.1
RUN pip3 install stem==1.8.0
RUN pip3 install user-agent==0.1.10
RUN pip3 install tekleo-common-utils==0.0.0.2
RUN pip3 install aiohttp==3.8.1

# Copy app
RUN mkdir /tor-flood-attack-service
COPY . /tor-flood-attack-service
WORKDIR /tor-flood-attack-service
RUN chmod a+x run.sh

# Run
CMD './run.sh'
