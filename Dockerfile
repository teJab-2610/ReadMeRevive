# Use the Ubuntu base image
FROM ubuntu:latest
RUN apt-get update 
RUN apt-get install -y curl

#Install python eviroment
RUN apt-get install -y python3 python3-pip git-all 

# Set the working directory inside the container
WORKDIR /app 

# Copy the shell script and Python script into the container
COPY install_requirements.sh .
COPY main.py .

# Run the shell script to install dependencies
RUN chmod +x install_requirements.sh
RUN ./install_requirements.sh

# Command to run the Python script
CMD ["python3", "main.py"]
