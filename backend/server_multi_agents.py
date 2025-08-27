from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient
import os, traceback

# Load environment variables from the .env file
# Expected: OPENAI_API_KEY, OPENAI_MODEL, FRONTEND_ORIGIN
load_dotenv()

# Default LLM model (can be overridden via OPENAI_MODEL in .env)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
# Default frontend origin allowed by CORS (Vite runs on localhost:5173)
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

# Initialize FastAPI app
app = FastAPI()

# Enable CORS so the frontend can call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- MCP SERVER CONFIGURATIONS ----
# Each entry here defines one MCP server.
# Every client instance will only connect to a single server.
# ---- MCP SERVER CONFIGURATIONS ----
SERVER_CONFIGS = {
    "playwright": {
        "mcpServers": {
            "playwright": {
                "command": "npx",
                "args": ["@playwright/mcp@latest"],
                # "env": {"DISPLAY": ":1"},  # cần trên Linux/Xvfb
            }
        }
    },
    "airbnb": {
        "mcpServers": {
            "airbnb": {
                "command": "npx",
                "args": ["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"],
            }
        }
    },
    "github": {
        "mcpServers": {
            "github": {
                "command": "npx",
                "args": ["@mcp/github-server@latest"],
                "env": {
                    "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN")
                }
            }
        }
    }

}

# (không đổi) Agent "all" gom toàn bộ tool:
ALL_CONFIG = {
    "mcpServers": {
        k: v
        for conf in SERVER_CONFIGS.values()
        for k, v in conf["mcpServers"].items()
    }
}


# Optional: a single client that connects to ALL servers at once
ALL_CONFIG = {
    "mcpServers": {
        k: v
        for conf in SERVER_CONFIGS.values()
        for k, v in conf["mcpServers"].items()
    }
}

# ---- INITIALIZE LLM + MCP AGENTS ----
llm = ChatOpenAI(model=OPENAI_MODEL)

AGENTS = {}
# Create one agent per server (playwright, airbnb, ...)
for name, conf in SERVER_CONFIGS.items():
    client = MCPClient.from_dict(conf)                # client connects to ONE server
    AGENTS[name] = MCPAgent(llm=llm, client=client, max_steps=30)

# Optional: an "all" agent that combines tools from all servers
ALL_CLIENT = MCPClient.from_dict(ALL_CONFIG)
AGENTS["all"] = MCPAgent(llm=llm, client=ALL_CLIENT, max_steps=30)

# ---- API ENDPOINTS ----

@app.get("/health")
def health():
    """Health check endpoint.
    Returns available agents (servers) so frontend can see which are active."""
    return {"ok": True, "servers": list(AGENTS.keys())}

@app.post("/api/nl")
async def run_query(req: Request):
    """Main endpoint to process natural language queries.
    - Expects JSON body with:
        { "query": "...", "max_steps": 30, "server_name": "playwright" }
    - Chooses the agent for the given server_name.
    - Runs the query with the selected agent.
    """
    # Parse request body
    body = await req.json()
    q = body.get("query", "")
    steps = int(body.get("max_steps", 30))
    # Choose server_name, default to playwright if not provided
    server_name = body.get("server_name", "playwright")

    # Validate server_name
    if server_name not in AGENTS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown server_name '{server_name}'. Available: {list(AGENTS.keys())}"
        )

    # Pick the corresponding agent
    agent = AGENTS[server_name]
    try:
        # Run the query through the agent (LLM + selected MCP server)
        result = await agent.run(q, max_steps=steps)
        return {"result": result, "server_used": server_name}
    except Exception as e:
        traceback.print_exc()
        # Return 500 if the agent fails
        raise HTTPException(status_code=500, detail=str(e))
