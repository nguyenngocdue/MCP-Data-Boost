import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/card";
import { Textarea } from "../components/ui/textarea";
import { Button } from "../components/ui/button";
import { ScrollArea } from "../components/ui/scroll-area";
import { Separator } from "../components/ui/separator";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "../components/ui/select";

const API = "http://localhost:8000";

// Danh sách server bạn cấu hình trong MCPClient (sửa tùy môi trường bạn)
const SERVERS = ["playwright", "airbnb", "github"];

export function AgentPanel() {
  const [query, setQuery] = useState("Hey, how are you?");
  const [result, setResult] = useState<string>("");
  const [serverName, setServerName] = useState<string>(SERVERS[0]); // default: "playwright"

  const runAgent = async () => {
    try {
      setResult("Running...");
      const r = await fetch(`${API}/api/nl`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query,
          max_steps: 30,
          server_name: serverName, // <-- gửi kèm server_name
        }),
      });
      const j = await r.json();
      setResult(j.result ?? JSON.stringify(j, null, 2));
    } catch (e: any) {
      setResult(`Error: ${e?.message ?? String(e)}`);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Agent (MCP) — /api/nl</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Dropdown chọn server */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Server (MCP-use):</span>
          <Select value={serverName} onValueChange={setServerName}>
            <SelectTrigger className="w-[220px]">
              <SelectValue placeholder="Choose server" />
            </SelectTrigger>
            <SelectContent>
              {SERVERS.map((s) => (
                <SelectItem key={s} value={s}>
                  {s}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <Textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="min-h-[120px]"
          placeholder="Type your agent prompt..."
        />

        <Button onClick={runAgent}>Run Agent</Button>
        <Separator />

        <ScrollArea className="h-48 p-3 bg-white border rounded-md">
          <pre className="text-sm whitespace-pre-wrap">{result}</pre>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
