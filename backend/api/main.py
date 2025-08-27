from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient
import os
import traceback
import json
from pathlib import Path

# Load biến môi trường
load_dotenv()

# Cấu hình
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
USERS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "users.json")
# Khởi tạo app
app = FastAPI(title="NL to CRUD API with MCP")
print(f"[INFO] Users file: {USERS_FILE}")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)


ROOT = Path(__file__).resolve().parents[1]  # Move up two levels to the project root
SERVER_DIR = ROOT / "user-manager"  # Correct path to user-manager folder
SERVER_SCRIPT = SERVER_DIR / "user_server.py"  # Full path to user_server.py

config = {
    "mcpServers": {
        "user-manager": {
            "command": "py",  # Ensure 'py' is installed and in the system PATH
            "args": [str(SERVER_SCRIPT)],  # Absolute path to the user_server.py script
            "cwd": str(SERVER_DIR)  # Set current working directory to user-manager
        }
    }
}

# Khởi tạo MCP
try:
    # client = MCPClient.from_config_file("../multi_server_config.json")
    client = MCPClient.from_dict(config)
    print(f"[INFO] MCP client initialized : {client}")
    print(f"[INFO] MCP client created. Server path: {SERVER_SCRIPT}")


    llm = ChatOpenAI(model=OPENAI_MODEL)
except Exception as e:
    print(f"[ERROR] Failed to initialize MCP or LLM: {e}")
    raise

# === Endpoints ===

@app.get("/health")
def health():
    return {"ok": True, "model": OPENAI_MODEL}

@app.get("/api/users")
def get_users():
    """REST endpoint: Lấy danh sách user (dùng cho frontend bảng dữ liệu)"""
    print(f"[INFO] Users file: {USERS_FILE}, exists: {os.path.exists(USERS_FILE)}")
    if not os.path.exists(USERS_FILE):
        return {"users": []}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"[INFO] Users data: {data}")
            return data
    except Exception:
        return {"users": []}

@app.post("/api/users/nl")
async def run_query(req: Request):
    """
    Xử lý câu hỏi tự nhiên:
    - Dùng MCP để gọi tool (createUser, listUsers,...)
    - Nếu MCP không xử lý → fallback sang chat
    """
    body = await req.json()
    query = (body.get("query") or "").strip()
    max_steps = int(body.get("max_steps", 30))

    if not query:
        raise HTTPException(status_code=400, detail="Missing 'query'")

    print(f"[NL] Query: {query!r}")

    # 1. Dùng MCP xử lý
    try:
        agent = MCPAgent(
            llm=llm,
            client=client,
            max_steps=max_steps,
            use_server_manager=True
        )
        result = await agent.run(query)
        print("[NL] MCP handled")
        return {
            "mode": "tool",
            "result": result.strip()
        }
    except Exception as e:
        print(f"[NL] MCP failed: {e}")
        traceback.print_exc()

    # 2. Fallback: Dùng LLM trả lời như chatbot
    try:
        response = await llm.ainvoke([{"role": "user", "content": query}])
        print("[NL] Fallback chat")
        return {
            "mode": "chat",
            "result": response.content
        }
    except Exception as e:
        print(f"[NL] Fallback failed: {e}")
        raise HTTPException(status_code=500, detail="Internal LLM error")
