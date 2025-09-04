from supertokens_python import init, InputAppInfo, SupertokensConfig
from supertokens_python.recipe import emailpassword, session
from supertokens_python import get_all_cors_headers
from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware
from supertokens_python.framework.fastapi import get_middleware
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from source.routes.admin.admin_routes import admin_router
from source.routes.chat.chat import chat_router
from source.routes.kube_config.kubeconfig import kubeconfig_router
from source.routes.projects.project import project_router
from source.routes.tasks.task import task_router
import secrets

from dotenv import load_dotenv
import os

load_dotenv()
 
supertokens_connection_url=os.getenv("SUPERTOKENS_CONNECTION_URL")
supertokens_api_key=os.getenv("SUPERTOKENS_API_KEY")

docs_username = os.getenv("DOCS_USERNAME")
docs_password = os.getenv("DOCS_PASSWORD")

if not (docs_username and docs_password):
    raise RuntimeError(
        "DOCS_USERNAME and DOCS_PASSWORD must be set to serve the API docs. "
        "See .env.example."
    )

security = HTTPBasic()

app = FastAPI(
    title="KubeAssist API",
    description="API for Kubernetes assistance",
    version="1.0.0",
    openapi_tags=[],
    docs_url=None,  
    redoc_url=None  
)

root_router = APIRouter()

async def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, docs_username)
    correct_password = secrets.compare_digest(credentials.password, docs_password)
    if not (correct_username & correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/openapi.json", include_in_schema=False)
def custom_openapi(username: str = Depends(get_current_user)):
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Kube Assist API",
        version="1.0.0",
        routes=app.routes,
    )
    
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            if "security" not in operation:
                operation["security"] = []
            operation["security"].append({"bearerAuth": []})
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


@app.get("/docs", include_in_schema=False)
async def get_documentation(username: str = Depends(get_current_user)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Kube Assist docs")

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
	    session.init(), 
        emailpassword.init()
    ],
    mode='asgi' 
)

app.add_middleware(get_middleware())

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"] + get_all_cors_headers(),
)

@app.get("/health")
def health_check():
    return {"status": "UP"}

@app.get("/version")
def get_version():
    return "v1"

@app.get("/", status_code=200)
def hello_world():
    return "Server is running!"

root_router.include_router(admin_router, prefix="/admin", tags=["admin"])
root_router.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(root_router)
app.include_router(kubeconfig_router, prefix="/kubeconfig", tags=["kubeconfig"])
app.include_router(project_router, prefix='/project', tags=["project"])
app.include_router(task_router, prefix='/task', tags=['task'])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
