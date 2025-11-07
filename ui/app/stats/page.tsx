"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api-client";
import type { EnhancedStats, PopularPort } from "@/lib/types";
import { BarChart, TrendingUp, Package, Users, Download, Clock, Calendar, Monitor, Code, Wrench } from "lucide-react";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, LineElement, PointElement, Title, Tooltip, Legend, Filler } from 'chart.js';
import { Bar, Pie, Line } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function StatsPage() {
  const [enhancedStats, setEnhancedStats] = useState<EnhancedStats | null>(null);
  const [popularPorts, setPopularPorts] = useState<PopularPort[]>([]);
  const [macportsVersions, setMacportsVersions] = useState<any[]>([]);
  const [osVersions, setOsVersions] = useState<any[]>([]);
  const [xcodeVersions, setXcodeVersions] = useState<any[]>([]);
  const [cltVersions, setCltVersions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(30);
  const [daysAgo, setDaysAgo] = useState(0);

  useEffect(() => {
    async function fetchStats() {
      setLoading(true);
      setError(null);
      try {
        const [enhanced, popular, macports, os, xcode, clt] = await Promise.all([
          api.getEnhancedStats(),
          api.getPopularPorts({ days, limit: 50 }),
          api.getGeneralStats({ days, days_ago: daysAgo, property: ['macports_version'], sort_by: 'macports_version' }),
          api.getGeneralStats({ days, days_ago: daysAgo, property: ['os_version', 'build_arch'], sort_by: 'os_version' }),
          api.getGeneralStats({ days, days_ago: daysAgo, property: ['os_version', 'xcode_version'], sort_by: 'os_version' }),
          api.getGeneralStats({ days, days_ago: daysAgo, property: ['os_version', 'clt_version'], sort_by: 'os_version' })
        ]);
        
        console.log("Raw OS data:", os);
        console.log("Raw Xcode data:", xcode);
        console.log("Raw CLT data:", clt);
        
        setEnhancedStats(enhanced);
        setPopularPorts(popular);
        setMacportsVersions(macports.result || []);
        setOsVersions(os.result || []);
        setXcodeVersions(xcode.result || []);
        setCltVersions(clt.result || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch statistics");
      } finally {
        setLoading(false);
      }
    }

    fetchStats();
  }, [days, daysAgo]);

  const formatNumber = (num: number | undefined) => {
    if (!num) return "—";
    return num.toLocaleString();
  };

  const formatDate = (dateString: string | undefined) => {
    if (!dateString) return "—";
    return new Date(dateString).toLocaleDateString();
  };

  const TopPortsChart = ({ ports }: { ports: PopularPort[] }) => {
    const maxCount = Math.max(...ports.map(p => p.total_count));
    
    return (
      <div className="space-y-3">
        {ports.slice(0, 15).map((port, index) => (
          <div key={port.port} className="space-y-1">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400 dark:text-white/40 w-6">#{index + 1}</span>
                <a 
                  href={`/port/${encodeURIComponent(port.port)}`}
                  className="font-mono text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors"
                >
                  {port.port}
                </a>
              </div>
              <div className="flex items-center gap-3 text-gray-600 dark:text-white/60 text-xs">
                <span>{formatNumber(port.req_count)} requested</span>
                <span>{formatNumber(port.total_count)} total</span>
              </div>
            </div>
            <div className="w-full bg-gray-200 dark:bg-white/10 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-blue-500 to-blue-400 h-2 rounded-full transition-all duration-300"
                style={{ width: `${(port.total_count / maxCount) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-4">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Installation Statistics</h1>
      </div>

      {/* Important Notice - Prominent */}
      <div className="card bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-500/10 dark:to-indigo-500/10 border-2 border-blue-200 dark:border-blue-500/30">
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0">
            <div className="p-3 bg-blue-500/20 rounded-lg">
              <Users className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">About These Statistics</h3>
            <p className="text-gray-700 dark:text-white/80 leading-relaxed">
              Statistics are collected from users who have opted in by installing the <code className="px-2 py-0.5 bg-gray-200 dark:bg-white/10 rounded text-sm font-mono">mpstats</code> port. 
              Data shows both <strong>requested installations</strong> (explicitly installed) and <strong>total installations</strong> (including dependencies).
            </p>
          </div>
        </div>
      </div>

      {/* Time Period Selector */}
      <div className="space-y-4">
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-gray-500 dark:text-white/60" />
            <span className="text-sm text-gray-600 dark:text-white/70">Duration:</span>
            <select 
              value={days} 
              onChange={(e) => setDays(Number(e.target.value))}
              className="text-sm border border-gray-300 dark:border-white/20 rounded-md px-2 py-1 bg-white dark:bg-white/5 text-gray-900 dark:text-white"
            >
              <option value={7}>7 days</option>
              <option value={30}>30 days</option>
              <option value={90}>90 days</option>
              <option value={180}>180 days</option>
              <option value={365}>365 days</option>
            </select>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600 dark:text-white/70">until:</span>
            <select 
              value={daysAgo} 
              onChange={(e) => setDaysAgo(Number(e.target.value))}
              className="text-sm border border-gray-300 dark:border-white/20 rounded-md px-2 py-1 bg-white dark:bg-white/5 text-gray-900 dark:text-white"
            >
              <option value={0}>today</option>
              <option value={7}>7 days ago</option>
              <option value={30}>30 days ago</option>
              <option value={90}>90 days ago</option>
              <option value={180}>180 days ago</option>
              <option value={365}>365 days ago</option>
            </select>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <p className="mt-2 text-gray-600 dark:text-white/60">Loading statistics...</p>
        </div>
      ) : error ? (
        <div className="bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-lg p-6 text-center py-12">
          <BarChart className="h-12 w-12 text-gray-400 dark:text-white/40 mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">Statistics Unavailable</h2>
          <p className="text-gray-600 dark:text-white/60 mb-4">
            {error || "Statistics data is currently unavailable."}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
          >
            Try Again
          </button>
        </div>
      ) : enhancedStats ? (
        <>
          {/* Overview Cards */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-lg p-6">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-blue-500/20 rounded-lg">
                  <Users className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {formatNumber(enhancedStats.total_unique_users)}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-white/60">Total Users</div>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-lg p-6">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-green-500/20 rounded-lg">
                  <Download className="h-6 w-6 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {formatNumber(enhancedStats.total_submissions)}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-white/60">Total Submissions</div>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-lg p-6">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-purple-500/20 rounded-lg">
                  <Package className="h-6 w-6 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {formatNumber(enhancedStats.total_ports)}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-white/60">Available Ports</div>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-lg p-6">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-orange-500/20 rounded-lg">
                  <TrendingUp className="h-6 w-6 text-orange-600 dark:text-orange-400" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {formatNumber(enhancedStats.current_week)}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-white/60">This Week</div>
                </div>
              </div>
            </div>
          </div>

          {/* Top Installations */}
          {popularPorts && popularPorts.length > 0 && (
            <div className="bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-lg p-6">
              <div className="flex items-center gap-2 mb-6">
                <TrendingUp className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Most Popular Ports</h2>
                <span className="text-sm text-gray-500 dark:text-white/60">({days} days)</span>
              </div>
              
              <TopPortsChart ports={popularPorts} />
              
              <div className="mt-6 pt-4 border-t border-gray-200 dark:border-white/10">
                <p className="text-sm text-gray-600 dark:text-white/60">
                  Statistics are collected from users who have opted in by installing the <code className="bg-gray-100 dark:bg-white/10 px-1 rounded text-xs">mpstats</code> port.
                  Data shows both requested installations (explicitly installed) and total installations (including dependencies).
                </p>
              </div>
            </div>
          )}

          {/* System Statistics Charts */}
          <div className="space-y-8">
            {/* MacPorts Versions */}
            {macportsVersions.length > 0 && (
              <div className="bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-lg p-6">
                <div className="flex items-center gap-2 mb-6">
                  <Package className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white">MacPorts Versions</h2>
                </div>
                <div className="h-80">
                  <Bar
                    data={{
                      labels: macportsVersions
                        .sort((a, b) => b.count - a.count)
                        .slice(0, 10)
                        .map(v => v.macports_version),
                      datasets: [{
                        label: 'Users',
                        data: macportsVersions
                          .sort((a, b) => b.count - a.count)
                          .slice(0, 10)
                          .map(v => v.count),
                        backgroundColor: 'rgba(147, 51, 234, 0.8)',
                        borderColor: 'rgba(147, 51, 234, 1)',
                        borderWidth: 1
                      }]
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      indexAxis: 'y' as const,
                      plugins: {
                        legend: {
                          display: false
                        },
                        tooltip: {
                          callbacks: {
                            label: (context) => `${formatNumber(context.parsed.x)} users`
                          }
                        }
                      },
                      scales: {
                        x: {
                          beginAtZero: true,
                          grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                          },
                          ticks: {
                            color: 'rgba(0, 0, 0, 0.7)'
                          }
                        },
                        y: {
                          grid: {
                            display: false
                          },
                          ticks: {
                            color: 'rgba(0, 0, 0, 0.7)'
                          }
                        }
                      }
                    }}
                  />
                </div>
              </div>
            )}

            {/* macOS Versions by Architecture */}
            {osVersions.length > 0 && (
              <div className="bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-lg p-6">
                <div className="flex items-center gap-2 mb-6">
                  <Monitor className="h-5 w-5 text-green-600 dark:text-green-400" />
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white">macOS Versions by Architecture</h2>
                </div>
                <div className="h-80">
                  {(() => {
                    console.log("OS Versions data:", osVersions.slice(0, 5));
                    
                    // Group by OS version and architecture
                    const grouped = osVersions.reduce((acc, item) => {
                      const osVersion = item.os_version;
                      const arch = item.build_arch || 'unknown';
                      
                      if (!acc[osVersion]) acc[osVersion] = {};
                      if (!acc[osVersion][arch]) acc[osVersion][arch] = 0;
                      acc[osVersion][arch] += item.count;
                      return acc;
                    }, {} as Record<string, Record<string, number>>);
                    
                    console.log("Grouped OS versions:", grouped);
                    
                    // Get ALL OS versions sorted by version number
                    const osVersionTotals = Object.entries(grouped)
                      .map(([os, archs]) => [
                        os,
                        Object.values(archs as Record<string, number>).reduce((sum, count) => sum + count, 0)
                      ])
                      .sort(([osA], [osB]) => {
                        // Sort by OS version number
                        const [majorA] = (osA as string).split('.').map(Number);
                        const [majorB] = (osB as string).split('.').map(Number);
                        return (majorB || 0) - (majorA || 0);
                      });
                    
                    // Get all unique architectures
                    const allArchs = Array.from(new Set(
                      Object.values(grouped).flatMap(archs => Object.keys(archs as Record<string, number>))
                    )).sort();
                    
                    console.log("Top OS versions:", osVersionTotals);
                    console.log("All architectures:", allArchs);
                    
                    const colors: Record<string, string> = {
                      'i386': 'rgba(239, 68, 68, 0.8)',
                      'x86_64': 'rgba(59, 130, 246, 0.8)',
                      'arm64': 'rgba(34, 197, 94, 0.8)',
                      'ppc': 'rgba(245, 158, 11, 0.8)',
                      'unknown': 'rgba(156, 163, 175, 0.8)'
                    };
                    
                    return (
                      <Bar
                        data={{
                          labels: osVersionTotals.map(([os]) => `macOS ${os}`),
                          datasets: allArchs.map((arch) => ({
                            label: arch,
                            data: osVersionTotals.map(([os]) => grouped[os as string]?.[arch] || 0),
                            backgroundColor: colors[arch] || 'rgba(147, 51, 234, 0.8)',
                            borderColor: (colors[arch] || 'rgba(147, 51, 234, 0.8)').replace('0.8', '1'),
                            borderWidth: 1
                          }))
                        }}
                        options={{
                          responsive: true,
                          maintainAspectRatio: false,
                          plugins: {
                            legend: {
                              position: 'top' as const,
                              labels: {
                                color: 'rgba(0, 0, 0, 0.7)',
                                usePointStyle: true,
                                padding: 15
                              }
                            },
                            tooltip: {
                              callbacks: {
                                label: (context) => `${context.dataset.label}: ${formatNumber(context.parsed.y)} users`
                              }
                            }
                          },
                          scales: {
                            x: {
                              stacked: true,
                              grid: {
                                display: false
                              },
                              ticks: {
                                color: 'rgba(0, 0, 0, 0.7)'
                              }
                            },
                            y: {
                              stacked: true,
                              beginAtZero: true,
                              grid: {
                                color: 'rgba(0, 0, 0, 0.1)'
                              },
                              ticks: {
                                color: 'rgba(0, 0, 0, 0.7)'
                              }
                            }
                          }
                        }}
                      />
                    );
                  })()}
                </div>
              </div>
            )}

            {/* Xcode Versions by macOS */}
            {xcodeVersions.length > 0 && (
              <div className="bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-lg p-6">
                <div className="flex items-center gap-2 mb-6">
                  <Code className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Xcode Versions by macOS</h2>
                </div>
                <div className="h-80">
                  {(() => {
                    console.log("Xcode Versions data:", xcodeVersions.slice(0, 5));
                    
                    // Group by macOS version and Xcode version
                    const grouped = xcodeVersions.reduce((acc, item) => {
                      const osVersion = item.os_version;
                      let xcodeVersion = item.xcode_version;
                      
                      // Simplify Xcode version (e.g., "15.2.0" -> "15.2")
                      const segments = xcodeVersion.split(".");
                      if (segments.length >= 2) {
                        xcodeVersion = segments[0] + "." + segments[1];
                      }
                      
                      if (!acc[osVersion]) acc[osVersion] = {};
                      if (!acc[osVersion][xcodeVersion]) acc[osVersion][xcodeVersion] = 0;
                      acc[osVersion][xcodeVersion] += item.count;
                      return acc;
                    }, {} as Record<string, Record<string, number>>);
                    
                    console.log("Grouped Xcode versions:", grouped);
                    
                    // Get ALL macOS versions sorted by version number
                    const osVersionTotals = Object.entries(grouped)
                      .map(([os, xcodeVersions]) => [
                        os,
                        Object.values(xcodeVersions as Record<string, number>).reduce((sum, count) => sum + count, 0)
                      ])
                      .sort(([osA], [osB]) => {
                        // Sort by OS version number
                        const [majorA] = (osA as string).split('.').map(Number);
                        const [majorB] = (osB as string).split('.').map(Number);
                        return (majorB || 0) - (majorA || 0);
                      });
                    
                    // Get all unique Xcode versions
                    const allXcodeVersions = Array.from(new Set(
                      Object.values(grouped).flatMap(xcodeVersions => Object.keys(xcodeVersions as Record<string, number>))
                    )).sort((a, b) => {
                      // Sort by version number
                      const [majorA, minorA] = a.split('.').map(Number);
                      const [majorB, minorB] = b.split('.').map(Number);
                      if (majorA !== majorB) return majorB - majorA;
                      return (minorB || 0) - (minorA || 0);
                    });
                    
                    console.log("All macOS versions:", osVersionTotals);
                    console.log("All Xcode versions:", allXcodeVersions);
                    
                    const colors = [
                      'rgba(59, 130, 246, 0.8)',
                      'rgba(147, 51, 234, 0.8)',
                      'rgba(34, 197, 94, 0.8)',
                      'rgba(239, 68, 68, 0.8)',
                      'rgba(245, 158, 11, 0.8)',
                      'rgba(236, 72, 153, 0.8)',
                      'rgba(14, 165, 233, 0.8)',
                      'rgba(168, 85, 247, 0.8)',
                      'rgba(251, 146, 60, 0.8)',
                      'rgba(192, 132, 252, 0.8)',
                      'rgba(99, 102, 241, 0.8)',
                      'rgba(244, 114, 182, 0.8)'
                    ];
                    
                    return (
                      <Bar
                        data={{
                          labels: osVersionTotals.map(([os]) => `macOS ${os}`),
                          datasets: allXcodeVersions.map((xcodeVersion, index) => ({
                            label: `Xcode ${xcodeVersion}`,
                            data: osVersionTotals.map(([os]) => grouped[os as string]?.[xcodeVersion] || 0),
                            backgroundColor: colors[index % colors.length],
                            borderColor: colors[index % colors.length].replace('0.8', '1'),
                            borderWidth: 1
                          }))
                        }}
                        options={{
                          responsive: true,
                          maintainAspectRatio: false,
                          plugins: {
                            legend: {
                              position: 'top' as const,
                              labels: {
                                color: 'rgba(0, 0, 0, 0.7)',
                                usePointStyle: true,
                                padding: 15
                              }
                            },
                            tooltip: {
                              callbacks: {
                                label: (context) => `${context.dataset.label}: ${formatNumber(context.parsed.y)} users`
                              }
                            }
                          },
                          scales: {
                            x: {
                              stacked: true,
                              grid: {
                                display: false
                              },
                              ticks: {
                                color: 'rgba(0, 0, 0, 0.7)'
                              }
                            },
                            y: {
                              stacked: true,
                              beginAtZero: true,
                              grid: {
                                color: 'rgba(0, 0, 0, 0.1)'
                              },
                              ticks: {
                                color: 'rgba(0, 0, 0, 0.7)'
                              }
                            }
                          }
                        }}
                      />
                    );
                  })()}
                </div>
              </div>
            )}

            {/* CLT Versions by macOS */}
            {cltVersions.length > 0 && (
              <div className="bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-lg p-6">
                <div className="flex items-center gap-2 mb-6">
                  <Wrench className="h-5 w-5 text-orange-600 dark:text-orange-400" />
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Command Line Tools by macOS</h2>
                </div>
                <div className="h-80">
                  {(() => {
                    console.log("CLT Versions data:", cltVersions.slice(0, 5));
                    
                    // Group by macOS version and CLT version
                    const grouped = cltVersions.reduce((acc, item) => {
                      const osVersion = item.os_version;
                      let cltVersion = item.clt_version;
                      
                      // Simplify CLT version (e.g., "15.1.0.0.1.1700200546" -> "15.1")
                      const segments = cltVersion.split(".");
                      if (segments.length >= 2) {
                        cltVersion = segments[0] + "." + segments[1];
                      }
                      
                      if (!acc[osVersion]) acc[osVersion] = {};
                      if (!acc[osVersion][cltVersion]) acc[osVersion][cltVersion] = 0;
                      acc[osVersion][cltVersion] += item.count;
                      return acc;
                    }, {} as Record<string, Record<string, number>>);
                    
                    console.log("Grouped CLT versions:", grouped);
                    
                    // Get ALL macOS versions sorted by version number
                    const osVersionTotals = Object.entries(grouped)
                      .map(([os, cltVersions]) => [
                        os,
                        Object.values(cltVersions as Record<string, number>).reduce((sum, count) => sum + count, 0)
                      ])
                      .sort(([osA], [osB]) => {
                        // Sort by OS version number
                        const [majorA] = (osA as string).split('.').map(Number);
                        const [majorB] = (osB as string).split('.').map(Number);
                        return (majorB || 0) - (majorA || 0);
                      });
                    
                    // Get all unique CLT versions
                    const allCltVersions = Array.from(new Set(
                      Object.values(grouped).flatMap(cltVersions => Object.keys(cltVersions as Record<string, number>))
                    )).sort((a, b) => {
                      // Sort by version number
                      const [majorA, minorA] = a.split('.').map(Number);
                      const [majorB, minorB] = b.split('.').map(Number);
                      if (majorA !== majorB) return majorB - majorA;
                      return (minorB || 0) - (minorA || 0);
                    });
                    
                    console.log("All macOS versions:", osVersionTotals);
                    console.log("All CLT versions:", allCltVersions);
                    
                    const colors = [
                      'rgba(245, 158, 11, 0.8)',
                      'rgba(239, 68, 68, 0.8)',
                      'rgba(34, 197, 94, 0.8)',
                      'rgba(59, 130, 246, 0.8)',
                      'rgba(147, 51, 234, 0.8)',
                      'rgba(236, 72, 153, 0.8)',
                      'rgba(14, 165, 233, 0.8)',
                      'rgba(168, 85, 247, 0.8)',
                      'rgba(251, 146, 60, 0.8)',
                      'rgba(192, 132, 252, 0.8)',
                      'rgba(99, 102, 241, 0.8)',
                      'rgba(244, 114, 182, 0.8)'
                    ];
                    
                    return (
                      <Bar
                        data={{
                          labels: osVersionTotals.map(([os]) => `macOS ${os}`),
                          datasets: allCltVersions.map((cltVersion, index) => ({
                            label: `CLT ${cltVersion}`,
                            data: osVersionTotals.map(([os]) => grouped[os as string]?.[cltVersion] || 0),
                            backgroundColor: colors[index % colors.length],
                            borderColor: colors[index % colors.length].replace('0.8', '1'),
                            borderWidth: 1
                          }))
                        }}
                        options={{
                          responsive: true,
                          maintainAspectRatio: false,
                          plugins: {
                            legend: {
                              position: 'top' as const,
                              labels: {
                                color: 'rgba(0, 0, 0, 0.7)',
                                usePointStyle: true,
                                padding: 15
                              }
                            },
                            tooltip: {
                              callbacks: {
                                label: (context) => `${context.dataset.label}: ${formatNumber(context.parsed.y)} users`
                              }
                            }
                          },
                          scales: {
                            x: {
                              stacked: true,
                              grid: {
                                display: false
                              },
                              ticks: {
                                color: 'rgba(0, 0, 0, 0.7)'
                              }
                            },
                            y: {
                              stacked: true,
                              beginAtZero: true,
                              grid: {
                                color: 'rgba(0, 0, 0, 0.1)'
                              },
                              ticks: {
                                color: 'rgba(0, 0, 0, 0.7)'
                              }
                            }
                          }
                        }}
                      />
                    );
                  })()}
                </div>
              </div>
            )}
          </div>

        </>
      ) : null}
    </div>
  );
}
