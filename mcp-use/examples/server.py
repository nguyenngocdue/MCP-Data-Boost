from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient
import os, traceback
from fastapi import HTTPException


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

# ── MCP cấu hình theo kiểu STDIO (spawn npx @playwright/mcp@latest) ──
stdio_config = {
    "mcpServers": {
        "playwright": {
            "command": "npx",
            "args": ["@playwright/mcp@latest"],
            # Nếu bạn đang ở Linux cần Xvfb mới set DISPLAY. Windows/macOS để trống.
            # "env": {"DISPLAY": ":1"}
        }
    }
}
client = MCPClient.from_dict(stdio_config)
llm = ChatOpenAI(model=OPENAI_MODEL)

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/api/nl")
async def run_query(req: Request):
    body = await req.json()
    q = body.get("query", "")
    steps = int(body.get("max_steps", 30))

    print(f"[API] query={q!r}, steps={steps}")
    try:
        agent = MCPAgent(llm=llm, client=client, max_steps=steps)
        result = await agent.run(q, max_steps=steps)
        print("[API] done")
        return {"result": result}
    except Exception as e:
        print("[API] ERROR:", e)
        traceback.print_exc()
        # Đẩy message ra response cho dễ thấy
        raise HTTPException(status_code=500, detail=str(e))
