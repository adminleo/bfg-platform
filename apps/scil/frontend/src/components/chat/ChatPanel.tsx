"use client";

import { useRef, useEffect } from "react";
import { ChatMessage } from "@/components/chat/ChatMessage";
import { ChatInput } from "@/components/chat/ChatInput";
import type { ChatMessage as ChatMessageType } from "@/lib/types";

interface ChatPanelProps {
  messages: ChatMessageType[];
  isStreaming: boolean;
  isComplete: boolean;
  progress: number;
  onSendMessage: (text: string) => void;
  onStartSession: () => void;
  hasSession: boolean;
  suggestions?: string[];
  onSelectSuggestion?: (text: string) => void;
}

export function ChatPanel({
  messages,
  isStreaming,
  isComplete,
  progress,
  onSendMessage,
  onStartSession,
  hasSession,
  suggestions = [],
  onSelectSuggestion,
}: ChatPanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isStreaming]);

  return (
    <div className="flex flex-col h-full">
      {/* Progress bar */}
      {hasSession && progress > 0 && !isComplete && (
        <div className="h-0.5 bg-black/[0.02]">
          <div
            className="h-full bg-gradient-to-r from-scil to-scil-light transition-all duration-500 ease-out"
            style={{ width: `${progress * 100}%` }}
          />
        </div>
      )}

      {/* Messages area */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-6 pt-12">
        {!hasSession ? (
          /* Empty state — no session */
          <div className="flex items-center justify-center h-full animate-fade-in">
            <div className="text-center max-w-md">
              <div className="text-6xl mb-4 animate-float">&#x1F98E;</div>
              <h1 className="text-2xl font-bold text-slate-900 mb-2">
                S.C.I.L. Diagnostik
              </h1>
              <p className="text-slate-500 mb-6">
                Entdecke dein Wirkungsprofil in einem KI-gestuetzten Gespraech.
                16 Frequenzen. 4 Bereiche. Deine Staerken.
              </p>
              <button
                onClick={onStartSession}
                className="px-6 py-3 btn-glass text-white rounded-xl font-medium transition-all text-lg"
              >
                Diagnostik starten
              </button>
            </div>
          </div>
        ) : messages.length === 0 ? (
          /* Loading state */
          <div className="flex items-center justify-center h-full">
            <div className="flex gap-1">
              <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
              <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
              <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
            </div>
          </div>
        ) : (
          /* Message list */
          <div className="max-w-3xl mx-auto space-y-4">
            {messages.map((msg) => (
              <ChatMessage
                key={msg.id}
                message={msg}
                isStreaming={
                  isStreaming &&
                  msg.role === "assistant" &&
                  msg.id === messages[messages.length - 1]?.id
                }
              />
            ))}

            {/* Streaming indicator */}
            {isStreaming &&
              messages.length > 0 &&
              messages[messages.length - 1]?.role === "user" && (
                <div className="flex items-center gap-2 text-slate-500">
                  <div className="flex gap-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-scil typing-dot" />
                    <div className="w-1.5 h-1.5 rounded-full bg-scil typing-dot" />
                    <div className="w-1.5 h-1.5 rounded-full bg-scil typing-dot" />
                  </div>
                </div>
              )}
          </div>
        )}
      </div>

      {/* Suggestion chips */}
      {hasSession && !isComplete && suggestions.length > 0 && !isStreaming && (
        <div className="border-t border-black/[0.06] px-4 py-2.5">
          <div className="max-w-3xl mx-auto flex flex-wrap gap-2">
            {suggestions.map((text, i) => (
              <button
                key={`${text.slice(0, 20)}-${i}`}
                onClick={() => onSelectSuggestion?.(text)}
                className="px-3.5 py-2 btn-ghost rounded-full text-xs text-slate-600 hover:text-slate-900 transition-all duration-200 hover:border-scil/40 hover:shadow-sm hover:shadow-scil/10"
              >
                {text}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input area */}
      {hasSession && !isComplete && (
        <div className="border-t border-black/[0.06] glass-subtle px-4 py-3">
          <div className="max-w-3xl mx-auto">
            <ChatInput
              onSend={onSendMessage}
              disabled={isStreaming}
              placeholder="Deine Antwort..."
            />
          </div>
        </div>
      )}

      {/* Completed state */}
      {isComplete && (
        <div className="border-t border-black/[0.06] glass-subtle px-4 py-3">
          <div className="max-w-3xl mx-auto text-center text-sm text-slate-500">
            &#x2713; Diagnostik abgeschlossen &mdash; Ergebnisse in der rechten Sidebar
          </div>
        </div>
      )}
    </div>
  );
}
