# mcp/agent.py
class MCPAgent:
    def __init__(self, llm, client, max_steps=30):
        self.llm = llm
        self.client = client
        self.max_steps = max_steps

    async def run(self, query: str, max_steps: int = None) -> str:
        steps = max_steps or self.max_steps
        print(f"[MCPAgent] Running for '{query}' with {steps} steps")

        # Giả lập: hỏi LLM xem có cần dùng tool không
        prompt = f"""
        User asks: {query}
        If this requires browsing, searching, or external data, use the browser tool.
        Otherwise, answer directly.
        """
        msg = [{"role": "user", "content": prompt}]
        resp = await self.llm.ainvoke(msg)
        answer = resp.content

        # Giả lập gọi tool nếu cần
        if any(kw in query.lower() for kw in ["weather", "news", "search", "find", "what is"]):
            tool_resp = await self.client.query(query)
            answer = f"[From browser]\n{tool_resp}"

        return answer