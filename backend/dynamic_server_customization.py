# api/main.py

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient
import os, traceback, json

load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khởi tạo MCP
client = MCPClient.from_config_file("multi_server_config.json")
llm = ChatOpenAI(model=OPENAI_MODEL)

# Đường dẫn file users.json
USERS_JSON = os.path.abspath("data/users.json")
os.makedirs(os.path.dirname(USERS_JSON), exist_ok=True)

# Tạo file nếu chưa có
if not os.path.exists(USERS_JSON):
    with open(USERS_JSON, "w", encoding="utf-8") as f:
        json.dump({"users": []}, f, indent=2, ensure_ascii=False)

def read_users():
    with open(USERS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)["users"]

def write_users(users):
    with open(USERS_JSON, "w", encoding="utf-8") as f:
        json.dump({"users": users}, f, ensure_ascii=False, indent=2)

def next_id(users):
    return max((u["id"] for u in users), default=0) + 1

@app.get("/health")
def health():
    return {"ok": True}

# SYSTEM PROMPT để parse CRUD nếu cần fallback
FALLBACK_PARSE_PROMPT = """
Bạn là một parser thông minh. Chuyển đổi yêu cầu người dùng thành JSON hành động.
Chỉ trả về JSON, không giải thích.

Schema:
{
  "action": "create|update|delete|list|none",
  "name": "str?",
  "email": "str?",
  "id": "int?"
}

Ví dụ:
- "tạo user tên Bob, email bob@x.com" → {"action":"create","name":"Bob","email":"bob@x.com"}
- "xóa user id 2" → {"action":"delete","id":2}
- "cập nhật user 3: name New" → {"action":"update","id":3,"name":"New"}
- "liệt kê" → {"action":"list"}
- "hello" → {"action":"none"}
"""

@app.post("/api/users/nl")
async def run_query(req: Request):
    body = await req.json()
    q = body.get("query", "").strip()
    steps = int(body.get("max_steps", 30))

    if not q:
        raise HTTPException(status_code=400, detail="Missing query")

    print(f"[API] Received query: {q!r}")

    # === 1. Thử dùng MCP trước ===
    try:
        agent = MCPAgent(llm=llm, client=client, max_steps=steps, use_server_manager=True)
        result = await agent.run(q, max_steps=steps)

        # Nếu MCP trả kết quả → dùng luôn
        if result.strip():
            print("[API] MCP handled the query")
            return {
                "result": result,
                "mode": "mcp_tool"
            }
    except Exception as e:
        print(f"[API] MCP failed: {e}")
        traceback.print_exc()

    # === 2. MCP không xử lý → fallback: thử parse CRUD nội bộ ===
    try:
        msgs = [
            {"role": "system", "content": FALLBACK_PARSE_PROMPT},
            {"role": "user", "content": q}
        ]
        resp = await llm.ainvoke(msgs)
        raw = resp.content.strip()
        cmd = json.loads(raw)
        action = cmd.get("action")

        if action == "list":
            users = read_users()
            return {
                "mode": "fallback_crud",
                "action": "list",
                "users": users
            }

        if action == "create":
            name = (cmd.get("name") or "").strip()
            email = (cmd.get("email") or "").strip()
            if not name or not email:
                raise HTTPException(status_code=400, detail="Name and email required")
            users = read_users()
            if any(u["email"].lower() == email.lower() for u in users):
                raise HTTPException(status_code=409, detail="Email already exists")
            new_user = {"id": next_id(users), "name": name, "email": email}
            users.append(new_user)
            write_users(users)
            return {
                "mode": "fallback_crud",
                "action": "create",
                "user": new_user
            }

               if action == "update":
            user_id = cmd.get("id")
            name = cmd.get("name")
            email = cmd.get("email")

            if not user_id:
                raise HTTPException(status_code=400, detail="User ID is required to update")

            users = read_users()
            user = next((u for u in users if u["id"] == user_id), None)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Kiểm tra trùng email nếu có cập nhật email
            if email:
                email = email.strip()
                if any(u["email"].lower() == email.lower() and u["id"] != user_id for u in users):
                    raise HTTPException(status_code=409, detail="Email already taken by another user")

                user["email"] = email
            if name:
                user["name"] = name.strip()

            write_users(users)
            return {
                "mode": "fallback_crud",
                "action": "update",
                "user": user
            }

        if action == "delete":
            user_id = cmd.get("id")
            if not user_id:
                raise HTTPException(status_code=400, detail="User ID is required to delete")

            users = read_users()
            user = next((u for u in users if u["id"] == user_id), None)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            users.remove(user)
            write_users(users)
            return {
                "mode": "fallback_crud",
                "action": "delete",
                "user": user
            }

        # Nếu action == "none" → không phải CRUD
        if action == "none":
            raise ValueError("Not a CRUD command")

    except Exception as e:
        print(f"[API] Fallback CRUD failed or not applicable: {e}")

    # === 3. Fallback cuối cùng: chat với LLM ===
    try:
        chat_resp = await llm.ainvoke([{"role": "user", "content": q}])
        return {
            "mode": "chat",
            "answer": chat_resp.content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="LLM fallback failed")