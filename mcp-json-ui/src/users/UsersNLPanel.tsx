import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/card";
import { Textarea } from "../components/ui/textarea";
import { Button } from "../components/ui/button";
import { ScrollArea } from "../components/ui/scroll-area";
import { Separator } from "../components/ui/separator";

type User = { id: number; name: string; email: string };
const API = "http://localhost:8000";

export function UsersNLPanel() {
  const [nlQ, setNlQ] = useState("I want to create a new user named Nissan, email Nissan@example.com");
  const [nlRes, setNlRes] = useState<string>("");
  const [users, setUsers] = useState<User[]>([]);
  const [busy, setBusy] = useState(false);

  const loadUsers = async () => {
    setBusy(true);
    try {
      const r = await fetch(`${API}/api/users`);
      const j = await r.json();
      setUsers(j ?? []);
    } finally {
      setBusy(false);
    }
  };

  const runUsersNL = async () => {
    setNlRes("Processing...");
    try {
      const r = await fetch(`${API}/api/users/nl`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: nlQ }),
      });
      const j = await r.json();
      setNlRes(JSON.stringify(j, null, 2));
      if (j?.action && ["create", "update", "delete"].includes(j.action)) {
        await loadUsers(); // Refresh user list if data changed
      }
    } catch (e: any) {
      setNlRes(`Error: ${e?.message ?? String(e)}`);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Users (Natural Language) — /api/users/nl</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Natural Language Input */}
        <div className="space-y-2">
          <Textarea
            value={nlQ}
            onChange={(e) => setNlQ(e.target.value)}
            placeholder="Enter your command in natural language..."
            className="min-h-[100px] font-mono text-sm"
          />
          {/* Instructions */}
          <div className="text-xs text-gray-500 space-y-2">
            <p><strong>💡 Tips & Guidelines:</strong> This interface supports natural language commands for managing users. Use clear, simple actions to trigger CRUD operations.</p>

            <ul className="list-disc list-inside ml-2 space-y-1">
              <li>
                <code className="bg-gray-100 px-1 rounded">create a user named Alice, email alice@test.com</code>
                <span className="text-gray-600 text-xs block ml-1">→ Adds a new user with specified details.</span>
              </li>
              <li>
                <code className="bg-gray-100 px-1 rounded">update user 1: name Bob</code>
                <span className="text-gray-600 text-xs block ml-1">→ Modifies the name of user ID 1.</span>
              </li>
              <li>
                <code className="bg-gray-100 px-1 rounded">update user 2: email new@x.com</code>
                <span className="text-gray-600 text-xs block ml-1">→ Changes the email of user ID 2.</span>
              </li>
              <li>
                <code className="bg-gray-100 px-1 rounded">delete user 3</code>
                <span className="text-gray-600 text-xs block ml-1">→ Removes user ID 3 permanently.</span>
              </li>
              <li>
                <code className="bg-gray-100 px-1 rounded">list all users</code> or <code className="bg-gray-100 px-1 rounded">show users</code>
                <span className="text-gray-600 text-xs block ml-1">→ Displays the full list of current users.</span>
              </li>
            </ul>

            <p><strong>✅ How It Works:</strong> The system parses your input in real time. If your message matches a known command pattern, it will execute the appropriate action locally.</p>

            <p><strong>🔧 Need Help?</strong> Stick to simple sentences using keywords like <strong>create, update, delete, list, show</strong>. Be specific with names, IDs, and values.</p>

            <div className="bg-blue-50 border border-blue-200 p-2 rounded mt-2">
              <p className="text-blue-800 font-medium text-xs mb-1">🌐 Remote Queries:</p>
              <p className="text-blue-700 text-xs">
                If your input is a valid command but <strong>cannot be processed locally</strong> (e.g., due to missing data, unsupported action, or server limitations), it will be automatically forwarded to the <strong>MCP-use server</strong> for intelligent response handling.
              </p>
              <p className="text-blue-700 text-xs mt-1">
                Example: Asking <code className="bg-white px-1 rounded text-xs">Hello!</code> will return a friendly automated reply from the remote AI service.
              </p>
            </div>

            <p className="text-xs text-gray-500 italic">
              Tip: You can mix command and chat inputs — the system knows which is which!
            </p>
          </div>

        </div>

        {/* Buttons */}
        <div className="flex gap-2">
          <Button onClick={runUsersNL}>Run Users NL</Button>
          <Button variant="outline" onClick={loadUsers}>Refresh Users</Button>
        </div>

        <Separator />

        {/* Results & Users Display */}
        <div className="grid grid-cols-2 gap-3">
          {/* API Response */}
          <ScrollArea className="h-48 p-3 bg-white border rounded-md">
            <h3 className="text-sm font-semibold mb-1">API Response</h3>
            <pre className="text-xs whitespace-pre-wrap text-blue-800">
              {nlRes || "Result will appear here..."}
            </pre>
          </ScrollArea>

          {/* Current Users List */}
          <ScrollArea className="h-48 p-3 bg-white border rounded-md">
            <h3 className="flex items-center justify-between mb-2 font-semibold text-sm">
              Users in Database
              {busy && <span className="text-xs text-gray-500">loading…</span>}
            </h3>
            <ul className="space-y-1 text-sm">
              {users.map((u) => (
                <li key={`${u.id}-${u.name}`} className="flex justify-between pb-1 border-b border-gray-200">
                  <span>#{u.id} {u.name}</span>
                  <span className="text-gray-600">&lt;{u.email}&gt;</span>
                </li>
              ))}
              {!users.length && <li className="text-gray-400 text-center py-2">(no users)</li>}
            </ul>
          </ScrollArea>
        </div>
      </CardContent>
    </Card>
  );
}