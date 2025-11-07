"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api-client";
import { Package, Users, Download, TrendingUp, Calendar, Globe } from "lucide-react";

interface HomeStatsData {
  total_ports?: number;
  total_unique_users?: number;
  total_installations?: number;
  current_week?: number;
  last_week?: number;
  total_submissions?: number;
}

export default function HomeStats() {
  const [stats, setStats] = useState<HomeStatsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStats() {
      try {
        console.log("Fetching MacPorts statistics...");
        
        // Fetch basic port count from ports API
        const portsResponse = await api.getPorts({ limit: 1 });
        console.log("Ports response:", portsResponse);
        
        // Fetch enhanced stats (includes accurate active ports count)
        let enhancedStats = null;
        try {
          const enhancedResponse = await fetch("https://ports.macports.org/api/v1/statistics/enhanced/");
          console.log("Enhanced stats response status:", enhancedResponse.status);
          if (enhancedResponse.ok) {
            enhancedStats = await enhancedResponse.json();
            console.log("Enhanced stats data:", enhancedStats);
          }
        } catch (err) {
          console.log("Enhanced stats API not available:", err);
        }

        const statsData = {
          // Prioritize active ports count from enhanced stats, fallback to total ports count
          total_ports: enhancedStats?.total_ports || portsResponse.count || 0,
          total_unique_users: enhancedStats?.total_unique_users,
          total_installations: enhancedStats?.total_submissions,
          current_week: enhancedStats?.current_week,
          last_week: enhancedStats?.last_week,
          total_submissions: enhancedStats?.total_submissions
        };
        
        console.log("Final stats data:", statsData);
        setStats(statsData);
      } catch (err) {
        console.error("Failed to fetch stats:", err);
        // Set basic fallback data
        setStats({ total_ports: 0 });
      } finally {
        setLoading(false);
      }
    }

    fetchStats();
  }, []);

  const formatNumber = (num: number | undefined) => {
    if (!num) return "—";
    return num.toLocaleString();
  };

  const calculateGrowth = (current: number | undefined, last: number | undefined) => {
    if (!current || !last || last === 0) return null;
    const growth = ((current - last) / last) * 100;
    return growth > 0 ? `+${growth.toFixed(1)}%` : `${growth.toFixed(1)}%`;
  };

  if (loading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="card animate-pulse">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-white/10 rounded-lg" />
              <div className="space-y-2">
                <div className="h-6 w-16 bg-white/10 rounded" />
                <div className="h-4 w-20 bg-white/5 rounded" />
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  const growth = calculateGrowth(stats?.current_week, stats?.last_week);

    const statsToShow = [
    stats?.total_ports && {
      icon: Package,
      color: "brand" as const,
      value: stats.total_ports,
      label: "Total Ports"
    },
    stats?.total_unique_users && {
      icon: Users,
      color: "green" as const,
      value: stats.total_unique_users,
      label: "Active Users"
    },
    stats?.total_installations && {
      icon: Download,
      color: "purple" as const,
      value: stats.total_installations,
      label: "Installations"
    },
    stats?.current_week && {
      icon: TrendingUp,
      color: "orange" as const,
      value: stats.current_week,
      label: growth ? `This Week ${growth}` : "This Week"
    }
  ].filter(Boolean) as Array<{
    icon: any;
    color: "brand" | "green" | "purple" | "orange";
    value: number;
    label: string;
  }>;

  return (
    <div className={`grid gap-4 ${statsToShow.length === 1 ? 'sm:grid-cols-1 max-w-sm mx-auto' : statsToShow.length === 2 ? 'sm:grid-cols-2 max-w-lg mx-auto' : statsToShow.length === 3 ? 'sm:grid-cols-3 max-w-3xl mx-auto' : 'sm:grid-cols-2 lg:grid-cols-4'}`}>
      {statsToShow.map((stat, index) => {
        const IconComponent = stat.icon;
        const colorClasses = {
          brand: "bg-brand-500/20 text-brand-300 group-hover:bg-brand-500/30",
          green: "bg-green-500/20 text-green-300 group-hover:bg-green-500/30",
          purple: "bg-purple-500/20 text-purple-300 group-hover:bg-purple-500/30",
          orange: "bg-orange-500/20 text-orange-300 group-hover:bg-orange-500/30"
        };
        
        return (
          <div key={index} className="card group hover:bg-white/10 transition-all duration-200">
            <div className="flex items-center gap-3">
              <div className={`p-3 rounded-lg transition-colors ${colorClasses[stat.color]}`}>
                <IconComponent className="h-6 w-6" />
              </div>
              <div>
                <div className="text-2xl font-bold">
                  {formatNumber(stat.value)}
                </div>
                <div className="text-sm text-white/60">{stat.label}</div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
