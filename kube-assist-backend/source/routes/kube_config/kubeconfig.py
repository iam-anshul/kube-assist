from fastapi import Depends, APIRouter, HTTPException
from supertokens_python.recipe.session.framework.fastapi import verify_session
from supertokens_python.recipe.session import SessionContainer
from uuid import UUID
from source.models import kubeconfigRequest, set_aws_credsRequest
from source.routes.kube_config.crud import get_cloudcreds, add_cloudcreds_entry, is_cloudcreds_entry_exist
import os
import yaml
import shutil
import subprocess
import configparser

kubeconfig_router = APIRouter()

def generate_eks_kubeconfig(credntialsPath: str, configPath: str, region: str, cluster_name: str, kubeconfigPath: str):
    env = os.environ.copy()
    env["AWS_SHARED_CREDENTIALS_FILE"] = credntialsPath
    env["AWS_CONFIG_FILE"] = configPath
    
    result = subprocess.run(f"aws eks update-kubeconfig --name {cluster_name} --region {region} --kubeconfig {kubeconfigPath}", shell=True, capture_output=True, env=env)

    if result.returncode != 0:
        print(result.stderr.decode().strip())
        raise Exception(f"Error in setting  generate_eks_kubeconfig: {result.stderr.decode().strip()}")

def does_cloudCreds_exist_in_filesystem(userID: UUID, projectID: UUID):
    directory_path = os.path.expanduser(f"~/.cloud_creds/{userID}_configs/{projectID}/")
    file_path = os.path.join(directory_path, 'config')

    return os.path.isfile(file_path)

def fetch_and_set_kubeconfig_from_cli(userID: UUID, projectID: UUID):
    creds = get_cloudcreds(userID, projectID)
    cloud_cred_dir = os.path.expanduser(f"~/.cloud_creds/{userID}_configs/{projectID}")
    cloud_cred_path = os.path.join(cloud_cred_dir, "credentials")
    cloud_config_path = os.path.join(cloud_cred_dir, "config")
    kubeconfig_path = os.path.expanduser(f"~/.server_kubeconfigs/{userID}_configs/{projectID}/config")
    credentials_file = f"""
[default]
aws_access_key_id = {creds["key"]}
aws_secret_access_key = {creds["value"]}
"""
    credentials_config = f"""
[default]
region = {creds["region"]}
"""
    try:
        os.makedirs(cloud_cred_dir, exist_ok=True)
        with open(cloud_cred_path, 'w') as credentials:
            credentials.write(credentials_file)

        os.makedirs(cloud_cred_dir, exist_ok=True)
        with open(cloud_config_path, 'w') as config:
            config.write(credentials_config)

        generate_eks_kubeconfig(cloud_cred_path, cloud_config_path, creds["region"], creds["name"], kubeconfig_path)
    except Exception as e:
        if os.path.exists(cloud_cred_dir):
            shutil.rmtree(cloud_cred_dir)  
        print("Exception occured in fetch_and_set_kubeconfig_from_cli function: ", e)
        raise HTTPException(500, detail=f'Error in setting aws creds file: {e}')
    
@kubeconfig_router.post('/set-aws-creds')
async def set_aws_creds(creds: set_aws_credsRequest, session: SessionContainer = Depends(verify_session())):
    user_id = session.get_user_id()
    cloud_cred_dir = os.path.expanduser(f"~/.cloud_creds/{user_id}_configs/{creds.project_id}")
    cloud_cred_path = os.path.join(cloud_cred_dir, "credentials")
    cloud_config_path = os.path.join(cloud_cred_dir, "config")
    kubeconfig_path = os.path.expanduser(f"~/.server_kubeconfigs/{user_id}_configs/{creds.project_id}/config")
    creds_data = f"""
[default]
aws_access_key_id = {creds.access_key_id}
aws_secret_access_key = {creds.access_key}
"""
    
    config_data = f"""
[default]
region = {creds.region}
"""

    try:
        os.makedirs(cloud_cred_dir, exist_ok=True)
        with open(cloud_cred_path, 'w') as creds_file:
            creds_file.write(creds_data)

        with open(cloud_config_path, 'w') as config_file:
            os.makedirs(cloud_cred_dir, exist_ok=True)
            config_file.write(config_data)

        generate_eks_kubeconfig(cloud_cred_path, cloud_config_path, creds.region, creds.cluster_name, kubeconfig_path)
    except Exception as e:
        print(f"Error occured in setting aws creds: {e}")
        raise HTTPException(500, detail=f"Error occured in setting aws creds: {e}") #2a1b4de9-2019-444c-a04b-2191d294621e

    try:
        add_cloudcreds_entry(
            userID=user_id,
            projectID=creds.project_id,
            userKey=creds.access_key_id.encode('utf-8'),
            userValue=creds.access_key.encode('utf-8'),
            userRegion=creds.region.encode('utf-8'),
            clusterName=creds.cluster_name.encode('utf-8')
        )
    except Exception as e:
        if os.path.exists(cloud_cred_dir):
            shutil.rmtree(cloud_cred_dir)  
            print(f"{cloud_cred_dir} and all its contents deleted.")
        else:
            print(f"{cloud_cred_dir} does not exist.")
        raise HTTPException(500, f"Cannot add entry: {e}")
    
    return creds.project_id

@kubeconfig_router.get('/initialize-cloud-kubeconfig')
def initialize_cloud_kubeconfig(projectID: UUID, session: SessionContainer = Depends(verify_session())):
    userID = session.get_user_id()

    if not does_cloudCreds_exist_in_filesystem(userID, projectID):
        if not is_cloudcreds_entry_exist(userID, projectID):
            raise HTTPException(404, detail='aws cloud not set')
        else:
            fetch_and_set_kubeconfig_from_cli(userID, projectID)
            return projectID
    return projectID

def get_context_names(path: str):
    """
    Extracts context names from a kubeconfig file provided as bytes.

    :param kubeconfig_bytes: The kubeconfig file content as bytes.
    :return: A list of context names.
    """
    with open(path, 'r') as kc:
        kubeconfig_str = kc.read()
    try:
        kubeconfig = yaml.safe_load(kubeconfig_str)

        # Extract and return context names
        contexts = kubeconfig.get("contexts", [])
        context = contexts[0]
        return context.get("name")
    except Exception as e:
        print(f"Error parsing kubeconfig: {e}")
        return []
    
def get_access_key_and_id(dirPath:str):
    config = configparser.ConfigParser()
    config.read(dirPath)

    access_key = config['default'].get("aws_access_key_id")
    secret_key = config['default'].get("aws_secret_access_key")

    return access_key, secret_key
    

