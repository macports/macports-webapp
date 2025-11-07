"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api-client";
import type { Port } from "@/lib/types";
import { Package, Clock, ExternalLink } from "lucide-react";

export default function RecentlyUpdated() {
  const [ports, setPorts] = useState<Port[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchRecentPorts() {
      setLoading(true);
      setError(null);
      try {
        console.log("Fetching recently updated ports...");
        
        // Try multiple approaches to get recently updated ports
        let recentPorts: Port[] = [];
        
        // First, try to get a larger sample and filter for recent updates
        const response = await api.getPorts({ 
          limit: 100 // Get more ports to find recently updated ones
        });
        
        console.log("Fetched ports response:", response);
        console.log("Total ports available:", response.count);
        
        if (response.results && response.results.length > 0) {
          // Filter and sort by update date
          recentPorts = response.results
            .filter(port => {
              const hasUpdateDate = port.version_updated_at || port.updated_at;
              if (hasUpdateDate) {
                // Only include ports updated in the last 90 days
                const updateDate = new Date(port.version_updated_at || port.updated_at || 0);
                const now = new Date();
                const daysDiff = (now.getTime() - updateDate.getTime()) / (1000 * 60 * 60 * 24);
                return daysDiff <= 90;
              }
              return false;
            })
            .sort((a, b) => {
              const dateA = new Date(a.version_updated_at || a.updated_at || 0);
              const dateB = new Date(b.version_updated_at || b.updated_at || 0);
              return dateB.getTime() - dateA.getTime();
            })
            .slice(0, 6);
          
          console.log("Filtered recent ports:", recentPorts);
        }
        
        // If we still don't have enough recent ports, just show the first 10 from API
        if (recentPorts.length < 5) {
          console.log("Not enough recent ports, using first 10 from API");
          recentPorts = response.results.slice(0, 6);
        }
        
        setPorts(recentPorts);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch recent ports");
        setPorts([]);
      } finally {
        setLoading(false);
      }
    }

    fetchRecentPorts();
  }, []);

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return "—";
    const date = new Date(dateString);
    const now = new Date();
    const diffInDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
    
    if (diffInDays === 0) return "Today";
    if (diffInDays === 1) return "Yesterday";
    if (diffInDays < 7) return `${diffInDays} days ago`;
    if (diffInDays < 30) return `${Math.floor(diffInDays / 7)} weeks ago`;
    if (diffInDays < 365) return `${Math.floor(diffInDays / 30)} months ago`;
    return date.toLocaleDateString();
  };

  const RecentPortItem = ({ port }: { port: Port }) => (
    <a
      href={`/port/${encodeURIComponent(port.name)}`}
      className="block border-b border-white/10 hover:bg-white/5 transition-colors last:border-b-0"
    >
      <div className="p-4 flex items-center justify-between gap-4">
        <div className="flex items-center gap-3 min-w-0 flex-1">
          <Package className="h-5 w-5 text-emerald-300 shrink-0" />
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <h3 className="font-semibold truncate">{port.name}</h3>
              {port.version && (
                <span className="text-xs text-emerald-300 bg-emerald-500/20 px-2 py-1 rounded">
                  v{port.version}
                </span>
              )}
            </div>
            <p className="text-sm text-white/70 truncate mt-1">
              {port.description || "No description available."}
            </p>
          </div>
        </div>
        
        <div className="hidden md:flex items-center gap-2 shrink-0">
          {port.categories?.slice(0, 2).map((category) => (
            <span
              key={category}
              className="px-2 py-1 text-xs rounded-full bg-white/10 text-white/80"
            >
              {category}
            </span>
          ))}
        </div>
        
        <div className="flex items-center gap-1 text-xs text-white/60 shrink-0">
          <Clock className="h-3 w-3" />
          <span className="hidden sm:block">{formatDate(port.version_updated_at || port.updated_at)}</span>
        </div>
      </div>
    </a>
  );

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <Clock className="h-5 w-5 text-emerald-300" />
          <h2 className="text-xl font-semibold">Recently Added</h2>
        </div>
        <div className="card p-0 overflow-hidden">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="p-4 border-b border-white/10 animate-pulse last:border-b-0">
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-3 flex-1">
                  <div className="w-5 h-5 bg-white/10 rounded" />
                  <div className="flex-1 space-y-2">
                    <div className="h-4 w-32 bg-white/10 rounded" />
                    <div className="h-3 w-64 bg-white/5 rounded" />
                  </div>
                </div>
                <div className="hidden md:flex gap-2">
                  <div className="h-5 w-12 bg-white/10 rounded-full" />
                  <div className="h-5 w-16 bg-white/10 rounded-full" />
                </div>
                <div className="h-3 w-16 bg-white/5 rounded" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error || ports.length === 0) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <Clock className="h-5 w-5 text-emerald-300" />
          <h2 className="text-xl font-semibold">Recently Added</h2>
        </div>
        <div className="card text-center py-8">
          <Package className="h-8 w-8 text-white/40 mx-auto mb-2" />
          <p className="text-white/60">
            {error ? "Unable to load recent ports" : "No recent ports available"}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Clock className="h-5 w-5 text-emerald-300" />
          <h2 className="text-xl font-semibold">Recently Added</h2>
        </div>
        <a 
          href="/ports?ordering=-version_updated_at" 
          className="text-sm text-emerald-300 hover:text-emerald-200 transition-colors flex items-center gap-1"
        >
          View all <ExternalLink className="h-3 w-3" />
        </a>
      </div>
      
      <div className="card p-0 overflow-hidden">
        {ports.map((port) => (
          <RecentPortItem key={port.name} port={port} />
        ))}
      </div>
    </div>
  );
}
