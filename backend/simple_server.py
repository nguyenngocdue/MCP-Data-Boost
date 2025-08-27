from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient
import os, traceback

# Load environment variables from .env file (OPENAI_API_KEY, OPENAI_MODEL, etc.)
load_dotenv()

# Default model and allowed frontend origin
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

# Initialize FastAPI app
app = FastAPI()

# Enable CORS so that the Vite frontend (running on port 5173) can call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── MCP client configuration using STDIO ──
# This will spawn a Playwright MCP server via npx
stdio_config = {
    "mcpServers": {
        "playwright": {
            "command": "npx",
            "args": ["@playwright/mcp@latest"],
        }
    }
}
# Create MCP client from the configuration
client = MCPClient.from_dict(stdio_config)

# Create the LLM (Large Language Model) interface using OpenAI
llm = ChatOpenAI(model=OPENAI_MODEL)

# Health check endpoint
@app.get("/health")
def health():
    return {"ok": True}

# Natural language query endpoint
@app.post("/api/nl")
async def run_query(req: Request):
    # Parse JSON request body
    body = await req.json()
    q = body.get("query", "")
    steps = int(body.get("max_steps", 30))

    print(f"[API] query={q!r}, steps={steps}")
    try:
        # Create an MCP agent with LLM + MCP client
        agent = MCPAgent(llm=llm, client=client, max_steps=steps)
        
        # Run the query using the agent (LLM + Playwright MCP)
        result = await agent.run(q, max_steps=steps)

        print("[API] done")
        return {"result": result}
    except Exception as e:
        # Print error to console and return 500 response
        print("[API] ERROR:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
