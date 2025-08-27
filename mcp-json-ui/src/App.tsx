// // src/App.tsx
// import { useState } from "react";

import { AgentPanel } from "./users/AgentPanel";
import { UsersNLPanel } from "./users/UsersNLPanel";

export default function App() {
  return (
    <>
      {/* Exploring about MCP-use */}
      <div className="container p-6 mx-auto space-y-6 font-sans">
        <h1 className="text-2xl font-bold">MCP UI (Vite + shadcn/ui) - Natural Language (NL)</h1>
        <AgentPanel />
        <UsersNLPanel />
      </div>
    </>
  );
}
