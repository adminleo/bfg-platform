"use client";

import ReactMarkdown from "react-markdown";
import type { ChatMessage as ChatMessageType } from "@/lib/types";

interface ChatMessageProps {
  message: ChatMessageType;
  isStreaming?: boolean;
}

export function ChatMessage({ message, isStreaming }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={`message-enter flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}
    >
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ring-1 ring-white/[0.08] ${
          isUser
            ? "bg-white/[0.06] text-slate-200"
            : "bg-gradient-to-br from-scil to-scil-dark text-white shadow-glow-sm"
        }`}
      >
        {isUser ? "Du" : "&#x1F98E;"}
      </div>

      {/* Message Bubble */}
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-white/[0.06] border border-white/[0.06] text-slate-100"
            : "bg-white/[0.03] border border-white/[0.04] text-slate-200"
        }`}
      >
        {isUser ? (
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="text-sm prose prose-invert prose-sm max-w-none prose-p:my-1 prose-li:my-0.5">
            <ReactMarkdown>{message.content}</ReactMarkdown>
            {isStreaming && message.content.length > 0 && (
              <span className="inline-block w-1.5 h-4 bg-scil animate-pulse ml-0.5 rounded-sm" />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
