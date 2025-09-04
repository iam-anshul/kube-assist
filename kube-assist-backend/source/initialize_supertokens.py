from supertokens_python import init, InputAppInfo, SupertokensConfig
from supertokens_python.recipe import emailpassword, session
from dotenv import load_dotenv
import os

def initialise_supertokens():

    load_dotenv()
    supertokens_connection_url=os.getenv("SUPERTOKENS_CONNECTION_URL")
    supertokens_api_key=os.getenv("SUPERTOKENS_API_KEY")

    init(
        app_info=InputAppInfo(
        app_name="kube-assist",
        api_domain="http://localhost:8000",
        website_domain="http://localhost:3000",
        api_base_path="/auth",
        website_base_path="/auth"
    ),
    supertokens_config=SupertokensConfig(
        connection_uri=supertokens_connection_url,
        api_key=supertokens_api_key
    ),
    framework='fastapi',
    recipe_list=[
	    session.init(), # initializes session features
        emailpassword.init()
    ],
    mode='asgi' # use wsgi if you are running using gunicorn
)   







