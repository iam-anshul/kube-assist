import os
from kubernetes import config

def load_kube_config(kubeconfig_path: str = None):
    if kubeconfig_path:
        config.load_kube_config(config_file=kubeconfig_path)
    else:
        config.load_kube_config()