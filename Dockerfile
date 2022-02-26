FROM ubuntu:20.04
ENV TZ=UTC

# Initial setup
RUN apt-get update && apt-get upgrade -y

# Install system utils
RUN apt-get install -y apt-utils software-properties-common
RUN apt-get install -y iputils-ping nmap
RUN apt-get install -y vim wget git

# Install TOR
RUN apt-get install -y tor
RUN tor --version

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

# Additional dependencies
RUN apt-get install -y curl
RUN apt-get install -y netcat

# Install privoxy
RUN apt-get install -y privoxy
RUN privoxy --version

# Copy app
RUN mkdir /tor-ddos-attack-service
COPY . /tor-ddos-attack-service
WORKDIR /tor-ddos-attack-service
RUN chmod a+x run.sh

# Run
CMD './run.sh'
