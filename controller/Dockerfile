FROM python:3.8

# Initial setup
RUN apt-get update && apt-get upgrade -y

# Install system utils
RUN apt-get install -y apt-utils software-properties-common
RUN apt-get install -y iputils-ping nmap netcat
RUN apt-get install -y vim wget curl git

# Common dependencies
RUN pip install requests==2.25.1
RUN pip install fastapi==0.63.0
RUN pip install uvicorn==0.13.3
RUN pip install injectable==3.4.4

# Main app
COPY . /app
WORKDIR /app

# Run command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000", "--workers", "1"]
