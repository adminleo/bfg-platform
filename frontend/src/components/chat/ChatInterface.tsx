"use client";

import { useState, useRef, useEffect } from "react";

interface Message {
  role: "user" | "agent";
  content: string;
}

interface ChatInterfaceProps {
  wsUrl: string;
  title: string;
  onPolygonUpdate?: (data: any) => void;
  onComplete?: (result: any) => void;
}

export function ChatInterface({ wsUrl, title, onPolygonUpdate, onComplete }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isConnected, setIsConnected] = useState(false);
  const [progress, setProgress] = useState(0);
  const wsRef = useRef<WebSocket | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => setIsConnected(true);
    ws.onclose = () => setIsConnected(false);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "agent_message") {
        setMessages((prev) => [...prev, { role: "agent", content: data.content }]);
        if (data.progress) setProgress(data.progress);
        if (data.polygon_update && onPolygonUpdate) onPolygonUpdate(data.polygon_update);
      }

      if (data.type === "result" && onComplete) {
        onComplete(data);
      }
    };

    wsRef.current = ws;
    return () => ws.close();
  }, [wsUrl]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = () => {
    if (!input.trim() || !wsRef.current) return;

    setMessages((prev) => [...prev, { role: "user", content: input }]);
    wsRef.current.send(JSON.stringify({ content: input }));
    setInput("");
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between bg-slate-50">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? "bg-gr8-neon" : "bg-red-400"}`} />
          <span className="font-medium text-sm text-gr8-navy">{title}</span>
        </div>
        {progress > 0 && (
          <div className="flex items-center gap-2">
            <div className="w-32 h-1.5 bg-slate-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-gr8-purple via-gr8-neon to-gr8-purple rounded-full transition-all duration-500"
                style={{ width: `${progress * 100}%` }}
              />
            </div>
            <span className="text-xs text-slate-400">{Math.round(progress * 100)}%</span>
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 chat-scroll">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                msg.role === "user"
                  ? "bg-gr8-navy text-white"
                  : "bg-slate-100 text-slate-700"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-slate-200">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Nachricht eingeben..."
            className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:border-gr8-purple transition-colors"
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || !isConnected}
            className="px-4 py-2.5 bg-gr8-navy hover:bg-gr8-navy-light disabled:opacity-50 text-white rounded-xl text-sm font-medium transition-colors"
          >
            Senden
          </button>
        </div>
      </div>
    </div>
  );
}
