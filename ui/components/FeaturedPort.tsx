"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api-client";
import type { PortDetail } from "@/lib/types";
import { Star, Package, Download, ExternalLink, Github, Globe, Copy, Check } from "lucide-react";

export default function FeaturedPort() {
  const [port, setPort] = useState<PortDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [copiedCommand, setCopiedCommand] = useState(false);

  // Featured ports rotation - could be made dynamic
  const featuredPortNames = [
    'git', 'python311', 'node18', 'ffmpeg', 'imagemagick', 'curl', 'wget', 'vim', 'emacs', 'gcc12'
  ];

  useEffect(() => {
    async function fetchFeaturedPort() {
      setLoading(true);
      try {
        // Select a featured port based on the current day to rotate daily
        const dayOfYear = Math.floor((Date.now() - new Date(new Date().getFullYear(), 0, 0).getTime()) / 86400000);
        const selectedPortName = featuredPortNames[dayOfYear % featuredPortNames.length];
        
        const portData = await api.getPort(selectedPortName);
        setPort(portData);
      } catch (err) {
        console.log("Failed to fetch featured port:", err);
        setPort(null);
      } finally {
        setLoading(false);
      }
    }

    fetchFeaturedPort();
  }, []);

  const copyInstallCommand = async () => {
    if (!port) return;
    const command = `sudo port install ${port.name}`;
    try {
      await navigator.clipboard.writeText(command);
      setCopiedCommand(true);
      setTimeout(() => setCopiedCommand(false), 2000);
    } catch (err) {
      console.error("Failed to copy to clipboard:", err);
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <Star className="h-5 w-5 text-yellow-400" />
          <h2 className="text-xl font-semibold">Featured Port</h2>
        </div>
        <div className="card animate-pulse">
          <div className="flex flex-col lg:flex-row gap-6">
            <div className="flex-1 space-y-4">
              <div className="space-y-2">
                <div className="h-8 w-48 bg-white/10 rounded" />
                <div className="h-4 w-24 bg-white/5 rounded" />
              </div>
              <div className="space-y-2">
                <div className="h-4 w-full bg-white/5 rounded" />
                <div className="h-4 w-3/4 bg-white/5 rounded" />
              </div>
              <div className="flex gap-2">
                <div className="h-6 w-16 bg-white/10 rounded-full" />
                <div className="h-6 w-20 bg-white/10 rounded-full" />
              </div>
            </div>
            <div className="lg:w-64 space-y-3">
              <div className="h-10 w-full bg-white/10 rounded" />
              <div className="h-8 w-full bg-white/5 rounded" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!port) {
    return null; // Don't show anything if we can't load a featured port
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Star className="h-5 w-5 text-yellow-400" />
        <h2 className="text-xl font-semibold">Featured Port</h2>
        <span className="text-sm text-white/60">• Today's pick</span>
      </div>
      
      <div className="card bg-gradient-to-br from-white/10 to-white/5 border-yellow-400/20">
        <div className="flex flex-col lg:flex-row gap-6">
          <div className="flex-1">
            <div className="flex items-start gap-3 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-lg flex items-center justify-center">
                <Package className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="text-2xl font-bold">{port.name}</h3>
                {port.version && (
                  <div className="text-yellow-400 font-medium">v{port.version}</div>
                )}
              </div>
            </div>
            
            <p className="text-white/80 mb-4 leading-relaxed">
              {port.long_description || port.description || "No description available."}
            </p>
            
            <div className="flex flex-wrap gap-2 mb-4">
              {port.categories?.slice(0, 3).map((category) => (
                <span
                  key={category}
                  className="inline-block px-3 py-1 bg-yellow-400/20 text-yellow-300 text-sm rounded-full"
                >
                  {category}
                </span>
              ))}
            </div>
            
            <div className="flex flex-wrap gap-4 text-sm text-white/70">
              {port.maintainers && port.maintainers.length > 0 && (
                <div>
                  <span className="text-white/80">Maintained by:</span>{" "}
                  {port.maintainers.slice(0, 2).map((maintainer, index) => (
                    <span key={index}>
                      {maintainer.github ? (
                        <a
                          href={`https://github.com/${maintainer.github}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-yellow-300 hover:text-yellow-200"
                        >
                          @{maintainer.github}
                        </a>
                      ) : (
                        maintainer.name || maintainer.email
                      )}
                      {index < Math.min(port.maintainers!.length, 2) - 1 && ", "}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
          
          <div className="lg:w-64 space-y-3">
            <button
              onClick={copyInstallCommand}
              className="w-full flex items-center justify-center gap-2 bg-yellow-500 hover:bg-yellow-600 text-black font-semibold py-3 px-4 rounded-lg transition-colors"
            >
              {copiedCommand ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              {copiedCommand ? 'Copied!' : 'Copy Install Command'}
            </button>
            
            <div className="text-xs text-white/60 font-mono text-center bg-black/20 p-2 rounded">
              sudo port install {port.name}
            </div>
            
            <div className="flex gap-2">
              <a
                href={`/port/${encodeURIComponent(port.name)}`}
                className="flex-1 flex items-center justify-center gap-2 bg-white/10 hover:bg-white/20 py-2 px-3 rounded text-sm transition-colors"
              >
                <Package className="h-4 w-4" />
                Details
              </a>
              
              {port.homepage && (
                <a
                  href={port.homepage}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 bg-white/10 hover:bg-white/20 py-2 px-3 rounded text-sm transition-colors"
                >
                  <Globe className="h-4 w-4" />
                  Homepage
                </a>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
