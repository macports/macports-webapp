"use client";

import { useState, useCallback, useEffect, useMemo, useRef } from "react";
import { Menu, X, Search as SearchIcon, Loader2 } from "lucide-react";
import { usePathname } from "next/navigation";
import { apiUrl } from "@/lib/api";
import ThemeToggle from "./ThemeToggle";

type Suggestion = { name: string; description?: string | null };

function useDebounced<T>(value: T, delay = 250) {
  const [v, setV] = useState(value);
  useEffect(() => {
    const id = setTimeout(() => setV(value), delay);
    return () => clearTimeout(id);
  }, [value, delay]);
  return v;
}

export default function Header() {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  
  // Search functionality
  const [query, setQuery] = useState("");
  const debounced = useDebounced(query);
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [searchOpen, setSearchOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const searchRef = useRef<HTMLDivElement | null>(null);

  const normalize = (data: any, searchQuery: string): Suggestion[] => {
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

    const query = searchQuery.toLowerCase();
    const sorted = suggestions.sort((a, b) => {
      const nameA = a.name.toLowerCase();
      const nameB = b.name.toLowerCase();
      
      if (nameA === query && nameB !== query) return -1;
      if (nameB === query && nameA !== query) return 1;
      
      if (nameA.startsWith(query) && !nameB.startsWith(query)) return -1;
      if (nameB.startsWith(query) && !nameA.startsWith(query)) return 1;
      
      if (nameA.startsWith(query) && nameB.startsWith(query)) {
        return nameA.length - nameB.length;
      }
      
      return nameA.localeCompare(nameB);
    });

    return sorted.slice(0, 8);
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
    setSearchOpen(suggestions.length > 0);
    setSelectedIndex(-1);
  }, [suggestions]);

  const onSelect = useCallback((name: string) => {
    window.location.href = `/port/${encodeURIComponent(name)}`;
    setQuery("");
    setSearchOpen(false);
  }, []);

  const hasQuery = useMemo(() => query.trim().length > 0, [query]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!searchOpen || suggestions.length === 0) return;

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
        setSearchOpen(false);
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

  // Check if current page is active
  const isActive = (path: string) => {
    if (path === "/" && pathname === "/") return true;
    if (path !== "/" && pathname.startsWith(path)) return true;
    return false;
  };

  return (
    <header className="sticky top-0 z-50 border-b border-gray-200 dark:border-white/10 bg-white/80 dark:bg-slate-950/80 backdrop-blur">
      <div className="container flex h-16 items-center justify-between gap-4">
        {/* Logo */}
        <a href="/" className="flex items-center font-semibold text-gray-900 dark:text-white">
          <img src="/macports-flat-logo.svg" alt="MacPorts" className="h-32 w-32" />
        </a>

        {/* Flexible spacer - always present to push navigation to the right */}
        <div className="flex-1">
          {/* Search Bar - Desktop (hidden on home and ports pages) */}
          {!isActive('/') && !isActive('/ports') && (
            <div className="hidden md:block max-w-md mx-auto" ref={searchRef}>
              <form onSubmit={handleSubmit} className="relative">
                <div className="flex items-center gap-2 rounded-lg border border-gray-300 dark:border-white/20 bg-gray-50 dark:bg-white/5 px-3 py-2 focus-within:border-blue-500 dark:focus-within:border-blue-400 focus-within:bg-white dark:focus-within:bg-white/10 transition-colors">
                  <SearchIcon className="h-4 w-4 text-gray-400 dark:text-white/60" />
                  <input
                    aria-label="Search ports"
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Quick search ports..."
                    className="w-full bg-transparent text-gray-900 dark:text-white placeholder:text-gray-400 dark:placeholder:text-white/40 focus:outline-none text-sm"
                    autoComplete="off"
                  />
                  {loading ? (
                    <Loader2 className="h-4 w-4 animate-spin text-gray-400 dark:text-white/60" />
                  ) : hasQuery ? (
                    <button
                      type="button"
                      aria-label="Clear search"
                      className="rounded p-1 text-gray-400 dark:text-white/60 hover:bg-gray-200 dark:hover:bg-white/10"
                      onClick={() => setQuery("")}
                    >
                      ×
                    </button>
                  ) : null}
                </div>

                {searchOpen && (
                  <ul className="absolute z-50 mt-2 max-h-64 w-full overflow-auto rounded-lg border border-gray-200 dark:border-white/20 bg-white dark:bg-slate-900 shadow-lg">
                    {suggestions.map((item, index) => {
                      const name = item.name;
                      const isExactMatch = name.toLowerCase() === debounced.toLowerCase();
                      
                      return (
                        <li key={name}>
                          <button
                            className={`flex w-full items-start gap-3 px-3 py-2 text-left hover:bg-gray-50 dark:hover:bg-white/10 transition-colors ${
                              isExactMatch ? 'bg-blue-50 dark:bg-blue-500/20 border-l-2 border-blue-500' : ''
                            } ${selectedIndex === index ? 'bg-gray-100 dark:bg-white/15' : ''}`}
                            onClick={() => onSelect(name)}
                          >
                            <div className="min-w-0 flex-1">
                              <div className={`font-mono text-sm truncate text-gray-900 dark:text-white ${
                                isExactMatch ? 'text-blue-600 dark:text-blue-400 font-semibold' : ''
                              }`}>
                                {name}
                                {isExactMatch && (
                                  <span className="ml-2 text-xs bg-blue-500 text-white px-1 rounded">EXACT</span>
                                )}
                              </div>
                              {item.description && (
                                <div className="text-xs text-gray-500 dark:text-white/60 line-clamp-1 mt-1">
                                  {item.description}
                                </div>
                              )}
                            </div>
                          </button>
                        </li>
                      );
                    })}
                    {!loading && suggestions.length === 0 && hasQuery && (
                      <li className="px-3 py-2 text-sm text-gray-500 dark:text-white/60">No matches</li>
                    )}
                  </ul>
                )}
              </form>
            </div>
          )}
        </div>

        {/* Navigation Links - Desktop */}
        <nav className="hidden items-center gap-1 text-sm md:flex">
          <a 
            href="/" 
            className={`px-3 py-2 rounded-md transition-colors ${
              isActive('/') 
                ? 'bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 font-medium' 
                : 'text-gray-600 dark:text-white/70 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-white/10'
            }`}
          >
            Home
          </a>
          <a 
            href="/ports" 
            className={`px-3 py-2 rounded-md transition-colors ${
              isActive('/ports') 
                ? 'bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 font-medium' 
                : 'text-gray-600 dark:text-white/70 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-white/10'
            }`}
          >
            All Ports
          </a>
          <a 
            href="/stats" 
            className={`px-3 py-2 rounded-md transition-colors ${
              isActive('/stats') 
                ? 'bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 font-medium' 
                : 'text-gray-600 dark:text-white/70 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-white/10'
            }`}
          >
            Stats
          </a>
          <a
            href="https://www.macports.org/" 
            target="_blank"
            rel="noreferrer"
            className="px-3 py-2 rounded-md text-gray-600 dark:text-white/70 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-white/10 transition-colors"
          >
            macports.org
          </a>
        </nav>

        {/* Right side controls */}
        <div className="flex items-center gap-3">
          <ThemeToggle />
        <button
            className="md:hidden rounded-md p-2 hover:bg-gray-100 dark:hover:bg-white/10 text-gray-900 dark:text-white transition-colors"
          onClick={() => setOpen((s) => !s)}
          aria-label="Toggle menu"
        >
          {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {open && (
        <div className="border-t border-gray-200 dark:border-white/10 bg-white dark:bg-slate-950 md:hidden">
          <nav className="container flex flex-col gap-1 py-3 text-sm">
            {/* Mobile Search (hidden on home and ports pages) */}
            {!isActive('/') && !isActive('/ports') && (
              <div className="mb-4">
                <form onSubmit={handleSubmit} className="relative">
                  <div className="flex items-center gap-2 rounded-lg border border-gray-300 dark:border-white/20 bg-gray-50 dark:bg-white/5 px-3 py-2 focus-within:border-blue-500 dark:focus-within:border-blue-400 transition-colors">
                    <SearchIcon className="h-4 w-4 text-gray-400 dark:text-white/60" />
                    <input
                      aria-label="Search ports"
                      type="text"
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder="Search ports..."
                      className="w-full bg-transparent text-gray-900 dark:text-white placeholder:text-gray-400 dark:placeholder:text-white/40 focus:outline-none text-sm"
                      autoComplete="off"
                    />
                    {loading ? (
                      <Loader2 className="h-4 w-4 animate-spin text-gray-400 dark:text-white/60" />
                    ) : hasQuery ? (
                      <button
                        type="button"
                        aria-label="Clear search"
                        className="rounded p-1 text-gray-400 dark:text-white/60 hover:bg-gray-200 dark:hover:bg-white/10"
                        onClick={() => setQuery("")}
                      >
                        ×
                      </button>
                    ) : null}
                  </div>

                  {searchOpen && (
                    <ul className="absolute z-50 mt-2 max-h-48 w-full overflow-auto rounded-lg border border-gray-200 dark:border-white/20 bg-white dark:bg-slate-900 shadow-lg">
                      {suggestions.map((item, index) => {
                        const name = item.name;
                        const isExactMatch = name.toLowerCase() === debounced.toLowerCase();
                        
                        return (
                          <li key={name}>
                            <button
                              className={`flex w-full items-start gap-3 px-3 py-2 text-left hover:bg-gray-50 dark:hover:bg-white/10 transition-colors ${
                                isExactMatch ? 'bg-blue-50 dark:bg-blue-500/20 border-l-2 border-blue-500' : ''
                              } ${selectedIndex === index ? 'bg-gray-100 dark:bg-white/15' : ''}`}
                              onClick={() => onSelect(name)}
                            >
                              <div className="min-w-0 flex-1">
                                <div className={`font-mono text-sm truncate text-gray-900 dark:text-white ${
                                  isExactMatch ? 'text-blue-600 dark:text-blue-400 font-semibold' : ''
                                }`}>
                                  {name}
                                  {isExactMatch && (
                                    <span className="ml-2 text-xs bg-blue-500 text-white px-1 rounded">EXACT</span>
                                  )}
                                </div>
                                {item.description && (
                                  <div className="text-xs text-gray-500 dark:text-white/60 line-clamp-1 mt-1">
                                    {item.description}
                                  </div>
                                )}
                              </div>
                            </button>
                          </li>
                        );
                      })}
                      {!loading && suggestions.length === 0 && hasQuery && (
                        <li className="px-3 py-2 text-sm text-gray-500 dark:text-white/60">No matches</li>
                      )}
                    </ul>
                  )}
                </form>
              </div>
            )}

            {/* Mobile Navigation Links */}
            <a 
              href="/" 
              className={`px-3 py-2 rounded-md transition-colors ${
                isActive('/') 
                  ? 'bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 font-medium' 
                  : 'text-gray-600 dark:text-white/70 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-white/10'
              }`}
            >
              Home
            </a>
            <a 
              href="/ports" 
              className={`px-3 py-2 rounded-md transition-colors ${
                isActive('/ports') 
                  ? 'bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 font-medium' 
                  : 'text-gray-600 dark:text-white/70 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-white/10'
              }`}
            >
              All Ports
            </a>
            <a 
              href="/stats" 
              className={`px-3 py-2 rounded-md transition-colors ${
                isActive('/stats') 
                  ? 'bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 font-medium' 
                  : 'text-gray-600 dark:text-white/70 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-white/10'
              }`}
            >
              Stats
            </a>
            <a
              href="https://www.macports.org/" 
              target="_blank"
              rel="noreferrer"
              className="px-3 py-2 rounded-md text-gray-600 dark:text-white/70 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-white/10 transition-colors"
            >
              macports.org
            </a>
          </nav>
        </div>
      )}
    </header>
  );
}
