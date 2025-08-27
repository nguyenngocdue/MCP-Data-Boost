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
![Alt text](pictures/frontend-main-ui.png)

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

---
## 🔄 MCP Workflow Diagram
```mermaid
flowchart TD
    %% === Styles ===
    classDef start    fill:#ffeb3b,stroke:#333,stroke-width:2px,color:#000;
    classDef step     fill:#bbdefb,stroke:#1a237e,stroke-width:1px,color:#000;
    classDef decision fill:#ffe082,stroke:#ff6f00,stroke-width:1px,color:#000;
    classDef process  fill:#c8e6c9,stroke:#2e7d32,stroke-width:1px,color:#000;
    classDef note     fill:#f5f5f5,stroke:#666,stroke-dasharray: 3 3,color:#000;

    %% === Core Nodes ===
    A[Start] --> B[Load Configuration]
    B --> C[Initialize Servers]
    C --> D[Discover Tools]
    D --> E[Format Tools for LLM]
    E --> F[Wait for User Input]
    
    F --> G{User Input Received?}
    G --> H[Send Input to LLM]
    H --> I{LLM Decision}
    I -->|🔧 Tool Call| J[Execute Tool]
    I -->|💬 Direct Response| K[Return Response to User]
    
    J --> L[Return Tool Result]
    L --> M[Send Result to LLM]
    M --> N[LLM Interprets Result]
    N --> O[Present Final Response to User]
    
    K --> O
    O --> F

    %% === Apply Styles ===
    class A start;
    class B,C,D,E,F step;
    class G,I decision;
    class H,J,L,M,N process;

```


