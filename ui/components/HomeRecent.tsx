"use client";

import { useEffect, useMemo, useState } from "react";
import { apiUrl } from "@/lib/api";
import { Clock } from "lucide-react";

type PortItem = {
  name: string;
  version?: string | null;
  description?: string | null;
  categories?: string[];
  modified?: string | null;
};

function normalizePorts(data: any): PortItem[] {
  const arr =
    Array.isArray(data)
      ? data
      : Array.isArray(data?.results)
      ? data.results
      : Array.isArray(data?.ports)
      ? data.ports
      : [];

  const items: PortItem[] = arr
    .map((it: any) => {
      const name: string | undefined =
        typeof it?.name === "string"
          ? it.name
          : typeof it?.port === "string"
          ? it.port
          : typeof it?.portname === "string"
          ? it.portname
          : undefined;

      if (!name) return null;

      const version =
        typeof it?.version === "string"
          ? it.version
          : typeof it?.active_version === "string"
          ? it.active_version
          : typeof it?.latest === "string"
          ? it.latest
          : null;

      const description =
        typeof it?.description === "string"
          ? it.description
          : typeof it?.long_description === "string"
          ? it.long_description
          : typeof it?.desc === "string"
          ? it.desc
          : null;

      const categories: string[] | undefined = Array.isArray(it?.categories)
        ? it.categories.filter((c: any) => typeof c === "string")
        : typeof it?.category === "string"
        ? [it.category]
        : undefined;

      const modified: string | null =
        typeof it?.modified === "string"
          ? it.modified
          : typeof it?.last_modified === "string"
          ? it.last_modified
          : typeof it?.updated === "string"
          ? it.updated
          : null;

      return { name, version, description, categories, modified };
    })
    .filter(Boolean);

  // Sort by modified desc if present
  items.sort((a, b) => {
    const da = a.modified ? Date.parse(a.modified) : 0;
    const db = b.modified ? Date.parse(b.modified) : 0;
    return db - da;
  });

  return items;
}

export default function HomeRecent() {
  const [ports, setPorts] = useState<PortItem[] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;
    (async () => {
      setLoading(true);
      try {
        // Try a simple limit parameter; server may ignore unknown params
        const res = await fetch(apiUrl("/ports/?limit=12"));
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const normalized = normalizePorts(data).slice(0, 12);
        if (alive) setPorts(normalized);
      } catch {
        if (alive) setPorts([]);
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  const content = useMemo(() => {
    if (loading) {
      return (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-4 w-1/2 rounded bg-gray-200 dark:bg-white/10" />
              <div className="mt-2 h-3 w-4/5 rounded bg-gray-100 dark:bg-white/5" />
              <div className="mt-4 flex gap-2">
                <div className="h-5 w-14 rounded bg-gray-200 dark:bg-white/10" />
                <div className="h-5 w-16 rounded bg-gray-200 dark:bg-white/10" />
              </div>
            </div>
          ))}
        </div>
      );
    }

    if (!ports || ports.length === 0) {
      return (
        <div className="card">
          <p className="text-gray-600 dark:text-white/70">No recent updates available right now. Try searching above.</p>
        </div>
      );
    }

    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {ports.map((p) => (
          <a
            key={p.name}
            className="card group"
            href={`https://ports.macports.org/port/${encodeURIComponent(p.name)}/`}
            target="_blank"
            rel="noreferrer"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <div className="truncate font-semibold">{p.name}</div>
                <div className="mt-1 text-sm text-gray-600 dark:text-white/70 line-clamp-2">
                  {p.description ?? "No description provided."}
                </div>
                <div className="mt-2 flex flex-wrap gap-2 text-xs">
                  {p.version ? (
                    <span className="tag-info">v{p.version}</span>
                  ) : null}
                  {p.categories?.slice(0, 2).map((c) => (
                    <span key={c} className="tag-muted">
                      {c}
                    </span>
                  ))}
                </div>
              </div>
              <div className="shrink-0 text-right text-xs text-gray-500 dark:text-white/60">
                <div className="inline-flex items-center gap-1">
                  <Clock className="h-3.5 w-3.5 text-brand-300" />
                  <span>
                    {p.modified ? new Date(p.modified).toLocaleDateString() : "—"}
                  </span>
                </div>
              </div>
            </div>
          </a>
        ))}
      </div>
    );
  }, [loading, ports]);

  return content;
}
