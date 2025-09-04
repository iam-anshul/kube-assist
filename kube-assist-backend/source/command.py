import logging
import os
import subprocess

logger = logging.getLogger(__name__)

def run_kubectl_command(command: str, context_name: str, kubeconfig_path: str, access_key_id: str, access_key: str):
    env = os.environ.copy()
    env["KUBECONFIG"] = kubeconfig_path
    env["AWS_ACCESS_KEY_ID"] = access_key_id
    env["AWS_SECRET_ACCESS_KEY"] = access_key

    full_command = f"{command} --context={context_name}"
    logger.info("Command ran by model: %s", full_command)

    result = subprocess.run(full_command, shell=True, capture_output=True, env=env)

    if result.returncode != 0:
        error = result.stderr.decode().strip()
        logger.warning("kubectl command failed with exit code %s", result.returncode)
        return f"Error: {error}"

    return result.stdout.decode().strip()
