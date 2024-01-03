# Use selenium/node-chrome as base image
FROM selenium/node-chrome:120.0.6099.109-chromedriver-120.0.6099.109

# Set the working directory in the container
WORKDIR /app

# Install Python and pip
USER root
RUN apt-get update \
    && apt-get install -y python3.11 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install the Python dependencies
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code into the Docker image
COPY . .

# Run your application
CMD [ "python3", "./grafanascreenshots.py" ]
