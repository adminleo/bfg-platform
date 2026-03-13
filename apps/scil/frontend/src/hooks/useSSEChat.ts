"use client";

import { useState, useCallback, useRef } from "react";
import { api } from "@/lib/api";
import type { ChatMessage, SCILScores, PolygonData, ClusterProgress, SSEEvent } from "@/lib/types";

interface UseSSEChatReturn {
  messages: ChatMessage[];
  scores: SCILScores | null;
  polygon: PolygonData | null;
  progress: number;
  clusterProgress: ClusterProgress | null;
  totalScored: number;
  isStreaming: boolean;
  isComplete: boolean;
  resultId: string | null;
  suggestions: string[];
  setSuggestions: (suggestions: string[]) => void;
  sendMessage: (sessionId: string, text: string) => Promise<void>;
  loadConversation: (conversation: Array<{ role: string; content: string }>) => void;
  setScores: (scores: SCILScores | null) => void;
  setPolygon: (polygon: PolygonData | null) => void;
  setClusterProgress: (cp: ClusterProgress | null) => void;
}

let messageIdCounter = 0;
function nextMsgId(): string {
  return `msg-${Date.now()}-${++messageIdCounter}`;
}

export function useSSEChat(): UseSSEChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [scores, setScores] = useState<SCILScores | null>(null);
  const [polygon, setPolygon] = useState<PolygonData | null>(null);
  const [progress, setProgress] = useState(0);
  const [clusterProgress, setClusterProgress] = useState<ClusterProgress | null>(null);
  const [totalScored, setTotalScored] = useState(0);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [resultId, setResultId] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const streamingTextRef = useRef("");

  const loadConversation = useCallback(
    (conversation: Array<{ role: string; content: string }>) => {
      const msgs: ChatMessage[] = conversation.map((m) => ({
        id: nextMsgId(),
        role: m.role as "user" | "assistant",
        content: m.content,
        timestamp: new Date(),
      }));
      setMessages(msgs);
    },
    []
  );

  const sendMessage = useCallback(
    async (sessionId: string, text: string) => {
      // Add user message + clear suggestions
      const userMsg: ChatMessage = {
        id: nextMsgId(),
        role: "user",
        content: text,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setSuggestions([]);
      setIsStreaming(true);
      streamingTextRef.current = "";

      // Create placeholder for assistant response
      const assistantMsgId = nextMsgId();
      const assistantMsg: ChatMessage = {
        id: assistantMsgId,
        role: "assistant",
        content: "",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMsg]);

      try {
        const response = await api.postSSE(
          `/scil/sessions/${sessionId}/message`,
          { content: text }
        );

        if (!response.body) {
          throw new Error("No response body");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const data = line.slice(6).trim();
              if (!data || data === "{}") continue;

              try {
                const event: SSEEvent = JSON.parse(data);

                if (event.type === "agent_text" && event.content) {
                  streamingTextRef.current += event.content;
                  const currentText = streamingTextRef.current;
                  setMessages((prev) =>
                    prev.map((m) =>
                      m.id === assistantMsgId
                        ? { ...m, content: currentText }
                        : m
                    )
                  );
                }

                if (event.type === "scores_update") {
                  if (event.scores) setScores(event.scores);
                  if (event.polygon) setPolygon(event.polygon);
                  if (event.progress !== undefined) setProgress(event.progress);
                }

                if (event.type === "cluster_progress") {
                  if (event.cluster) setClusterProgress(event.cluster);
                  if (event.total_scored !== undefined) setTotalScored(event.total_scored);
                }

                if (event.type === "status" && event.status === "scoring") {
                  setProgress(1.0);
                }

                if (event.type === "suggestions" && event.suggestions) {
                  setSuggestions(event.suggestions);
                }

                if (event.type === "complete") {
                  setIsComplete(true);
                  if (event.result_id) setResultId(event.result_id);
                }
              } catch {
                // Ignore malformed JSON lines
              }
            }
          }
        }
      } catch (e) {
        console.error("SSE error:", e);
        // Update assistant message with error
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantMsgId
              ? { ...m, content: m.content || "Fehler bei der Kommunikation mit dem Server." }
              : m
          )
        );
      } finally {
        setIsStreaming(false);
      }
    },
    []
  );

  return {
    messages,
    scores,
    polygon,
    progress,
    clusterProgress,
    totalScored,
    isStreaming,
    isComplete,
    resultId,
    suggestions,
    setSuggestions,
    sendMessage,
    loadConversation,
    setScores,
    setPolygon,
    setClusterProgress,
  };
}
