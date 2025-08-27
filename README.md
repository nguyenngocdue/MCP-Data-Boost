# 🌐 Natural Language MCP-Data-Boost / User Management Demo

A demo application that allows managing users via **natural language commands**.  
You can create, update, delete, and list users just by typing sentences in plain English (or Vietnamese).

---

## ✨ Features

- ✅ **Natural Language Input** – e.g., `"create a user named Alice, email alice@test.com"`
- ✅ **Smart Parsing** – Uses **LLM + MCP tools** to interpret user intent
- ✅ **Fallback CRUD Parser** – Falls back to JSON parsing if tool call fails
- ✅ **Real-time UI** – View and manage users in a clean React interface
- ✅ **Auto-refresh** – User list updates automatically after changes
- ✅ **Clear Instructions** – Built-in tips for supported commands

---

## ⚙️ Supported Actions

| Action                | Example                                                                 |
|-----------------------|-------------------------------------------------------------------------|
| **Create**            | `create a user named Bob, email bob@example.com`                        |
| **Update**            | `update user 1: name Alice` or `change email of user 2 to alice@new.com`|
| **Delete**            | `delete user 3` or `remove user with id 3`                              |
| **List**              | `list all users` or `show users`                                        |
| **Bulk Create**       | `create 5 users named Dev`                                              |
| **Bulk Create Random**| `create 10 random users` · `tạo 3 người dùng ngẫu nhiên` · `make 2 random testers` |
| **None** *(fallback)* | `what is the weather today?` → not related to user management            |

---

## 🔎 How It Works

1. **User Input** – You type a command in natural language, e.g., *"delete user 3"*  
2. **Frontend → Backend** – The request is sent to FastAPI at `/api/users/nl`  
3. **Backend Processing**:
   - First tries to use **MCP tools**  
   - If tools are not available → fallback LLM parser  
   - Executes CRUD operations on `data/users.json`  
4. **Response** – The result is returned, UI refreshes automatically  

🌐 **Remote Queries**:  
If the input is valid but cannot be processed locally (missing data, unsupported action, etc.),  
it is automatically forwarded to the **MCP-use server** for intelligent response handling.  

💡 *Tip*: You can mix chat + command inputs — the system will recognize which is which.  

---

## 🛠️ Tech Stack

- **Frontend** → React + Tailwind CSS + ShadCN UI  
- **Backend** → FastAPI (Python)  
- **LLM** → OpenAI GPT models  
- **Tooling** → [MCP (Model Context Protocol)](https://github.com/isi-mcp), MCP-use  
- **Storage** → Local JSON file (`data/users.json`)  

---

## 🖥️ Run the Backend

Choose one of the server options below (all based on **Uvicorn**):

```bash
  # Simple server
  uvicorn simple_server:app --host 0.0.0.0 --port 8000 --reload

  # Server with customization
  uvicorn server_customization:app --host 0.0.0.0 --port 8000 --reload

  # Multi-agents server
  uvicorn server_multi_agents:app --host 0.0.0.0 --port 8000 --reload

  # Dynamic server
  uvicorn dynamic_server:app --host 0.0.0.0 --port 8000 --reload

  # Dynamic server with customization
  uvicorn dynamic_server_customization:app --host 0.0.0.0 --port 8000 --reload

  # Main API server
  uvicorn main:app --host 0.0.0.0 --port 8000 --reload

👉 The backend will be available at http://localhost:8000
```

---

🌟 Run the Frontend
```bash
  # 1. Navigate to the frontend directory
  cd mcp-json-ui

  # 2. Install dependencies
  npm install

  # 3. Start the development server
  npm run dev

👉 Open your browser at http://localhost:5173
```

---

📂 Server Customization Example

server_customization.py – A customizable MCP server that integrates with tools + local JSON database.
- MCP Tool Hosting: Exposes CRUD as MCP tools
- Natural Language Interface: Free-text commands parsed by LLM
- Persistent Data: Stored in data/users.json
- Integration Ready: Compatible with langchain, mcp SDKs, multi-agent systems

CRUD operations supported:
| Operation     | Description                      |
| ------------- | -------------------------------- |
| `create_user` | Add a new user with name & email |
| `list_users`  | Retrieve all users               |
| `update_user` | Modify name or email by ID       |
| `delete_user` | Remove a user by ID              |

✅ Email uniqueness enforced
✅ IDs auto-incremented
---
📖 Examples (IN → OUT)
```bash
  Ex1 IN:  "create a new user named Minh, email minh@example.com"
  Ex1 OUT: {"action":"create","name":"Minh","email":"minh@example.com"}

  Ex2 IN:  "delete user with id 3"
  Ex2 OUT: {"action":"delete","id":3}

  Ex3 IN:  "update user 2: name Nam, email nam@abc.com"
  Ex3 OUT: {"action":"update","id":2,"name":"Nam","email":"nam@abc.com"}

  Ex4 IN:  "list all users"
  Ex4 OUT: {"action":"list"}

  Ex5 IN:  "what is the weather today?"
  Ex5 OUT: {"action":"none","reason":"Question not related to user management"}

  Ex6 IN:  "create 5 users named Dev"
  Ex6 OUT: {"action":"bulk_create","name":"Dev","count":5}

  Ex7 IN:  "tạo 3 người dùng ngẫu nhiên"
  Ex7 OUT: {"action":"bulk_create_random","count":3}

  Ex8 IN:  "create 10 random users"
  Ex8 OUT: {"action":"bulk_create_random","count":10}

  Ex9 IN:  "make 2 random testers"
  Ex9 OUT: {"action":"bulk_create_random","count":2}

```