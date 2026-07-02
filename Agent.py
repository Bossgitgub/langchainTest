import os
import requests

from dotenv import load_dotenv
from msal import PublicClientApplication

from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent

# ==========================
# ENV
# ==========================
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID")

AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
BASE_URL = os.getenv("AZURE_OPENAI_ENDPOINT")
MODEL_NAME = os.getenv("AZURE_OPENAI_MODEL")

# ==========================
# TOKEN CACHE
# ==========================
cached_token = None

# ==========================
# LOGIN
# ==========================
def get_user_token():
    global cached_token

    if cached_token:
        return cached_token

    app = PublicClientApplication(
        client_id=CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}"
    )

    result = app.acquire_token_interactive(
        scopes=["User.Read.All"]
    )

    if "access_token" not in result:
        raise Exception(result)

    cached_token = result["access_token"]

    return cached_token

# ==========================
# TOOL
# ==========================
@tool
def get_users(question: str) -> str:
    """
    Get top users from Microsoft 365
    """

    token = get_user_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(
        "https://graph.microsoft.com/v1.0/users?$top=5",
        headers=headers
    )

    if response.status_code != 200:
        return response.text

    users = []

    for user in response.json().get("value", []):
        users.append({
            "name": user.get("displayName"),
            "email": user.get("userPrincipalName")
        })

    return str(users)

# ==========================
# MODEL
# ==========================
llm = ChatOpenAI(
    api_key=AZURE_API_KEY,
    base_url=BASE_URL,
    model=MODEL_NAME,
    default_headers={
        "api-key": AZURE_API_KEY
    },
    temperature=0
)

# ==========================
# AGENT
# ==========================
agent = create_react_agent(
    model=llm,
    tools=[get_users]
)

# ==========================
# TEST
# ==========================
if __name__ == "__main__":

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "List top 5 users"
                }
            ]
        }
    )

    print(result)
