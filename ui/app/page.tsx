"use client";

import { useState, useEffect } from "react";
import SearchBar from "@/components/SearchBar";
import PopularPorts from "@/components/PopularPorts";
import RecentlyUpdated from "@/components/RecentlyAdded";
import FeaturedPort from "@/components/FeaturedPort";
import { Search, ArrowRight, Package, Code, Terminal } from "lucide-react";
import { api } from "@/lib/api-client";

export default function HomePage() {
  const [totalPorts, setTotalPorts] = useState<number | null>(null);

  useEffect(() => {
    async function fetchTotalPorts() {
      try {
        // Fetch enhanced stats for accurate total ports count
        const enhancedResponse = await fetch("https://ports.macports.org/api/v1/statistics/enhanced/");
        if (enhancedResponse.ok) {
          const enhancedStats = await enhancedResponse.json();
          setTotalPorts(enhancedStats?.total_ports || null);
        }
      } catch (err) {
        console.error("Failed to fetch total ports:", err);
      }
    }
    fetchTotalPorts();
  }, []);

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="relative rounded-2xl border border-gray-200 dark:border-white/10 bg-gradient-to-br from-gray-50 via-brand-100/30 to-transparent dark:from-white/10 dark:via-brand-500/5 dark:to-transparent p-8 md:p-12">
        <div className="relative z-10">
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight mb-6 text-gray-900 dark:text-white">
              The macOS Package Manager
            </h1>
            <p className="text-lg md:text-xl text-gray-600 dark:text-white/80 mb-8 leading-relaxed">
              Discover, install, and manage thousands of open-source packages for macOS. 
              From development tools to multimedia libraries, find everything you need.
            </p>

            <div className="max-w-2xl mx-auto mb-8">
              <SearchBar placeholder="Search for packages, tools, libraries..." />
            </div>

            <div className="flex flex-wrap justify-center gap-4 text-sm">
              <div className="flex items-center gap-2 px-4 py-2 bg-gray-200 dark:bg-white/10 rounded-full text-gray-700 dark:text-white">
                <Package className="h-4 w-4 text-brand-300" />
                <span>{totalPorts ? `${totalPorts.toLocaleString()} Ports` : 'Thousands of Ports'}</span>
              </div>
              <div className="flex items-center gap-2 px-4 py-2 bg-gray-200 dark:bg-white/10 rounded-full text-gray-700 dark:text-white">
                <Terminal className="h-4 w-4 text-purple-300" />
                <span>Easy Install</span>
              </div>
            </div>
          </div>
        </div>

        {/* Decorative elements */}
        <div className="pointer-events-none absolute top-0 left-0 w-full h-full overflow-hidden rounded-2xl">
          <div className="absolute right-[-10%] top-[-10%] h-64 w-64 rounded-full bg-brand-500/20 blur-3xl" />
          <div className="absolute left-[-5%] bottom-[-5%] h-48 w-48 rounded-full bg-purple-500/20 blur-3xl" />
        </div>
      </section>

      {/* Featured Port */}
      <FeaturedPort />

      {/* Popular and Recent Ports Side by Side */}
      <div className="grid gap-8 lg:grid-cols-2">
        <PopularPorts />
        <RecentlyUpdated />
      </div>

      {/* Quick Actions */}
      <section className="space-y-6">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-2">Explore MacPorts</h2>
          <p className="text-gray-600 dark:text-white/70">Different ways to discover packages</p>
        </div>

                  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <a
              href="/ports"
              className="card group dark:hover:bg-white/10 hover:bg-gray-50 transition-all duration-200 hover:scale-[1.02] text-center"
            >
              <Package className="h-8 w-8 text-brand-300 mx-auto mb-3" />
              <h3 className="font-semibold mb-2">All Ports</h3>
              <p className="text-sm text-gray-600 dark:text-white/70 mb-4">Browse, search, and filter the complete collection</p>
              <div className="flex items-center justify-center gap-1 text-brand-600 dark:text-brand-300 group-hover:text-brand-700 dark:group-hover:text-brand-200">
                <span className="text-sm">Explore</span>
                <ArrowRight className="h-4 w-4" />
              </div>
            </a>

            <a
              href="/ports"
              className="card group dark:hover:bg-white/10 hover:bg-gray-50 transition-all duration-200 hover:scale-[1.02] text-center"
            >
              <div className="h-8 w-8 bg-green-500/10 dark:bg-green-500/20 rounded-lg flex items-center justify-center mx-auto mb-3">
                <span className="text-green-600 dark:text-green-300 text-lg">#</span>
              </div>
              <h3 className="font-semibold mb-2">Categories</h3>
              <p className="text-sm text-gray-600 dark:text-white/70 mb-4">Browse by category</p>
              <div className="flex items-center justify-center gap-1 text-green-600 dark:text-green-300 group-hover:text-green-700 dark:group-hover:text-green-200">
                <span className="text-sm">Browse</span>
                <ArrowRight className="h-4 w-4" />
              </div>
            </a>

            <a
              href="/ports"
              className="card group dark:hover:bg-white/10 hover:bg-gray-50 transition-all duration-200 hover:scale-[1.02] text-center"
            >
              <div className="h-8 w-8 bg-purple-500/10 dark:bg-purple-500/20 rounded-lg flex items-center justify-center mx-auto mb-3">
                <span className="text-purple-600 dark:text-purple-300 text-lg">@</span>
              </div>
              <h3 className="font-semibold mb-2">Maintainers</h3>
              <p className="text-sm text-gray-600 dark:text-white/70 mb-4">Meet the contributors</p>
              <div className="flex items-center justify-center gap-1 text-purple-600 dark:text-purple-300 group-hover:text-purple-700 dark:group-hover:text-purple-200">
                <span className="text-sm">Discover</span>
                <ArrowRight className="h-4 w-4" />
              </div>
            </a>
          </div>
      </section>

      {/* Getting Started */}
      <section className="bg-gradient-to-r from-brand-500/10 to-purple-500/10 rounded-2xl p-8 md:p-12 border border-gray-200 dark:border-white/10">
        <div className="text-center max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold mb-4">Get Started with MacPorts</h2>
          <p className="text-gray-700 dark:text-white/80 mb-8 leading-relaxed">
            New to MacPorts? Install it on your Mac and start discovering thousands of packages.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="https://www.macports.org/install.php"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-brand-500 hover:bg-brand-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              <Package className="h-5 w-5" />
              Install MacPorts
            </a>

            <a
              href="https://guide.macports.org/"
              target="_blank"
              rel="noopener noreferrer"
              className="border border-gray-300 dark:border-white/20 hover:bg-gray-50 dark:hover:bg-white/10 text-gray-900 dark:text-white font-semibold py-3 px-6 rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              <Code className="h-5 w-5" />
              Read Documentation
            </a>
          </div>
        </div>
      </section>
    </div>
  );
}
