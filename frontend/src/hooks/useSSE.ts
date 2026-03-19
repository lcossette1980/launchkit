import { useEffect, useRef, useState } from "react";
import type { JobStatus } from "../types/api";

interface LogEntry {
  time: string;
  message: string;
}

interface QuickResults {
  website_analysis?: {
    overall_scores?: Record<string, number>;
    top_strengths?: string[];
    top_weaknesses?: string[];
    quick_wins?: string[];
  };
}

interface SSEState {
  progress: number;
  step: string;
  status: JobStatus | null;
  error: string | null;
  logs: LogEntry[];
  quickResults: QuickResults | null;
}

export function useSSE(jobId: string | null) {
  const [state, setState] = useState<SSEState>({
    progress: 0,
    step: "starting",
    status: null,
    error: null,
    logs: [],
    quickResults: null,
  });
  const esRef = useRef<EventSource | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!jobId) return;

    setState({ progress: 0, step: "starting", status: null, error: null, logs: [], quickResults: null });

    // SSE connection
    const es = new EventSource(`/api/v1/analyses/${jobId}/stream`);
    esRef.current = es;

    es.addEventListener("progress", (e) => {
      const data = JSON.parse(e.data);
      setState((prev) => ({
        ...prev,
        progress: data.pct ?? prev.progress,
        step: data.step ?? prev.step,
        logs: data.message
          ? [...prev.logs, { time: new Date().toLocaleTimeString(), message: data.message }]
          : prev.logs,
      }));
    });

    es.addEventListener("quick_results", (e) => {
      const data = JSON.parse(e.data);
      setState((prev) => ({
        ...prev,
        quickResults: data.results ?? null,
        logs: data.message
          ? [...prev.logs, { time: new Date().toLocaleTimeString(), message: data.message }]
          : prev.logs,
      }));
    });

    es.addEventListener("complete", () => {
      setState((prev) => ({ ...prev, status: "completed", progress: 100 }));
      es.close();
    });

    es.addEventListener("error_event", (e) => {
      const data = JSON.parse(e.data);
      setState((prev) => ({ ...prev, status: "failed", error: data.message }));
      es.close();
    });

    es.onerror = () => es.close();

    // Polling fallback
    const poll = setInterval(async () => {
      try {
        const res = await fetch(`/api/v1/analyses/${jobId}/status`, { credentials: "include" });
        if (!res.ok) return;
        const data = await res.json();
        setState((prev) => ({
          ...prev,
          progress: data.progress_pct,
          step: data.current_step,
          status: data.status,
          error: data.error_message,
          // Pick up quick_results from the status endpoint (polling fallback)
          quickResults: data.quick_results ?? prev.quickResults,
        }));
        if (data.status === "completed" || data.status === "failed") {
          clearInterval(poll);
        }
      } catch { /* ignore */ }
    }, 3000);
    pollRef.current = poll;

    return () => {
      es.close();
      clearInterval(poll);
    };
  }, [jobId]);

  return state;
}
