
-------------------
# Natural Language User Management Demo
A simple demo application that allows managing users via **natural language commands** using:
- **FastAPI backend** with LLM-powered parsing (OpenAI + MCP tools)
- **React frontend** with a user-friendly interface
- Fallback logic for CRUD operations when tools aren't available

This project demonstrates how natural language can be used to perform database-like operations (Create, Read, Update, Delete) without writing code.

---

## 🧩 Features

- ✅ **Natural Language Input**: Type commands like `"create a user named Alice, email alice@test.com"`
- ✅ **Smart Parsing**: Uses LLM + MCP tools to interpret and execute user intent
- ✅ **Fallback CRUD Parser**: If tools fail, falls back to structured JSON parsing
- ✅ **Real-time UI**: View and manage users in a clean, responsive interface
- ✅ **Auto-refresh**: User list updates automatically after create/update/delete
- ✅ **Clear Instructions**: Built-in tips to guide users on supported commands

---

## 🚀 How It Works

1. You type a command in plain English (e.g., *"delete user 3"*)
2. The frontend sends it to the FastAPI backend at `/api/users/nl`
3. The backend:
   - First tries to handle it using **MCP tools** (if configured)
   - If not, uses an LLM to **parse the intent** into a structured action
   - Executes the CRUD operation on `data/users.json`
4. The result is returned and the user list is refreshed automatically.

---

## 💬 Supported Commands
You can use variations of these formats:

| Action  | Example |
|--------|--------|
| **Create** | `create a user named Bob, email bob@example.com` |
| **Update** | `update user 1: name Alice` or `change email of user 2 to alice@new.com` |
| **Delete** | `delete user 3` or `remove user with id 3` |
| **List**   | `list all users` or `show users` |

> 💡 Tip: Keep commands simple and include clear keywords like `create`, `update`, `email`, `id`.

---

## 🛠️ Tech Stack

- **Frontend**: React + Tailwind CSS + ShadCN UI
- **Backend**: FastAPI (Python)
- **LLM**: OpenAI (GPT model for parsing & reasoning)
- **Tooling**: [MCP (Model Context Protocol)](https://github.com/isi-mcp) for tool integration
- **Storage**: Local JSON file (`data/users.json`)

---

How to run

uvicorn simple_server:app --host 0.0.0.0 --port 8000 --reload
uvicorn server_customization:app --host 0.0.0.0 --port 8000 --reload
uvicorn server_multi_agents:app --host 0.0.0.0 --port 8000 --reload
uvicorn dynamic_server:app --host 0.0.0.0 --port 8000 --reload
uvicorn dynamic_server_customization:app --host 0.0.0.0 --port 8000 --reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload


#####

|||||||||||||||||||||||||||||||||||||server_customization.py|||||||||||||||||||||||||||||||||||||
# `server_customization.py` – Customizable MCP Server with LLM-Powered User Management
Run server:
uvicorn server_customization:app --host 0.0.0.0 --port 8000 --reload

This server is designed to demonstrate a **customizable Model Context Protocol (MCP) host** that integrates with external tools and a local database (simulated via JSON) to support **natural language CRUD operations** on user data.

## 🧩 Overview

- **Purpose**: Enable users to perform Create, Read, Update, and Delete (CRUD) operations on a user database using natural language.
- **Core Tech**:
  - FastAPI (backend server)
  - OpenAI's `ChatOpenAI` (LLM for intent parsing and reasoning)
  - MCP (Model Context Protocol) for tool integration
  - Local JSON file (`data/users.json`) as persistent storage

## 🛠️ Key Features

### 1. **MCP Tool Hosting**
- The server acts as an **MCP host**, allowing external agents (like `MCPClient`) to discover and invoke tools.
- Exposes CRUD operations as MCP tools that can be called by LLM agents.

### 2. **Natural Language Interface**
- Accepts free-text queries (e.g., *"create a user named Alice, email alice@test.com"*)
- Uses `ChatOpenAI` to interpret user intent
- Falls back to structured parsing if direct tool calls fail

### 3. **User Data Management (CRUD)**
All operations are persisted in `data/users.json`:

| Operation | Description |
|---------|-------------|
| `create_user` | Add a new user with name and email |
| `list_users`  | Retrieve all users |
| `update_user` | Modify name or email by ID |
| `delete_user` | Remove a user by ID |

> ✅ Email uniqueness is enforced.  
> ✅ IDs are auto-incremented.

### 4. **Integration with External Agents**
- Can be used as a backend for:
  - Autonomous agents
  - AI assistants
  - Multi-agent systems
- Compatible with `langchain` and `mcp` SDKs

