#!/bin/bash

set -e

# Choose the version you want (or use `latest`)
KUBECTL_VERSION=$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)

# Download kubectl binary for ARM64
curl -LO "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/arm64/kubectl"

# Make it executable and move to /usr/local/bin
chmod +x kubectl
mv kubectl /usr/local/bin/kubectl

# Test it
kubectl version --client