📘 Explanations
```mermaid
flowchart TD
    %% === Styles ===
    classDef start    fill:#ffeb3b,stroke:#333,stroke-width:2px,color:#000;
    classDef step     fill:#bbdefb,stroke:#1a237e,stroke-width:1px,color:#000;
    classDef decision fill:#ffe082,stroke:#ff6f00,stroke-width:1px,color:#000;
    classDef process  fill:#c8e6c9,stroke:#2e7d32,stroke-width:1px,color:#000;
    classDef note     fill:#f5f5f5,stroke:#666,stroke-dasharray: 3 3,color:#000;

    %% === Core Flow (left column) ===
    A[Start] --> B[Load Configuration]
    B --> C[Initialize Servers]
    C --> D[Discover Tools]
    D --> E[Format Tools for LLM]
    E --> F[Wait for User Input]
    F --> G{User Input Received?}
    G --> H[Send Input to LLM]
    H --> I{LLM Decision}
    I -->|🔧 Tool Call| J[Execute Tool]
    I -->|💬 Direct Response| K[Return Response to User]
    J --> L[Return Tool Result]
    L --> M[Send Result to LLM]
    M --> N[LLM Interprets Result]
    N --> O[Present Final Response to User]
    K --> O
    O --> F

    %% === Explanations with Icons (right column) ===
    subgraph EX["📘 Explanations (step-by-step)"]
      direction TB
      EA[🟡 Entry point of the workflow]:::note
      EB[⚙️ Load configuration files: API keys, environment variables, settings]:::note
      EC[⚙️ Initialize server connections for available services]:::note
      ED[🛠️ Discover accessible tools from connected servers]:::note
      EE[🛠️ Prepare tool schemas for LLM consumption]:::note
      EF[⏳ Idle state — waiting for user request]:::note
      EG[❓ Decision — has the user submitted input?]:::note
      EH[📤 Forward the request to the LLM for reasoning]:::note
      EI[❓ Decision — respond directly or invoke a tool]:::note
      EJ[🛠️ Execute the selected tool per LLM instruction]:::note
      EL[📥 Tool returns raw results]:::note
      EM[📤 Send results back to the LLM for interpretation]:::note
      EN[🧠 LLM interprets and structures the final answer]:::note
      EK[💬 Direct-answer path without tool usage]:::note
      EO[💬 Deliver a polished response to the user]:::note

      %% Keep vertical order
      EA --> EB --> EC --> ED --> EE --> EF --> EG --> EH --> EI --> EJ --> EL --> EM --> EN --> EK --> EO
    end

    %% === Dotted links (horizontal mapping) ===
    A -.-> EA
    B -.-> EB
    C -.-> EC
    D -.-> ED
    E -.-> EE
    F -.-> EF
    G -.-> EG
    H -.-> EH
    I -.-> EI
    J -.-> EJ
    L -.-> EL
    M -.-> EM
    N -.-> EN
    K -.-> EK
    O -.-> EO

    %% === Apply Styles ===
    class A start;
    class B,C,D,E,F step;
    class G,I decision;
    class H,J,L,M,N process;

“Please refer to the chart at this link: 
[![View in Mermaid Live Editor](https://mermaid.live/edit#pako:eNqVVs1uGzcQfhVigwAJsDIky_rxFmlgSytbtuwEsYsWXflA7XIlwityS3Ity46BvkGAOof-oHAKtMilt176PH6B5hE6JHdXkuUWiHzwDjnzcWY48w2vnZBHxPGcOOGzcIKFQqfdIUPwe_oUvXjxAp2oeUKk_rTLYYKl7JIYSaW14RfTJPGexDEZ1UeuVIKfE-9JvV7PvyszGqmJt5leuiFPuPCeVKvVL9bASIoWYKNRROIFWA1v1ltkFa_2v3gRCamknC2cq7Y3S7w4bsbV6ufgpYKHRMrCv7BNmuF2ibdJWlF983PwGFdkKd64of9KvGazWYBFWMKtCDz3UB3VVxFX7qnDBUE9uEX0LCGxQqCZTdnzxcXtBCf6xs5QpfIl2g0GHEdgxGI6zgRWkKszq7drFDpBn1FFcUKvCDoh4oIImSt0jEI36FIZclhHp5wnxWbXbPpBj4spVnYLxVygweAoV_GNSi_4GlNltr6SANJnaaZyjZ7R2LtebKA3JCT0gkQvb6zKnlHZD04Ii3IVxZcO2Tf7_WtYQd28GHLTvt56--nu_UfjHurgJHmLDgL_koQZXItePFtV_eFP1KWChNoPmXImyVt0GLwhKhOsXNIOaI9z2wPjwaDQMkeBapYUUQ6MwpENwe6sxnBkFI4DHUOfKSJSQZRcBTk2Oq-C14JIwhTqUYaT_3Lp0Cpb4ZW9hgdl5F-mCWamHiSaUTVB_VB_PhN0PHmkqmQ2GgucTpD_TTB0Pt3d_rgK8Ux3dmU0r-j_z4dO7glCkcmnbtHT3WLN3wk-3d39hnymxBylnEJAPEZqQtCMi3PNUWee5-nmKU12g_uff_rn73fIFHS4XNC6uYj00M7rPjonc-kiwi6o4GyqM3WBBcUjUHCRJEpRNpZr4J0CfKkZpGkGfRKzAdj6xheYJhrPKFBgizW0LkT3ywcNV7YODjWtUG2mbKsIPi2wSZQftg7ll1Bw8SkW1hzJcEKmuGw4DSSzaWq6-yFEL7h_9xfqR9pjhaHu779_j2bQk5AJA5Dp7hPku4xItWa9F9z_elt2lrGdwMH6qowd1MWUKh0C1c35cg1gHyK4_R0BT8ywiIxhfpYuWi3qALQfgmDJGXi1htFfd0KYyo_y8krmCAAouwAqRdjkaA3koExlQQD6cEkSewMmrymx-aQMaDkLH83nQAf0h-1zYXpeIoFn2iNo1_UrPLIJMN2f66ARDs8fhk-LzsePHnsMMB8_5N6VHIEB1LqaAbbBiw0zYCZnwAcPUQ6DJZKrWCWUYmh_zQHcsCvElUk8JmvGr3JjklBT09C5CZUTEuW3YXmoKI2FeQEA1HNIYP6DsaIhOMlFRMSCFOxIsXPJt9PHz-eMnSW-HRi-HQq-5X6_b_9ZHvYt2_qWU31Lm74lRD9nRLiJB2zY5aaEE8rOgcomXNArzhR4OMVpChW5PF5RZUNj7ZRT1Ii75cw0YqeckkbslhPRiH45_ozYK0edEffKyWbE_XJEGbFfTh0jHpQzxoiDcqIY8agcHkY8LseDEQ_LAbGRZ2clKTtpCn316LsQsmCehcvPHbTrdtyu67s988pb2dpz--VTbWVj3z1wB-6Re1y8vGDXcZ2xoJHjQV0T15kSeGFo0bnWlkMHCmxKho4HnxEW50NnyG7AJsXsW86nhZng2XjieDFOJEhZGgH1dSmGITYtVwVUAhEdnjHleLXmlgFxvGvnEsRGe2Oz1diu1bYa1fZ2G55qzhyWq_WN6laj3txqbFcbtXqjdeM6V-bc2kZra7vVaDdr7cZWvVWt3_wLjsSrnA)]