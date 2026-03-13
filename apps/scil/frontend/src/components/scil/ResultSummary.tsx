"use client";

import ReactMarkdown from "react-markdown";
import type { DiagnosticResult } from "@/lib/types";

interface ResultSummaryProps {
  result: DiagnosticResult;
}

export function ResultSummary({ result }: ResultSummaryProps) {
  return (
    <div className="bg-surface rounded-xl p-4">
      <div className="text-xs text-slate-400 mb-3">Zusammenfassung</div>
      <div className="prose prose-invert prose-sm max-w-none prose-p:my-1 prose-li:my-0.5 prose-headings:text-slate-200">
        <ReactMarkdown>{result.summary}</ReactMarkdown>
      </div>

      {result.recommendations.length > 0 && (
        <div className="mt-4 pt-3 border-t border-border">
          <div className="text-xs text-slate-400 mb-2">Entwicklungsfelder</div>
          <div className="space-y-2">
            {result.recommendations.map((rec, i) => (
              <div key={i} className="flex items-center gap-2 text-xs">
                <span className="text-yellow-400">↑</span>
                <span className="text-slate-300">{rec.label}</span>
                <span className="text-slate-500">({rec.current_score.toFixed(1)})</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
