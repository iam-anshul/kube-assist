FROM python:3.12-slim

WORKDIR /requirements

COPY requirements.txt .

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    groff \
    less \
    && rm -rf /var/lib/apt/lists/*

# Download and install AWS CLI v2 (x86_64 version)
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip aws

# Verify installation
RUN aws --version

# Install kubectl (x86_64 version)
RUN KUBECTL_VERSION=$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt) && \
    curl -LO "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl" && \
    chmod +x kubectl && \
    mv kubectl /usr/local/bin/kubectl

RUN kubectl version --client

# Install Python dependencies
RUN pip install -r requirements.txt

COPY /kube-assist-backend /kube-assist-backend

WORKDIR /kube-assist-backend

EXPOSE 8000

CMD /bin/sh -c "alembic upgrade head && python main.py"
