"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { apiUrl } from "@/lib/api";
import { Search as SearchIcon, Loader2 } from "lucide-react";

type Suggestion = { name: string; description?: string | null };

function useDebounced<T>(value: T, delay = 250) {
  const [v, setV] = useState(value);
  useEffect(() => {
    const id = setTimeout(() => setV(value), delay);
    return () => clearTimeout(id);
  }, [value, delay]);
  return v;
}

export default function SearchBar({ placeholder }: { placeholder?: string }) {
  const [query, setQuery] = useState("");
  const debounced = useDebounced(query);
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [open, setOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const listRef = useRef<HTMLUListElement | null>(null);

  const normalize = (data: any, searchQuery: string): Suggestion[] => {
    // Accept arrays of strings or objects, or wrapped in {results} / {ports}
    const arr =
      Array.isArray(data)
        ? data
        : Array.isArray(data?.results)
        ? data.results
        : Array.isArray(data?.ports)
        ? data.ports
        : [];

    const suggestions: Suggestion[] = arr
      .map((item: any) => {
        if (typeof item === "string") return { name: item as string, description: null };
        if (item && typeof item === "object") {
          const name: string | undefined =
            typeof item.name === "string"
              ? item.name
              : typeof item.port === "string"
              ? item.port
              : typeof item.portname === "string"
              ? item.portname
              : undefined;
          if (!name) return null;
          const description =
            typeof item.description === "string"
              ? item.description
              : typeof item.desc === "string"
              ? item.desc
              : null;
          return { name, description };
        }
        return null;
      })
      .filter((item: Suggestion | null): item is Suggestion => item !== null);

    // Sort suggestions by relevance - exact matches first, then prefix matches, then others
    const query = searchQuery.toLowerCase();
    const sorted = suggestions.sort((a, b) => {
      const nameA = a.name.toLowerCase();
      const nameB = b.name.toLowerCase();
      
      // Exact match gets highest priority
      if (nameA === query && nameB !== query) return -1;
      if (nameB === query && nameA !== query) return 1;
      
      // Prefix match gets second priority
      if (nameA.startsWith(query) && !nameB.startsWith(query)) return -1;
      if (nameB.startsWith(query) && !nameA.startsWith(query)) return 1;
      
      // If both or neither are prefix matches, sort by length (shorter names first)
      if (nameA.startsWith(query) && nameB.startsWith(query)) {
        return nameA.length - nameB.length;
      }
      
      // For non-prefix matches, sort alphabetically
      return nameA.localeCompare(nameB);
    });

    return sorted.slice(0, 10);
  };

  const fetchSuggestions = useCallback(async (q: string) => {
    if (!q || q.trim().length < 2) {
      setSuggestions([]);
      return;
    }
    setLoading(true);
    try {
      const url = apiUrl(`/autocomplete/port/?q=${encodeURIComponent(q)}`);
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setSuggestions(normalize(data, q));
    } catch {
      setSuggestions([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSuggestions(debounced);
  }, [debounced, fetchSuggestions]);

  useEffect(() => {
    setOpen(suggestions.length > 0);
    setSelectedIndex(-1); // Reset selection when suggestions change
  }, [suggestions]);

  const onSelect = useCallback((name: string) => {
    window.location.href = `/port/${encodeURIComponent(name)}`;
  }, []);

  const hasQuery = useMemo(() => query.trim().length > 0, [query]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!open || suggestions.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => (prev < suggestions.length - 1 ? prev + 1 : 0));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => (prev > 0 ? prev - 1 : suggestions.length - 1));
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
          onSelect(suggestions[selectedIndex].name);
        } else if (query.trim()) {
          window.location.href = `/ports?q=${encodeURIComponent(query.trim())}`;
        }
        break;
      case 'Escape':
        setOpen(false);
        setSelectedIndex(-1);
        break;
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
      onSelect(suggestions[selectedIndex].name);
    } else if (query.trim()) {
      window.location.href = `/ports?q=${encodeURIComponent(query.trim())}`;
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className="flex items-center gap-2 rounded-xl border border-white/15 dark:border-white/15 border-gray-300 bg-white/5 dark:bg-white/5 bg-white px-3 py-2 shadow-inner focus-within:border-brand-400 focus-within:bg-white/10 dark:focus-within:bg-white/10 focus-within:bg-gray-50 transition">
        <SearchIcon className="h-5 w-5 flex-shrink-0 text-white/60 dark:text-white/60 text-gray-400" />
        <input
          aria-label="Search ports"
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder ?? "Search ports…"}
          className="w-full bg-transparent text-white dark:text-white text-gray-900 placeholder:text-white/40 dark:placeholder:text-white/40 placeholder:text-gray-400 focus:outline-none"
          autoComplete="off"
        />
        <div className="w-6 h-6 flex items-center justify-center flex-shrink-0">
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin text-white/60 dark:text-white/60 text-gray-400" />
          ) : hasQuery ? (
            <button
              type="button"
              aria-label="Clear search"
              className="rounded p-1 text-white/60 dark:text-white/60 text-gray-400 hover:bg-white/10 dark:hover:bg-white/10 hover:bg-gray-200 flex items-center justify-center"
              onClick={() => setQuery("")}
            >
              ×
            </button>
          ) : null}
        </div>
      </div>

      {open && (
        <ul
          ref={listRef}
          className="absolute z-50 mt-2 max-h-72 w-full overflow-auto rounded-xl border border-white/10 dark:border-white/10 border-gray-200 bg-slate-900/95 dark:bg-slate-900/95 bg-white/95 backdrop-blur shadow-lg"
        >
          {suggestions.map((item, index) => {
            const name = item.name;
            const desc = item.description || null;
            const isExactMatch = name.toLowerCase() === debounced.toLowerCase();
            const isPrefix = name.toLowerCase().startsWith(debounced.toLowerCase());
            
            return (
              <li key={name}>
                <button
                  className={`flex w-full items-start justify-between gap-3 px-3 py-2 text-left hover:bg-white/10 dark:hover:bg-white/10 hover:bg-gray-100 transition-colors ${
                    isExactMatch ? 'bg-brand-500/20 border-l-2 border-brand-400' : ''
                  } ${selectedIndex === index ? 'bg-white/15 dark:bg-white/15 bg-gray-100' : ''}`}
                  onClick={() => onSelect(name)}
                >
                  <div className="min-w-0 flex-1">
                    <div className={`font-mono text-sm truncate flex items-center gap-2 text-white dark:text-white text-gray-900 ${
                      isExactMatch ? 'text-brand-200 dark:text-brand-200 text-brand-600 font-semibold' : ''
                    }`}>
                      {name}
                      {isExactMatch && (
                        <span className="text-xs bg-brand-500 text-white px-1 rounded">EXACT</span>
                      )}
                      {!isExactMatch && isPrefix && (
                        <span className="text-xs bg-gray-200 text-gray-700 dark:bg-white/20 dark:text-white/80 px-1 rounded">PREFIX</span>
                      )}
                    </div>
                    {desc ? (
                      <div className="text-xs text-white/60 dark:text-white/60 text-gray-500 line-clamp-2 mt-1">
                        {desc}
                      </div>
                    ) : null}
                  </div>
                  <span className="shrink-0 self-center text-xs text-white/50 dark:text-white/50 text-gray-400">Open</span>
                </button>
              </li>
            );
          })}
          {!loading && suggestions.length === 0 && hasQuery && (
            <li className="px-3 py-2 text-sm text-white/60 dark:text-white/60 text-gray-500">No matches</li>
          )}
        </ul>
      )}
    </form>
  );
}
