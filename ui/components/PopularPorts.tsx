"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api-client";
import type { Port } from "@/lib/types";
import { TrendingUp, Package, ExternalLink, Star, Download } from "lucide-react";

export default function PopularPorts() {
  const [ports, setPorts] = useState<Port[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchPopularPorts() {
      setLoading(true);
      setError(null);
      try {
        // Get popular ports from the real MacPorts stats API
        let popularPorts: Port[] = [];
        
        try {
          // First try the actual popular ports API endpoint (correct URL from Django routes)
          const popularResponse = await fetch("https://ports.macports.org/api/v1/statistics/popular/?limit=6");
          if (popularResponse.ok) {
            const popularData = await popularResponse.json();
            console.log("Popular ports data:", popularData);
            
            if (Array.isArray(popularData) && popularData.length > 0) {
              // Get detailed port information for each popular port
              const portPromises = popularData.map((item: any) => 
                api.getPort(item.port).catch((err) => {
                  console.log(`Failed to get port ${item.port}:`, err);
                  return null;
                })
              );
              
              const portDetails = await Promise.all(portPromises);
              popularPorts = portDetails.filter((port): port is Port => port !== null);
              console.log("Fetched popular port details:", popularPorts);
            }
          } else {
            console.log("Popular ports API failed:", popularResponse.status);
          }
        } catch (err) {
          console.log("Popular ports API error:", err);
        }

        // Fallback: use well-known popular ports
        if (popularPorts.length === 0) {
          console.log("Using fallback popular ports");
          const knownPopularPorts = ['git', 'python311', 'curl', 'wget', 'ffmpeg', 'imagemagick', 'node18', 'vim'];
          const portPromises = knownPopularPorts.map((name: string) => 
            api.getPort(name).catch(() => null)
          );
          
          const portDetails = await Promise.all(portPromises);
          popularPorts = portDetails.filter((port): port is Port => port !== null).slice(0, 6);
        }

        setPorts(popularPorts);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch popular ports");
        setPorts([]);
      } finally {
        setLoading(false);
      }
    }

    fetchPopularPorts();
  }, []);

  const PopularPortItem = ({ port, rank }: { port: Port; rank: number }) => (
    <a
      href={`/port/${encodeURIComponent(port.name)}`}
      className="block border-b border-white/10 hover:bg-white/5 transition-colors last:border-b-0"
    >
      <div className="p-4 flex items-center justify-between gap-4">
        <div className="flex items-center gap-3 min-w-0 flex-1">
          <div className="w-8 h-8 bg-gradient-to-br from-brand-400 to-brand-600 rounded-lg flex items-center justify-center text-white font-bold text-sm shrink-0">
            #{rank}
          </div>
          <Package className="h-5 w-5 text-brand-300 shrink-0" />
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <h3 className="font-semibold truncate">{port.name}</h3>
              {port.version && (
                <span className="text-xs text-brand-300 bg-brand-500/20 px-2 py-1 rounded">
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
          <TrendingUp className="h-3 w-3" />
          <span className="hidden sm:block">Popular</span>
        </div>
      </div>
    </a>
  );

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-brand-300" />
          <h2 className="text-xl font-semibold">Popular Ports</h2>
        </div>
        <div className="card p-0 overflow-hidden">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="p-4 border-b border-white/10 animate-pulse last:border-b-0">
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-3 flex-1">
                  <div className="w-8 h-8 bg-white/10 rounded-lg" />
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
          <TrendingUp className="h-5 w-5 text-brand-300" />
          <h2 className="text-xl font-semibold">Popular Ports</h2>
        </div>
        <div className="card text-center py-8">
          <Package className="h-8 w-8 text-white/40 mx-auto mb-2" />
          <p className="text-white/60">
            {error ? "Unable to load popular ports" : "No popular ports available"}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-brand-300" />
          <h2 className="text-xl font-semibold">Popular Ports</h2>
        </div>
        <a 
          href="/stats" 
          className="text-sm text-brand-300 hover:text-brand-200 transition-colors flex items-center gap-1"
        >
          View all stats <ExternalLink className="h-3 w-3" />
        </a>
      </div>
      
      <div className="card p-0 overflow-hidden">
        {ports.map((port, index) => (
          <PopularPortItem key={port.name} port={port} rank={index + 1} />
        ))}
      </div>
    </div>
  );
}
