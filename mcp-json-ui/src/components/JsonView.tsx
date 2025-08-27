// src/components/JsonView.tsx
import React from "react";
import SyntaxHighlighter from "react-syntax-highlighter";
import { a11yDark } from "react-syntax-highlighter/dist/esm/styles/hljs";

type JsonViewProps = {
  data: any;
  language?: "json" | "javascript";
  maxHeight?: string; // Tùy chọn: giới hạn chiều cao
  showCopyButton?: boolean; // Tùy chọn: nút copy
};

export default function JsonView({
  data,
  language = "json",
  maxHeight = "400px",
  showCopyButton = true,
}: JsonViewProps) {
  const json = typeof data === "string" ? data : JSON.stringify(data, null, 2);
  const [copied, setCopied] = React.useState(false);

  const handleCopy = () => {
    navigator.clipboard
      .writeText(json)
      .then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      })
      .catch((err) => console.error("Failed to copy:", err));
  };

  return (
    <div
      className="json-view-container"
      style={{
        position: "relative",
        borderRadius: "0.5rem",
        border: "1px solid #e5e7eb",
        overflow: "hidden",
        background: "#1e1e1e",
        boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
      }}
    >
      {/* Header */}
      <div
        style={{
          backgroundColor: "#2d2d2d",
          color: "#ffffff",
          fontSize: "0.75rem",
          padding: "0.5rem 0.75rem",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <span>JSON Output</span>
        {showCopyButton && (
          <button
            onClick={handleCopy}
            style={{
              background: copied ? "#10b981" : "#6b7280",
              color: "white",
              border: "none",
              borderRadius: "0.25rem",
              padding: "0.25rem 0.5rem",
              fontSize: "0.75rem",
              cursor: "pointer",
              transition: "background 0.2s",
            }}
            title="Copy to clipboard"
          >
            {copied ? "✅ Copied!" : "📋 Copy"}
          </button>
        )}
      </div>

      {/* Syntax Highlighted JSON */}
      <div style={{ maxHeight, overflow: "auto" }}>
        <SyntaxHighlighter
          language={language}
          style={a11yDark}
          customStyle={{
            margin: 0,
            padding: "1rem",
            fontSize: "0.875rem",
            lineHeight: 1.6,
            background: "transparent",
            borderRadius: "0",
            overflow: "auto",
          }}
          wrapLongLines
          codeTagProps={{
            style: {
              fontFamily: "Consolas, Monaco, 'Courier New', monospace",
            },
          }}
        >
          {json}
        </SyntaxHighlighter>
      </div>
    </div>
  );
}