/**
 * Polyglot-Liquidity-Hub — Live Stream Dashboard
 * Next.js 14 + TypeScript + HTML5 semantic structure
 */

"use client";

import React, { useEffect, useState } from "react";

interface LatencyRow {
  id: string;
  layer: string;
  language: string;
  latencyMs: number;
  status: "healthy" | "degraded" | "critical";
  updatedAt: number;
}

const LAYERS = [
  { layer: "FIX Adapter", language: "Java 17" },
  { layer: "Channel Router", language: "Go" },
  { layer: "Stream Bridge", language: "Python 3.12" },
  { layer: "UI Cockpit", language: "TypeScript" },
] as const;

function statusClass(status: LatencyRow["status"]): string {
  switch (status) {
    case "healthy":
      return "status-healthy";
    case "degraded":
      return "status-degraded";
    case "critical":
      return "status-critical";
    default:
      return "";
  }
}

export default function Dashboard() {
  const [rows, setRows] = useState<LatencyRow[]>([]);

  useEffect(() => {
    const id = setInterval(() => {
      const now = Date.now();
      const next: LatencyRow[] = LAYERS.map((l, idx) => {
        const base = [1.8, 0.4, 3.2, 6.5][idx];
        const jitter = Math.random() * 1.5;
        const latencyMs = Number((base + jitter).toFixed(2));
        let status: LatencyRow["status"] = "healthy";
        if (latencyMs > 8) status = "critical";
        else if (latencyMs > 4) status = "degraded";

        return {
          id: `\( {l.layer}- \){now}`,
          layer: l.layer,
          language: l.language,
          latencyMs,
          status,
          updatedAt: now,
        };
      });
      setRows(next);
    }, 900);

    return () => clearInterval(id);
  }, []);

  return (
    <main className="dashboard-root">
      <header className="dashboard-header">
        <h1>Polyglot Liquidity Hub</h1>
        <p className="subtitle">
          Enterprise multi-language financial stream engine · Live latency view
        </p>
      </header>

      <section className="table-wrapper" aria-label="Latency monitoring">
        <table className="latency-table">
          <thead>
            <tr>
              <th scope="col">Layer</th>
              <th scope="col">Language</th>
              <th scope="col">Latency (ms)</th>
              <th scope="col">Status</th>
              <th scope="col">Updated</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td>{r.layer}</td>
                <td className="lang">{r.language}</td>
                <td className="numeric">{r.latencyMs.toFixed(2)}</td>
                <td>
                  <span className={`status-pill ${statusClass(r.status)}`}>
                    {r.status}
                  </span>
                </td>
                <td className="numeric">
                  {new Date(r.updatedAt).toLocaleTimeString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <footer className="dashboard-footer">
        Java 17 · Go · Python 3.12 · TypeScript / Next.js · CSS3
      </footer>
    </main>
  );
}
