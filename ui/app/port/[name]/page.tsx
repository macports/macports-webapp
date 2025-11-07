"use client";

import React, { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api-client";
import type { PortDetail, Build } from "@/lib/types";
import { 
  Package, 
  ExternalLink, 
  Download, 
  Users, 
  Clock, 
  Tag, 
  GitBranch, 
  AlertCircle, 
  CheckCircle, 
  Code, 
  Globe,
  Copy,
  Check,
  Settings,
  Eye,
  EyeOff,
  Terminal,
  Info,
  BarChart3,
  Wrench,
  Shield,
  Bug,
  ChevronDown,
  ChevronUp,
  Monitor,
  Heart,
  Star,
  Zap,
  X
} from "lucide-react";
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

type ViewMode = 'basic' | 'advanced';

interface PortPageProps {
  params: { name: string };
}

// Chart.js helper functions
const generateChartColors = (count: number) => {
  const colors = [
    '#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6',
    '#06B6D4', '#F97316', '#84CC16', '#EC4899', '#6366F1',
    '#14B8A6', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'
  ];
  return Array.from({ length: count }, (_, i) => colors[i % colors.length]);
};

const createBarChartData = (data: any[], labelKey: string, valueKey: string, title: string) => {
  if (!data || data.length === 0) {
    return {
      labels: [],
      datasets: [{
        label: title,
        data: [],
        backgroundColor: generateChartColors(1)[0],
        borderColor: generateChartColors(1)[0],
        borderWidth: 1
      }]
    };
  }

  const labels = data.map(item => item[labelKey] || 'Unknown');
  const values = data.map(item => item[valueKey] || 0);
  
  return {
    labels,
    datasets: [{
      label: title,
      data: values,
      backgroundColor: generateChartColors(data.length),
      borderColor: generateChartColors(data.length),
      borderWidth: 1
    }]
  };
};

// Create stacked bar chart for Xcode versions - exactly matching Django JavaScript logic
const createStackedBarChartData = (data: any[], title: string) => {
  if (!data || data.length === 0) {
    return {
      labels: [],
      datasets: []
    };
  }

  // Step 1: Replicate getXCodeVersionsData() and generateDataset() logic exactly
  
  // Group by Xcode version (like the reduce function in Django JS)
  const groupedByXcode: Record<string, any[]> = {};
  data.forEach(item => {
    const xcodeVersion = item.submission__xcode_version || 'Unknown';
    if (!groupedByXcode[xcodeVersion]) {
      groupedByXcode[xcodeVersion] = [];
    }
    groupedByXcode[xcodeVersion].push(item);
  });

  // Create the result object like generateDataset returns
  const result: Record<string, Map<string, number>> = {};
  
  // Create dataMap for all OS versions
  const allOsVersions = new Set<string>();
  data.forEach(item => {
    allOsVersions.add(item.submission__os_version || 'Unknown');
  });
  
  // For each Xcode version, create a Map of OS version -> count
  Object.keys(groupedByXcode).forEach(xcodeVersion => {
    const dataMap = new Map<string, number>();
    
    // Initialize all OS versions to 0
    allOsVersions.forEach(osVersion => {
      dataMap.set(osVersion, 0);
    });
    
    // Fill in actual data
    groupedByXcode[xcodeVersion].forEach(item => {
      const osVersion = item.submission__os_version || 'Unknown';
      dataMap.set(osVersion, item.count || 0);
    });
    
    result[xcodeVersion] = dataMap;
  });

  // Step 2: Process exactly like the Django JavaScript does
  const keys = Object.keys(result);
  const datasets: any[] = [];
  const colors = generateChartColors(keys.length);
  
  let c = 0;
  for (let key in result) {
    if (result.hasOwnProperty(key)) {
      const obj = {
        label: key, // Xcode version
        backgroundColor: colors[c],
        borderColor: colors[c],
        borderWidth: 1,
        data: Array.from(result[key].values()) // Counts for each macOS version
      };
      c++;
      datasets.push(obj);
    }
  }
  
  // Sort datasets by total count (descending)
  datasets.sort((a, b) => {
    const totalA = a.data.reduce((sum: number, val: number) => sum + val, 0);
    const totalB = b.data.reduce((sum: number, val: number) => sum + val, 0);
    return totalB - totalA; // Descending order
  });
  
  // Labels are the macOS versions (keys from the first Map)
  const labels = keys.length > 0 ? Array.from(result[keys[0]].keys()) : [];

  return {
    labels, // X-axis: macOS versions
    datasets // Each Xcode version as a dataset
  };
};

// Create stacked bar chart for CLT versions - same logic as Xcode but for CLT
const createCltStackedBarChartData = (data: any[], title: string) => {
  if (!data || data.length === 0) {
    return {
      labels: [],
      datasets: []
    };
  }

  // Group by CLT version (like the reduce function in Django JS)
  const groupedByClt: Record<string, any[]> = {};
  data.forEach(item => {
    const cltVersion = item.submission__clt_version || 'Unknown';
    if (!groupedByClt[cltVersion]) {
      groupedByClt[cltVersion] = [];
    }
    groupedByClt[cltVersion].push(item);
  });

  // Create the result object like generateDataset returns
  const result: Record<string, Map<string, number>> = {};
  
  // Create dataMap for all OS versions
  const allOsVersions = new Set<string>();
  data.forEach(item => {
    allOsVersions.add(item.submission__os_version || 'Unknown');
  });
  
  // For each CLT version, create a Map of OS version -> count
  Object.keys(groupedByClt).forEach(cltVersion => {
    const dataMap = new Map<string, number>();
    
    // Initialize all OS versions to 0
    allOsVersions.forEach(osVersion => {
      dataMap.set(osVersion, 0);
    });
    
    // Fill in actual data
    groupedByClt[cltVersion].forEach(item => {
      const osVersion = item.submission__os_version || 'Unknown';
      dataMap.set(osVersion, item.count || 0);
    });
    
    result[cltVersion] = dataMap;
  });

  // Process exactly like the Django JavaScript does
  const keys = Object.keys(result);
  const datasets: any[] = [];
  const colors = generateChartColors(keys.length);
  
  let c = 0;
  for (let key in result) {
    if (result.hasOwnProperty(key)) {
      const obj = {
        label: key, // CLT version
        backgroundColor: colors[c],
        borderColor: colors[c],
        borderWidth: 1,
        data: Array.from(result[key].values()) // Counts for each macOS version
      };
      c++;
      datasets.push(obj);
    }
  }
  
  // Sort datasets by total count (descending)
  datasets.sort((a, b) => {
    const totalA = a.data.reduce((sum: number, val: number) => sum + val, 0);
    const totalB = b.data.reduce((sum: number, val: number) => sum + val, 0);
    return totalB - totalA; // Descending order
  });
  
  // Labels are the macOS versions (keys from the first Map)
  const labels = keys.length > 0 ? Array.from(result[keys[0]].keys()) : [];

  return {
    labels, // X-axis: macOS versions
    datasets // Each CLT version as a dataset
  };
};

// Create monthly percentage chart
const createMonthlyPercentageChartData = (data: any[], title: string) => {
  if (!data || data.length === 0) {
    return {
      labels: [],
      datasets: []
    };
  }

  // Process monthly version data for percentages
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  
  // Format month labels
  const processedData = data.map(item => {
    let formattedMonth = item.month;
    if (item.month && item.month.includes(',')) {
      const [year, month] = item.month.split(',');
      formattedMonth = `${months[parseInt(month) - 1]} ${year}`;
    }
    return {
      ...item,
      month: formattedMonth
    };
  });

  // Group by version
  const groupedByVersion: Record<string, Record<string, number>> = {};
  const monthSet = new Set<string>();
  
  processedData.forEach(item => {
    const version = item.version || 'Unknown';
    const month = item.month;
    const count = item.count || 0;
    
    if (!groupedByVersion[version]) {
      groupedByVersion[version] = {};
    }
    groupedByVersion[version][month] = count;
    monthSet.add(month);
  });

  // Convert to percentages
  const monthList = Array.from(monthSet).sort();
  monthList.forEach(month => {
    let monthlySum = 0;
    Object.keys(groupedByVersion).forEach(version => {
      monthlySum += groupedByVersion[version][month] || 0;
    });
    
    if (monthlySum > 0) {
      Object.keys(groupedByVersion).forEach(version => {
        const count = groupedByVersion[version][month] || 0;
        groupedByVersion[version][month] = Number(((count / monthlySum) * 100).toFixed(1));
      });
    }
  });

  const versions = Object.keys(groupedByVersion).sort();
  const colors = generateChartColors(versions.length);

  const datasets = versions.map((version, index) => ({
    label: version,
    data: monthList.map(month => groupedByVersion[version][month] || 0),
    backgroundColor: colors[index],
    borderColor: colors[index],
    fill: false,
    tension: 0.1
  }));

  return {
    labels: monthList,
    datasets
  };
};

const createLineChartData = (data: any[], title: string) => {
  if (!data || data.length === 0) {
    return {
      labels: [],
      datasets: [{
        label: title,
        data: [],
        borderColor: '#3B82F6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true
      }]
    };
  }

  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const labels = data.map(item => {
    if (item.month && item.month.includes(',')) {
      const [year, month] = item.month.split(',');
      return `${months[parseInt(month) - 1]} ${year}`;
    }
    return item.month || 'Unknown';
  });
  
  const values = data.map(item => item.count || 0);
  
  return {
    labels,
    datasets: [{
      label: title,
      data: values,
      borderColor: '#3B82F6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      fill: true
    }]
  };
};

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
      labels: {
        color: '#fff'
      }
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: '#fff',
      bodyColor: '#fff'
    }
  },
  scales: {
    x: {
      ticks: {
        color: '#9CA3AF',
        maxRotation: 45
      },
      grid: {
        color: 'rgba(255, 255, 255, 0.1)'
      }
    },
    y: {
      ticks: {
        color: '#9CA3AF'
      },
      grid: {
        color: 'rgba(255, 255, 255, 0.1)'
      }
    }
  }
};

export default function PortPage({ params }: PortPageProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  const [port, setPort] = useState<PortDetail | null>(null);
  const [builds, setBuilds] = useState<Build[]>([]);
  const [portStats, setPortStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copiedCommand, setCopiedCommand] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>('basic');
  const [activeTab, setActiveTab] = useState<'info' | 'builds' | 'stats' | 'health' | 'tickets'>('info');
  const [showInstructions, setShowInstructions] = useState(false);
  const [expandedDeps, setExpandedDeps] = useState<{[key: string]: boolean}>({});
  const instructionsRef = React.useRef<HTMLDivElement>(null);
  
  const toggleInstructions = () => {
    setShowInstructions(!showInstructions);
    // Scroll to instructions after a short delay to allow animation to start
    if (!showInstructions) {
      setTimeout(() => {
        instructionsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }, 100);
    }
  };
  
  // Build history pagination and filters
  const [buildPage, setBuildPage] = useState(1);
  const [buildsPerPage] = useState(20);
  const [selectedBuilders, setSelectedBuilders] = useState<string[]>([]);
  const [selectedStatuses, setSelectedStatuses] = useState<string[]>([]);
  const [totalBuilds, setTotalBuilds] = useState(0);
  const [availableBuilders, setAvailableBuilders] = useState<{name: string, displayName: string}[]>([]);
  const [availableStatuses] = useState([
    { value: 'success', label: 'Success' },
    { value: 'failure', label: 'Failure' },
    { value: 'in-progress', label: 'In Progress' },
    { value: 'build successful', label: 'Build Successful' },
    { value: 'build failed', label: 'Build Failed' }
  ]);
  
  // Dropdown states
  const [showBuilderDropdown, setShowBuilderDropdown] = useState(false);
  const [showStatusDropdown, setShowStatusDropdown] = useState(false);
  
  // Statistics states
  const [selectedDuration, setSelectedDuration] = useState(30);
  const [selectedDaysAgo, setSelectedDaysAgo] = useState(0);
  const [portStatistics, setPortStatistics] = useState<any>(null);
  const [monthlyStats, setMonthlyStats] = useState<any>(null);
  const [monthlyVersionStats, setMonthlyVersionStats] = useState<any>(null);
  const [osVersionStats, setOsVersionStats] = useState<any>(null);
  const [portVersionStats, setPortVersionStats] = useState<any>(null);
  const [xcodeVersionStats, setXcodeVersionStats] = useState<any>(null);
  const [cltVersionStats, setCltVersionStats] = useState<any>(null);
  const [variantsStats, setVariantsStats] = useState<any>(null);
  
  // Individual loading states for each chart
  const [basicStatsLoading, setBasicStatsLoading] = useState(false);
  const [osVersionLoading, setOsVersionLoading] = useState(false);
  const [portVersionLoading, setPortVersionLoading] = useState(false);
  const [xcodeVersionLoading, setXcodeVersionLoading] = useState(false);
  const [cltVersionLoading, setCltVersionLoading] = useState(false);
  const [variantsLoading, setVariantsLoading] = useState(false);
  const [monthlyLoading, setMonthlyLoading] = useState(false);
  const [monthlyVersionLoading, setMonthlyVersionLoading] = useState(false);
  
  // Health and Tickets states
  const [healthData, setHealthData] = useState<any[]>([]);
  const [ticketsData, setTicketsData] = useState<any[]>([]);
  const [ticketsCount, setTicketsCount] = useState(0);
  const [healthLoading, setHealthLoading] = useState(false);
  const [ticketsLoading, setTicketsLoading] = useState(false);
  
  // File modal states
  const [showFilesModal, setShowFilesModal] = useState(false);
  const [selectedBuildId, setSelectedBuildId] = useState<string | null>(null);
  const [buildFiles, setBuildFiles] = useState<string[]>([]);
  const [filesLoading, setFilesLoading] = useState(false);
  const [selectedBuilderName, setSelectedBuilderName] = useState<string>('');

  const portName = decodeURIComponent(params.name);

  // Parse health HTML data
  const parseHealthData = (html: string) => {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const listItems = doc.querySelectorAll('ul.list-group li.list-group-item');
    
    const builders: any[] = [];
    listItems.forEach(item => {
      const link = item.querySelector('a');
      const badge = item.querySelector('span.badge');
      const fileButton = item.querySelector('button.loadFiles');
      
      if (link) {
        const builderName = link.textContent?.trim();
        const buildUrl = link.getAttribute('href');
        const isSuccess = badge?.classList.contains('text-success');
        const fileCount = fileButton ? parseInt(fileButton.textContent?.match(/\d+/)?.[0] || '0') : 0;
        
        // Extract build ID from button ID (format: build-{id})
        const buildId = fileButton?.getAttribute('id')?.replace('build-', '');
        
        builders.push({
          name: builderName,
          url: buildUrl,
          status: isSuccess ? 'success' : 'failure',
          fileCount,
          buildId
        });
      }
    });
    
    return builders;
  };

  // Fetch build files
  const fetchBuildFiles = async (buildId: string, builderName: string) => {
    setFilesLoading(true);
    setSelectedBuildId(buildId);
    setSelectedBuilderName(builderName);
    setShowFilesModal(true);
    
    try {
      const response = await api.getBuildFiles(buildId);
      // Extract file names from the response (each file object has a 'file' property)
      const fileNames = response.files?.map((fileObj: any) => fileObj.file || fileObj) || [];
      setBuildFiles(fileNames);
    } catch (err) {
      console.error('Failed to fetch build files:', err);
      setBuildFiles([]);
    } finally {
      setFilesLoading(false);
    }
  };

  // Parse tickets HTML data
  const parseTicketsData = (html: string) => {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    
    // Get count from hidden span
    const countSpan = doc.querySelector('#tickets-count-returned');
    const count = parseInt(countSpan?.textContent || '0');
    
    // Parse table rows
    const rows = doc.querySelectorAll('table tr');
    const tickets: any[] = [];
    
    rows.forEach(row => {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 3) {
        const idLink = cells[0].querySelector('a');
        const ticketId = idLink?.textContent?.trim();
        const ticketUrl = idLink?.getAttribute('href');
        const title = cells[1].textContent?.trim();
        const type = cells[2].textContent?.trim();
        const typeClass = cells[2].className;
        
        if (ticketId && title) {
          tickets.push({
            id: ticketId,
            title,
            type,
            url: `https://trac.macports.org${ticketUrl}`,
            priority: typeClass.includes('text-danger') ? 'high' : 
                     typeClass.includes('text-warning') ? 'medium' : 'normal'
          });
        }
      }
    });
    
    return { tickets, count };
  };

  // Function to update URL with current state
  const updateURL = (updates: {
    tab?: string;
    page?: number;
    builders?: string[];
    statuses?: string[];
  }) => {
    const current = new URLSearchParams(searchParams.toString());
    
    if (updates.tab !== undefined) {
      if (updates.tab === 'info') {
        current.delete('tab');
      } else {
        current.set('tab', updates.tab);
      }
    }
    
    if (updates.page !== undefined) {
      if (updates.page === 1) {
        current.delete('page');
      } else {
        current.set('page', updates.page.toString());
      }
    }
    
    if (updates.builders !== undefined) {
      current.delete('builders');
      if (updates.builders.length > 0) {
        current.set('builders', updates.builders.join(','));
      }
    }
    
    if (updates.statuses !== undefined) {
      current.delete('statuses');
      if (updates.statuses.length > 0) {
        current.set('statuses', updates.statuses.join(','));
      }
    }
    
    const newUrl = `${window.location.pathname}${current.toString() ? '?' + current.toString() : ''}`;
    router.replace(newUrl, { scroll: false });
  };

  // Load initial state from URL and localStorage
  useEffect(() => {
    // View mode from localStorage
    const savedViewMode = localStorage.getItem('macports-view-mode') as ViewMode;
    if (savedViewMode) {
      setViewMode(savedViewMode);
    }
    
    // State from URL parameters
    const tab = searchParams.get('tab') as 'info' | 'builds' | 'stats' | 'health' | 'tickets' || 'info';
    const page = parseInt(searchParams.get('page') || '1');
    const builders = searchParams.get('builders')?.split(',').filter(Boolean) || [];
    const statuses = searchParams.get('statuses')?.split(',').filter(Boolean) || [];
    
    setActiveTab(tab);
    setBuildPage(page);
    setSelectedBuilders(builders);
    setSelectedStatuses(statuses);
  }, [searchParams]);

  // Save view preference to localStorage
  const toggleViewMode = () => {
    const newMode = viewMode === 'basic' ? 'advanced' : 'basic';
    setViewMode(newMode);
    localStorage.setItem('macports-view-mode', newMode);
    
    // Clear advanced-mode data when switching to basic
    if (newMode === 'basic') {
      setBuilds([]);
      setPortStats(null);
      setPortStatistics(null);
      setOsVersionStats(null);
      setPortVersionStats(null);
      setXcodeVersionStats(null);
      setCltVersionStats(null);
      setVariantsStats(null);
      setMonthlyStats(null);
      setMonthlyVersionStats(null);
      setHealthData([]);
      setTicketsData([]);
      setTicketsCount(0);
    }
  };

  // Fetch basic port data (always needed)
  useEffect(() => {
    async function fetchPortData() {
      setLoading(true);
      setError(null);
      try {
        const portData = await api.getPort(portName);
        setPort(portData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch port data");
      } finally {
        setLoading(false);
      }
    }

    fetchPortData();
  }, [portName]);

  // Fetch installation stats (only for advanced view)
  useEffect(() => {
    async function fetchInstallationStats() {
      if (viewMode !== 'advanced') return;
      
      try {
        const [allStatsData, requestedStatsData] = await Promise.all([
          // Get all installations (no property filter = gets all installation records)
          api.getPortStats(portName, { days: 30 }).catch(() => ({ result: [] })),
          // Get only requested installations (optimized with property filter)
          api.getPortStats(portName, { days: 30, property: ['requested'] }).catch(() => ({ result: [] }))
        ]);
        
        // Extract installation counts from the stats response
        const installationStats = {
          all: 0,
          requested: 0
        };
        
        if (allStatsData.result && Array.isArray(allStatsData.result)) {
          // Sum up all counts for total installations
          installationStats.all = allStatsData.result.reduce((sum: number, item: any) => {
            return sum + (item.count || 0);
          }, 0);
        }
        
        if (requestedStatsData.result && Array.isArray(requestedStatsData.result)) {
          // Count installations where requested = true
          installationStats.requested = requestedStatsData.result
            .filter((item: any) => item.requested === true)
            .reduce((sum: number, item: any) => sum + (item.count || 0), 0);
        }
        
        setPortStats(installationStats);
      } catch (err) {
        console.error("Failed to fetch installation stats:", err);
      }
    }

    fetchInstallationStats();
  }, [portName, viewMode]);

  // Fetch builds (only when on builds tab in advanced mode)
  useEffect(() => {
    async function fetchBuilds() {
      if (viewMode !== 'advanced' || activeTab !== 'builds') return;
      
      try {
        const buildParams: any = {
          port_name: portName,
          page: buildPage,
          page_size: buildsPerPage
        };
        
        if (selectedBuilders.length > 0) buildParams.builder_name = selectedBuilders;
        if (selectedStatuses.length > 0) buildParams.status = selectedStatuses;
        
        const buildsData = await api.getBuilds(buildParams);
        setBuilds(buildsData.results || []);
        setTotalBuilds(buildsData.count || 0);
        
        // Extract unique builders for filter dropdown
        if (buildPage === 1 && selectedBuilders.length === 0 && selectedStatuses.length === 0) {
          const allBuildsData = await api.getBuilds({ port_name: portName, page_size: 1000 });
          const builderMap = new Map();
          allBuildsData.results?.forEach(build => {
            const name = build.builder_name?.name || build.buildername;
            const displayName = build.builder_name?.display_name || build.buildername || 'Unknown';
            if (name && !builderMap.has(name)) {
              builderMap.set(name, { name, displayName });
            }
          });
          const builders = Array.from(builderMap.values()).sort((a, b) => b.displayName.localeCompare(a.displayName));
          setAvailableBuilders(builders);
        }
      } catch (err) {
        console.error("Failed to fetch builds:", err);
      }
    }

    fetchBuilds();
  }, [portName, viewMode, activeTab, buildPage, selectedBuilders, selectedStatuses, buildsPerPage]);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (!target.closest('.dropdown-container')) {
        setShowBuilderDropdown(false);
        setShowStatusDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Fetch statistics data independently when stats tab is active or duration changes
  useEffect(() => {
    if (viewMode !== 'advanced' || activeTab !== 'stats' || !port) return;
    
    // Fetch basic installation stats
    async function fetchBasicStats() {
      setBasicStatsLoading(true);
      try {
        const basicStats = await api.getPortStats(portName, { 
          days: selectedDuration, 
          days_ago: selectedDaysAgo 
        });
        setPortStatistics(basicStats);
      } catch (err) {
        console.error('Failed to fetch basic stats:', err);
        setPortStatistics({ result: [] });
      } finally {
        setBasicStatsLoading(false);
      }
    }
    
    // Fetch OS version distribution
    async function fetchOsVersionStats() {
      setOsVersionLoading(true);
      try {
        const osVersionData = await api.getPortStats(portName, {
          days: selectedDuration,
          days_ago: selectedDaysAgo,
          property: ['submission__os_version', 'submission__build_arch', 'submission__cxx_stdlib'],
          sort_by: 'submission__os_version'
        });
        setOsVersionStats(osVersionData);
      } catch (err) {
        console.error('Failed to fetch OS version stats:', err);
        setOsVersionStats({ result: [] });
      } finally {
        setOsVersionLoading(false);
      }
    }
    
    // Fetch port version distribution
    async function fetchPortVersionStats() {
      setPortVersionLoading(true);
      try {
        const portVersionData = await api.getPortStats(portName, {
          days: selectedDuration,
          days_ago: selectedDaysAgo,
          property: ['version'],
          sort_by: 'version'
        });
        setPortVersionStats(portVersionData);
      } catch (err) {
        console.error('Failed to fetch port version stats:', err);
        setPortVersionStats({ result: [] });
      } finally {
        setPortVersionLoading(false);
      }
    }
    
    // Fetch Xcode version distribution
    async function fetchXcodeVersionStats() {
      setXcodeVersionLoading(true);
      try {
        const xcodeVersionData = await api.getPortStats(portName, {
          days: selectedDuration,
          days_ago: selectedDaysAgo,
          property: ['submission__os_version', 'submission__xcode_version'],
          sort_by: 'submission__os_version'
        });
        setXcodeVersionStats(xcodeVersionData);
      } catch (err) {
        console.error('Failed to fetch Xcode version stats:', err);
        setXcodeVersionStats({ result: [] });
      } finally {
        setXcodeVersionLoading(false);
      }
    }
    
    // Fetch CLT version distribution
    async function fetchCltVersionStats() {
      setCltVersionLoading(true);
      try {
        const cltVersionData = await api.getPortStats(portName, {
          days: selectedDuration,
          days_ago: selectedDaysAgo,
          property: ['submission__os_version', 'submission__clt_version'],
          sort_by: 'submission__os_version'
        });
        setCltVersionStats(cltVersionData);
      } catch (err) {
        console.error('Failed to fetch CLT version stats:', err);
        setCltVersionStats({ result: [] });
      } finally {
        setCltVersionLoading(false);
      }
    }
    
    // Fetch variants usage
    async function fetchVariantsStats() {
      setVariantsLoading(true);
      try {
        const variantsData = await api.getPortStats(portName, {
          days: selectedDuration,
          days_ago: selectedDaysAgo,
          property: ['variants']
        });
        setVariantsStats(variantsData);
      } catch (err) {
        console.error('Failed to fetch variants stats:', err);
        setVariantsStats({ result: [] });
      } finally {
        setVariantsLoading(false);
      }
    }
    
    // Fetch monthly installation data
    async function fetchMonthlyStats() {
      setMonthlyLoading(true);
      try {
        const monthlyData = await api.getPortMonthlyStats(portName, false);
        setMonthlyStats(monthlyData);
      } catch (err) {
        console.error('Failed to fetch monthly stats:', err);
        setMonthlyStats({ result: [] });
      } finally {
        setMonthlyLoading(false);
      }
    }
    
    // Fetch monthly version data
    async function fetchMonthlyVersionStats() {
      setMonthlyVersionLoading(true);
      try {
        const monthlyVersionData = await api.getPortMonthlyStats(portName, true);
        setMonthlyVersionStats(monthlyVersionData);
      } catch (err) {
        console.error('Failed to fetch monthly version stats:', err);
        setMonthlyVersionStats({ result: [] });
      } finally {
        setMonthlyVersionLoading(false);
      }
    }
    
    // Trigger all fetches independently
    fetchBasicStats();
    fetchOsVersionStats();
    fetchPortVersionStats();
    fetchXcodeVersionStats();
    fetchCltVersionStats();
    fetchVariantsStats();
    fetchMonthlyStats();
    fetchMonthlyVersionStats();
  }, [viewMode, activeTab, portName, selectedDuration, selectedDaysAgo, port]);

  // Fetch port health data (only when on info tab in advanced mode)
  useEffect(() => {
    async function fetchHealthData() {
      if (viewMode !== 'advanced' || activeTab !== 'info') return;
      
      setHealthLoading(true);
      try {
        const healthHtml = await api.getPortHealth(portName);
        const parsedHealth = parseHealthData(healthHtml);
        setHealthData(parsedHealth);
      } catch (err) {
        console.error('Failed to fetch health data:', err);
        setHealthData([]);
      } finally {
        setHealthLoading(false);
      }
    }

    fetchHealthData();
  }, [viewMode, activeTab, portName]);

  // Fetch port tickets data (only when on tickets tab in advanced mode)
  useEffect(() => {
    async function fetchTicketsData() {
      if (viewMode !== 'advanced' || activeTab !== 'tickets') return;
      
      setTicketsLoading(true);
      try {
        const ticketsHtml = await api.getPortTickets(portName);
        const { tickets, count } = parseTicketsData(ticketsHtml);
        setTicketsData(tickets);
        setTicketsCount(count);
      } catch (err) {
        console.error('Failed to fetch tickets data:', err);
        setTicketsData([]);
        setTicketsCount(0);
      } finally {
        setTicketsLoading(false);
      }
    }

    fetchTicketsData();
  }, [viewMode, activeTab, portName]);

  const copyInstallCommand = async () => {
    const command = `sudo port install ${portName}`;
    try {
      await navigator.clipboard.writeText(command);
      setCopiedCommand(true);
      setTimeout(() => setCopiedCommand(false), 2000);
    } catch (err) {
      // Fallback for browsers that don't support clipboard API
      console.error("Failed to copy to clipboard:", err);
    }
  };

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return "—";
    return new Date(dateString).toLocaleDateString();
  };

  const formatRelativeTime = (dateString: string | null | undefined) => {
    if (!dateString) return "—";
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return "Today";
    if (diffDays === 1) return "Yesterday";
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
    return `${Math.floor(diffDays / 365)} years ago`;
  };

  const getBuildStatusColor = (status: string | undefined) => {
    switch (status?.toLowerCase()) {
      case 'success': return 'text-green-400';
      case 'failure': return 'text-red-400';
      case 'in-progress': return 'text-yellow-400';
      default: return 'text-white/60';
    }
  };

  const getBuildStatusIcon = (status: string | undefined) => {
    switch (status?.toLowerCase()) {
      case 'success': 
      case 'build successful': return <CheckCircle className="h-4 w-4" />;
      case 'failure': 
      case 'build failed': return <AlertCircle className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  const getBuildUrl = (builderName: string, buildId: number) => {
    return `https://build.macports.org/builders/ports-${builderName}-builder/builds/${buildId}`;
  };

  const getWatcherUrl = (builderName: string, watcherId: number) => {
    return `https://build.macports.org/builders/ports-${builderName}-watcher/builds/${watcherId}`;
  };

  const formatElapsedTime = (seconds: number | null | undefined) => {
    if (!seconds) return "—";
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-brand-400"></div>
        <p className="mt-2 text-white/60">Loading port details...</p>
      </div>
    );
  }

  if (error || !port) {
    return (
      <div className="card text-center py-12">
        <Package className="h-12 w-12 text-white/40 mx-auto mb-4" />
        <h1 className="text-2xl font-bold mb-2">Port Not Found</h1>
        <p className="text-white/60 mb-4">
          {error || `The port "${portName}" could not be found.`}
        </p>
        <a href="/ports" className="btn-primary">
          Browse All Ports
        </a>
      </div>
    );
  }

  // Basic View Component
  const BasicView = () => (
    <div className="space-y-6">
      {/* Hero Section */}
      <div className="text-center max-w-4xl mx-auto">
        <h1 className="text-4xl md:text-5xl font-bold mb-2">{port.name}</h1>
        {port.version && (
          <p className="text-xl text-white/80 mb-4">
            Version {port.version}
            {port.version_updated_at && (
              <span className="text-white/60 text-base ml-2">
                • Updated {formatRelativeTime(port.version_updated_at)}
              </span>
            )}
          </p>
        )}
        
        <p className="text-lg md:text-xl text-white/90 mb-6 leading-relaxed">
          {port.description || "No description available."}
        </p>

        {port.long_description && port.long_description !== port.description && (
          <div className="mb-6">
            <button
              onClick={() => setShowInstructions(!showInstructions)}
              className="text-brand-600 dark:text-brand-300 hover:text-brand-700 dark:hover:text-brand-200 flex items-center gap-2 mx-auto"
            >
              Learn more {showInstructions ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </button>
            {showInstructions && (
              <p className="text-white/80 mt-4 max-w-3xl mx-auto">
                {port.long_description}
              </p>
            )}
          </div>
        )}

        {port.homepage && (
          <p className="mb-6">
            <a href={port.homepage} target="_blank" rel="noopener noreferrer" 
               className="text-brand-600 dark:text-brand-300 hover:text-brand-700 dark:hover:text-brand-200 inline-flex items-center gap-2">
              <Globe className="h-4 w-4" />
              {port.homepage}
              <ExternalLink className="h-3 w-3" />
            </a>
          </p>
        )}

        {/* Installation Section */}
        {port.active && !port.replaced_by && (
          <div className="bg-gradient-to-br from-white/10 to-white/5 rounded-2xl p-8 border border-white/10">
            <p className="text-white/80 mb-4">
              To install {port.name}, paste this into the macOS Terminal after{' '}
              <a href="https://www.macports.org/install.php" className="text-brand-600 dark:text-brand-300 hover:text-brand-700 dark:hover:text-brand-200">
                installing MacPorts
              </a>
            </p>
            
            <div className="bg-gray-100 dark:bg-slate-900/80 rounded-lg p-4 mb-4 border border-gray-300 dark:border-white/10">
              <div className="flex items-center justify-between gap-4">
                <code className="text-brand-700 dark:text-brand-200 font-mono text-lg font-semibold">
                  sudo port install {portName}
                </code>
                <button
                  onClick={copyInstallCommand}
                  className="btn-secondary flex items-center gap-2 text-gray-900 dark:text-white bg-white/90 dark:bg-white/10 hover:bg-white dark:hover:bg-white/20 px-4 py-2 rounded-lg transition-colors font-medium"
                >
                  {copiedCommand ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                  {copiedCommand ? 'Copied!' : 'Copy'}
                </button>
              </div>
            </div>

            <div className="flex flex-wrap justify-center gap-4">
              <button
                onClick={toggleInstructions}
                className="btn-secondary flex items-center gap-2 transition-transform hover:scale-105"
              >
                {showInstructions ? (
                  <>
                    <ChevronUp className="h-4 w-4" />
                    Hide instructions
                  </>
                ) : (
                  <>
                    <ChevronDown className="h-4 w-4 animate-bounce" />
                    More instructions
                  </>
                )}
              </button>
              <a
                href={`https://trac.macports.org/newticket?port=${portName}`}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-secondary inline-flex items-center gap-2"
              >
                <Bug className="h-4 w-4" />
                Report an issue
              </a>
            </div>

            {/* Detailed Instructions */}
            <div 
              ref={instructionsRef}
              className={`overflow-hidden transition-all duration-500 ease-in-out ${showInstructions ? 'max-h-[1000px] opacity-100 mt-6 mb-4' : 'max-h-0 opacity-0 mt-0'}`}
            >
              <div className="pt-6 border-t border-white/10 text-left animate-fadeIn">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Terminal className="h-5 w-5 text-brand-300" />
                  Installation Instructions
                </h3>
                <div className="space-y-4 text-sm">
                  <div className="bg-gray-50 dark:bg-white/5 border border-gray-300 dark:border-white/10 rounded-lg p-4">
                    <p className="mb-2 font-medium text-gray-900 dark:text-white">1. If not done already, <a href="https://www.macports.org/install.php" className="text-brand-600 dark:text-brand-300 hover:text-brand-700 dark:hover:text-brand-200 underline">install MacPorts</a>.</p>
                  </div>
                  <div className="bg-gray-50 dark:bg-white/5 border border-gray-300 dark:border-white/10 rounded-lg p-4">
                    <p className="mb-3 font-medium text-gray-900 dark:text-white">2. To <strong>install</strong> {port.name}, run:</p>
                    <div className="bg-gray-100 dark:bg-slate-900/80 rounded-lg p-3 border border-gray-300 dark:border-white/5">
                      <code className="text-brand-700 dark:text-brand-200 font-mono font-semibold">sudo port install {portName}</code>
                    </div>
                  </div>
                  <div className="bg-gray-50 dark:bg-white/5 border border-gray-300 dark:border-white/10 rounded-lg p-4">
                    <p className="mb-3 font-medium text-gray-900 dark:text-white">3. To see what <strong>files</strong> were installed:</p>
                    <div className="bg-gray-100 dark:bg-slate-900/80 rounded-lg p-3 border border-gray-300 dark:border-white/5">
                      <code className="text-brand-700 dark:text-brand-200 font-mono font-semibold">port contents {portName}</code>
                    </div>
                  </div>
                  <div className="bg-gray-50 dark:bg-white/5 border border-gray-300 dark:border-white/10 rounded-lg p-4">
                    <p className="mb-3 font-medium text-gray-900 dark:text-white">4. To <strong>uninstall</strong> {port.name}:</p>
                    <div className="bg-gray-100 dark:bg-slate-900/80 rounded-lg p-3 border border-gray-300 dark:border-white/5">
                      <code className="text-brand-700 dark:text-brand-200 font-mono font-semibold">sudo port uninstall {portName}</code>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Warning if port is inactive or replaced */}
        {(!port.active || port.replaced_by) && (
          <div className="bg-red-500/20 border border-red-500/30 rounded-lg p-4 mb-6">
            <div className="flex items-center gap-2 text-red-300 mb-2">
              <AlertCircle className="h-5 w-5" />
              <span className="font-semibold">Port Notice</span>
            </div>
            {!port.active && (
              <p>This port is no longer active and may not be available for installation.</p>
            )}
            {port.replaced_by && (
              <p>This port has been replaced by <strong>{port.replaced_by}</strong>.</p>
            )}
          </div>
        )}
      </div>

      {/* Port Information Cards */}
      <div className="max-w-4xl mx-auto">
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {/* Categories */}
          {port.categories && Array.isArray(port.categories) && port.categories.length > 0 && (
            <div className="bg-white/5 border border-white/10 rounded-xl p-6 hover:bg-white/10 transition-colors">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-brand-500/20 rounded-lg">
                  <Tag className="h-5 w-5 text-brand-300" />
                </div>
                <h3 className="font-semibold text-white">Categories</h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {port.categories.map((category) => (
                  <a
                    key={category}
                    href={`/ports?category=${encodeURIComponent(category)}`}
                    className="px-3 py-1 bg-brand-500/20 hover:bg-brand-500/30 rounded-full text-sm transition-colors text-brand-600 dark:text-brand-200 hover:text-brand-700 dark:hover:text-brand-100 font-medium"
                  >
                    {category}
                  </a>
                ))}
              </div>
            </div>
          )}

          {/* Maintainers */}
          {port.maintainers && Array.isArray(port.maintainers) && port.maintainers.length > 0 && (
            <div className="bg-white/5 border border-white/10 rounded-xl p-6 hover:bg-white/10 transition-colors">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-green-500/20 rounded-lg">
                  <Users className="h-5 w-5 text-green-300" />
                </div>
                <h3 className="font-semibold text-white">Maintainers</h3>
              </div>
              <div className="space-y-2">
                {port.maintainers.slice(0, 3).map((maintainer, index) => (
                  <div key={index} className="text-sm">
                    {maintainer.github ? (
                      <a
                        href={`https://github.com/${maintainer.github}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-green-600 dark:text-green-300 hover:text-green-700 dark:hover:text-green-200 flex items-center gap-2 font-medium"
                      >
                        @{maintainer.github}
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    ) : (
                      <span className="text-gray-700 dark:text-white/80 font-medium">{maintainer.name || maintainer.email}</span>
                    )}
                  </div>
                ))}
                {port.maintainers.length > 3 && (
                  <div className="text-xs text-gray-500 dark:text-white/60">
                    +{port.maintainers.length - 3} more
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Quick Info */}
          <div className="bg-white/5 border border-white/10 rounded-xl p-6 hover:bg-white/10 transition-colors">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-purple-500/20 rounded-lg">
                <Info className="h-5 w-5 text-purple-300" />
              </div>
              <h3 className="font-semibold text-white">Details</h3>
            </div>
            <div className="space-y-3 text-sm">
              {port.license && (
                <div>
                  <div className="text-white/60 text-xs uppercase tracking-wide mb-1">License</div>
                  <div className="font-mono text-white/90">{port.license}</div>
                </div>
              )}
              {port.platforms && Array.isArray(port.platforms) && port.platforms.length > 0 && (
                <div>
                  <div className="text-white/60 text-xs uppercase tracking-wide mb-1">Platforms</div>
                  <div className="text-white/90">{port.platforms.join(', ')}</div>
                </div>
              )}
              {port.version_updated_at && (
                <div>
                  <div className="text-white/60 text-xs uppercase tracking-wide mb-1">Last Updated</div>
                  <div className="text-white/90">{formatRelativeTime(port.version_updated_at)}</div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Advanced View Component
  const AdvancedView = () => (
    <div className="space-y-6">
      <div className="card">
        <div className="flex items-start justify-between gap-6">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-3 mb-2">
              <Package className="h-8 w-8 text-brand-300" />
              <h1 className="text-3xl font-bold">{port.name}</h1>
              {port.version && (
                <span className="px-3 py-1 bg-brand-500 text-white text-sm rounded-full">
                  v{port.version}
                </span>
              )}
            </div>
            
            <p className="text-lg text-white/80 mb-4">
              {port.description || "No description available."}
            </p>

            {port.long_description && port.long_description !== port.description && (
              <p className="text-white/70 mb-4">
                {port.long_description}
              </p>
            )}

            <div className="flex flex-wrap gap-2 mb-4">
              {port.categories && Array.isArray(port.categories) && port.categories.map((category) => (
                <a
                  key={category}
                  href={`/ports?category=${encodeURIComponent(category)}`}
                  className="inline-flex items-center gap-1 px-2 py-1 bg-white/10 hover:bg-white/20 rounded-full text-sm transition-colors"
                >
                  <Tag className="h-3 w-3" />
                  {category}
                </a>
              ))}
            </div>

            <div className="flex flex-wrap gap-4 text-sm text-white/70">
              {port.version_updated_at && (
                <div className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  Updated {formatDate(port.version_updated_at)}
                </div>
              )}
              {port.maintainers && Array.isArray(port.maintainers) && port.maintainers.length > 0 && (
                <div className="flex items-center gap-1">
                  <Users className="h-4 w-4" />
                  {port.maintainers.length} maintainer{port.maintainers.length !== 1 ? 's' : ''}
                </div>
              )}
            </div>
          </div>

          <div className="space-y-3 shrink-0">
            <button
              onClick={copyInstallCommand}
              className="flex items-center gap-2 btn-primary"
            >
              {copiedCommand ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              {copiedCommand ? 'Copied!' : 'Copy Install Command'}
            </button>
            
            <div className="text-xs text-white/60 font-mono max-w-48">
              sudo port install {portName}
            </div>

            {port.homepage && (
              <a
                href={port.homepage}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-3 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-sm transition-colors"
              >
                <Globe className="h-4 w-4" />
                Homepage
                <ExternalLink className="h-3 w-3" />
              </a>
            )}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-white/10">
        <div className="flex gap-6">
          {[
            { id: 'info', label: 'Information', icon: Package },
            { id: 'builds', label: 'Build History', icon: GitBranch },
            { id: 'stats', label: 'Statistics', icon: BarChart3 },
            { id: 'tickets', label: 'Tickets', icon: Bug }
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => {
                setActiveTab(id as any);
                updateURL({ tab: id, page: 1 }); // Reset to page 1 when changing tabs
              }}
              className={`flex items-center gap-2 pb-3 border-b-2 transition-colors ${
                activeTab === id
                  ? 'border-brand-500 dark:border-brand-400 text-brand-600 dark:text-brand-300 font-semibold'
                  : 'border-transparent text-gray-600 dark:text-white/60 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              <Icon className="h-4 w-4" />
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'info' && (
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Left Section - Takes 2 columns */}
          <div className="lg:col-span-2 space-y-6">
            {/* Basic Info */}
            <div className="card">
              <h2 className="text-xl font-semibold mb-4">Basic Information</h2>
              <dl className="space-y-3">
              {port.created_at && (
                <div>
                  <dt className="text-sm text-white/60">Created</dt>
                  <dd className="text-sm">{formatDate(port.created_at)}</dd>
                </div>
              )}
              {port.license && (
                <div>
                  <dt className="text-sm text-white/60">License</dt>
                  <dd className="font-mono text-sm">{port.license}</dd>
                </div>
              )}
              {port.maintainers && Array.isArray(port.maintainers) && port.maintainers.length > 0 && (
                <div>
                  <dt className="text-sm text-white/60">Maintainers</dt>
                  <dd className="space-y-1">
                    {port.maintainers.map((maintainer, index) => (
                      <div key={index} className="text-sm">
                        {maintainer.github ? (
                          <a
                            href={`https://github.com/${maintainer.github}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-brand-600 dark:text-brand-300 hover:text-brand-700 dark:hover:text-brand-200"
                          >
                            @{maintainer.github}
                          </a>
                        ) : (
                          maintainer.name || maintainer.email
                        )}
                      </div>
                    ))}
                  </dd>
                </div>
              )}
              {port.openmaintainer !== undefined && (
                <div>
                  <dt className="text-sm text-white/60">Open Maintainer</dt>
                  <dd className="text-sm">{port.openmaintainer ? 'Yes' : 'No'}</dd>
                </div>
              )}
              {port.platforms && Array.isArray(port.platforms) && port.platforms.length > 0 && (
                <div>
                  <dt className="text-sm text-white/60">Platforms</dt>
                  <dd className="text-sm">{port.platforms.join(', ')}</dd>
                </div>
              )}
              {port.portdir && (
                <div>
                  <dt className="text-sm text-white/60">Port Directory</dt>
                  <dd className="font-mono text-sm">{port.portdir}</dd>
                </div>
              )}
              {port.replaced_by && (
                <div>
                  <dt className="text-sm text-white/60">Replaced By</dt>
                  <dd className="text-sm">
                    <a
                      href={`/ports/${encodeURIComponent(port.replaced_by)}`}
                      className="text-brand-600 dark:text-brand-300 hover:text-brand-700 dark:hover:text-brand-200"
                    >
                      {port.replaced_by}
                    </a>
                  </dd>
                </div>
              )}
              {port.submitter && (
                <div>
                  <dt className="text-sm text-white/60">Submitter</dt>
                  <dd className="text-sm">{port.submitter}</dd>
                </div>
              )}
              {port.updated_at && (
                <div>
                  <dt className="text-sm text-white/60">Updated</dt>
                  <dd className="text-sm">{formatDate(port.updated_at)}</dd>
                </div>
              )}
              {port.version_updated_at && (
                <div>
                  <dt className="text-sm text-white/60">Version Updated</dt>
                  <dd className="text-sm">{formatDate(port.version_updated_at)}</dd>
                </div>
              )}
              {port.variants && Array.isArray(port.variants) && port.variants.length > 0 && (
                <div>
                  <dt className="text-sm text-white/60">Variants</dt>
                  <dd className="text-sm">
                    <div className="flex flex-wrap gap-1">
                      {port.variants.map((variant, index) => {
                        const variantName = typeof variant === 'string' ? variant : variant.variant;
                        return (
                          <span key={index} className="px-2 py-1 bg-white/10 rounded text-xs font-mono">
                            +{variantName}
                          </span>
                        );
                      })}
                    </div>
                  </dd>
                </div>
                            )}
              </dl>

              {/* Port Notes */}
              {port.notes && (
                <div className="mt-6 pt-6 border-t border-white/10">
                  <h3 className="text-lg font-semibold mb-3">Port Notes</h3>
                  <div className="prose prose-invert max-w-none">
                    {port.notes.split('\n').map((line, index) => (
                      <p key={index} className="text-white/80 text-sm">
                        {line}
                      </p>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Dependencies and Dependents Grid */}
            <div className="grid gap-6 lg:grid-cols-2">
              {/* Dependencies - what this port depends on */}
              {port.dependencies && Array.isArray(port.dependencies) && port.dependencies.length > 0 && (
              <div className="card">
                <h3 className="text-lg font-semibold mb-3">Dependencies</h3>
                <div className="space-y-2">
                  {port.dependencies.map((depGroup, index) => (
                    <div key={index} className="border border-white/10 rounded-lg">
                      <button
                        onClick={() => setExpandedDeps(prev => ({
                          ...prev,
                          [`deps-${index}`]: !prev[`deps-${index}`]
                        }))}
                        className="w-full flex items-center justify-between p-3 text-left hover:bg-white/5 transition-colors"
                      >
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-medium text-white/70 uppercase tracking-wide">
                            {depGroup.type}
                          </span>
                          <span className="px-2 py-1 bg-brand-500/20 text-brand-700 dark:text-brand-300 text-xs rounded-full font-semibold">
                            {depGroup.ports?.length || 0}
                          </span>
                        </div>
                        {expandedDeps[`deps-${index}`] ? (
                          <ChevronUp className="h-3 w-3 text-white/60" />
                        ) : (
                          <ChevronDown className="h-3 w-3 text-white/60" />
                        )}
                      </button>
                      {expandedDeps[`deps-${index}`] && (
                        <div className="px-3 pb-3">
                          <div className="max-h-32 overflow-y-auto border border-white/5 rounded bg-black/20 p-2">
                            <div className="flex flex-wrap gap-1">
                              {depGroup.ports?.sort((a, b) => a.localeCompare(b)).map((portName, idx) => (
                                <a
                                  key={idx}
                                  href={`/ports/${encodeURIComponent(portName)}`}
                                  className="px-2 py-1 bg-white/5 hover:bg-white/10 rounded text-xs font-mono transition-colors whitespace-nowrap"
                                >
                                  {portName}
                                </a>
                              ))}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
              )}

              {/* Dependents - ports that depend on this port */}
              {port.depends_on && Array.isArray(port.depends_on) && port.depends_on.length > 0 && (
                <div className="card">
                <h3 className="text-lg font-semibold mb-3">Dependents</h3>
                <div className="space-y-2">
                  {port.depends_on.map((depGroup, index) => (
                    <div key={index} className="border border-white/10 rounded-lg">
                      <button
                        onClick={() => setExpandedDeps(prev => ({
                          ...prev,
                          [`dependents-${index}`]: !prev[`dependents-${index}`]
                        }))}
                        className="w-full flex items-center justify-between p-3 text-left hover:bg-white/5 transition-colors"
                      >
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-medium text-white/70 uppercase tracking-wide">
                            {depGroup.type}
                          </span>
                          <span className="px-2 py-1 bg-green-500/20 text-green-300 text-xs rounded-full">
                            {depGroup.ports?.length || 0}
                          </span>
                        </div>
                        {expandedDeps[`dependents-${index}`] ? (
                          <ChevronUp className="h-3 w-3 text-white/60" />
                        ) : (
                          <ChevronDown className="h-3 w-3 text-white/60" />
                        )}
                      </button>
                      {expandedDeps[`dependents-${index}`] && (
                        <div className="px-3 pb-3">
                          <div className="max-h-32 overflow-y-auto border border-white/5 rounded bg-black/20 p-2">
                            <div className="flex flex-wrap gap-1">
                              {depGroup.ports?.sort((a, b) => a.localeCompare(b)).map((portName, idx) => (
                                <a
                                  key={idx}
                                  href={`/ports/${encodeURIComponent(portName)}`}
                                  className="px-2 py-1 bg-white/5 hover:bg-white/10 rounded text-xs font-mono transition-colors whitespace-nowrap"
                                >
                                  {portName}
                                </a>
                              ))}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
                </div>
              )}
            </div>
          </div>

          {/* Right Section - Port Health */}
          <div>
            {/* Port Health - only in advanced mode */}
            {viewMode === 'advanced' && (
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Port Health</h3>
                {healthLoading ? (
                  <div className="flex items-center justify-center py-6">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-brand-500"></div>
                    <span className="ml-2 text-white/60 text-sm">Loading...</span>
                  </div>
                ) : healthData.length > 0 ? (
                  <div className="space-y-1">
                    {healthData.map((builder, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-white/5 rounded border border-white/10 hover:bg-white/10 transition-colors">
                        <div className="flex items-center gap-2">
                          {builder.status === 'success' ? (
                            <CheckCircle className="h-3 w-3 text-green-400" />
                          ) : builder.status === 'failure' ? (
                            <AlertCircle className="h-3 w-3 text-red-400" />
                          ) : (
                            <Clock className="h-3 w-3 text-yellow-400" />
                          )}
                          <div className="text-xs font-medium text-white">
                            {builder.name}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {builder.fileCount > 0 && (
                            <button
                              onClick={() => fetchBuildFiles(builder.buildId, builder.name)}
                              className="text-xs text-brand-600 dark:text-brand-300 hover:text-brand-700 dark:hover:text-brand-200 underline"
                            >
                              Files ({builder.fileCount})
                            </button>
                          )}
                          {builder.url && (
                            <a
                              href={builder.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-brand-600 dark:text-brand-300 hover:text-brand-700 dark:hover:text-brand-200"
                            >
                              <ExternalLink className="h-3 w-3" />
                            </a>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-6">
                    <Shield className="h-8 w-8 text-white/40 mx-auto mb-2" />
                    <p className="text-white/60 text-sm">No health data</p>
                  </div>
                )}
              </div>
            )}

            {/* Livecheck Results */}
            {port?.livecheck && (
              <div className="card mt-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Zap className="h-5 w-5 text-yellow-400" />
                  Livecheck Results
                </h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-white/5 rounded-lg border border-gray-200 dark:border-white/10">
                    <span className="text-gray-700 dark:text-white/80 text-sm">Has Check</span>
                    <span className={`font-medium ${port.livecheck.has_check ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                      {port.livecheck.has_check ? 'Yes' : 'No'}
                    </span>
                  </div>
                  
                  {port.livecheck.version && (
                    <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-white/5 rounded-lg border border-gray-200 dark:border-white/10">
                      <span className="text-gray-700 dark:text-white/80 text-sm">Latest Version</span>
                      <span className="text-brand-700 dark:text-brand-300 font-mono font-semibold">{port.livecheck.version}</span>
                    </div>
                  )}

                  {port.version && port.livecheck.version && port.version !== port.livecheck.version && (
                    <div className="p-3 bg-yellow-50 dark:bg-yellow-500/10 border border-yellow-200 dark:border-yellow-500/20 rounded-lg">
                      <div className="flex items-start gap-2">
                        <AlertCircle className="h-4 w-4 text-yellow-600 dark:text-yellow-400 mt-0.5 flex-shrink-0" />
                        <div className="text-sm">
                          <p className="font-medium text-yellow-800 dark:text-yellow-300 mb-1">Update Available</p>
                          <p className="text-yellow-700 dark:text-yellow-400">
                            Current: <code className="font-mono text-xs bg-yellow-100 dark:bg-yellow-900/30 px-1 py-0.5 rounded">{port.version}</code>
                            {' → '}
                            Latest: <code className="font-mono text-xs bg-yellow-100 dark:bg-yellow-900/30 px-1 py-0.5 rounded">{port.livecheck.version}</code>
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  {port.version && port.livecheck.version && port.version === port.livecheck.version && (
                    <div className="p-3 bg-green-50 dark:bg-green-500/10 border border-green-200 dark:border-green-500/20 rounded-lg">
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400 flex-shrink-0" />
                        <p className="text-sm text-green-700 dark:text-green-300 font-medium">Port is up to date</p>
                      </div>
                    </div>
                  )}
                  
                  {port.livecheck.last_updated && (
                    <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-white/5 rounded-lg border border-gray-200 dark:border-white/10">
                      <span className="text-gray-700 dark:text-white/80 text-sm">Last Checked</span>
                      <span className="text-gray-600 dark:text-white/60 text-sm">{formatRelativeTime(port.livecheck.last_updated)}</span>
                    </div>
                  )}

                  {port.livecheck.result && (
                    <div className="p-3 bg-gray-50 dark:bg-white/5 rounded-lg border border-gray-200 dark:border-white/10">
                      <p className="text-xs text-gray-600 dark:text-white/60 mb-1">Result</p>
                      <p className="text-sm text-gray-800 dark:text-white/80 font-mono break-all">{port.livecheck.result}</p>
                    </div>
                  )}

                  {port.livecheck.error && (
                    <div className="p-3 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 rounded-lg">
                      <div className="flex items-start gap-2">
                        <AlertCircle className="h-4 w-4 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
                        <div className="text-sm">
                          <p className="font-medium text-red-800 dark:text-red-300 mb-1">Livecheck Error</p>
                          <p className="text-red-700 dark:text-red-400 font-mono text-xs">{port.livecheck.error}</p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'builds' && (
        <div className="card">
          <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <h2 className="text-xl font-semibold">Build History</h2>
              
              {/* Clear Filters */}
              {(selectedBuilders.length > 0 || selectedStatuses.length > 0) && (
                <button
                  onClick={() => {
                    setSelectedBuilders([]);
                    setSelectedStatuses([]);
                    setBuildPage(1);
                    updateURL({ builders: [], statuses: [], page: 1 });
                  }}
                  className="text-sm text-brand-600 dark:text-brand-300 hover:text-brand-700 dark:hover:text-brand-200 transition-colors"
                >
                  Clear all filters
                </button>
              )}
            </div>

            {/* Dropdown Filters */}
            <div className="flex flex-col sm:flex-row gap-4">
              {/* Builder Dropdown */}
              <div className="relative flex-1 dropdown-container">
                <label className="block text-sm font-medium text-white/80 mb-2">
                  Builder
                </label>
                <button
                  onClick={() => {
                    setShowBuilderDropdown(!showBuilderDropdown);
                    setShowStatusDropdown(false);
                  }}
                  className="w-full flex items-center justify-between px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white text-sm hover:bg-white/15 focus:outline-none focus:ring-2 focus:ring-brand-500 transition-colors"
                >
                  <span className="font-mono">
                    {selectedBuilders.length === 0 
                      ? 'All Builders' 
                      : selectedBuilders.length === 1 
                      ? availableBuilders.find(b => b.name === selectedBuilders[0])?.displayName || selectedBuilders[0]
                      : `${selectedBuilders.length} builders selected`
                    }
                  </span>
                  <ChevronDown className={`h-4 w-4 transition-transform ${showBuilderDropdown ? 'rotate-180' : ''}`} />
                </button>
                
                {showBuilderDropdown && (
                  <div className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-slate-800 border border-gray-300 dark:border-white/20 rounded-lg shadow-xl z-50 max-h-60 overflow-y-auto">
                    {availableBuilders.map((builder) => {
                      const isSelected = selectedBuilders.includes(builder.name);
                      return (
                        <button
                          key={builder.name}
                          onClick={() => {
                            const newBuilders = isSelected
                              ? selectedBuilders.filter(b => b !== builder.name)
                              : [...selectedBuilders, builder.name];
                            setSelectedBuilders(newBuilders);
                            setBuildPage(1);
                            updateURL({ builders: newBuilders, page: 1 });
                          }}
                          className={`w-full text-left px-4 py-3 text-sm font-mono hover:bg-gray-100 dark:hover:bg-white/10 transition-colors flex items-center justify-between ${
                            isSelected 
                              ? 'bg-brand-100 dark:bg-brand-500/20 text-brand-700 dark:text-brand-300 font-semibold' 
                              : 'text-gray-700 dark:text-white/80'
                          }`}
                        >
                          <span>{builder.displayName}</span>
                          {isSelected && (
                            <div className="w-2 h-2 bg-brand-600 dark:bg-brand-400 rounded-full"></div>
                          )}
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Status Dropdown */}
              <div className="relative flex-1 dropdown-container">
                <label className="block text-sm font-medium text-white/80 mb-2">
                  Status
                </label>
                <button
                  onClick={() => {
                    setShowStatusDropdown(!showStatusDropdown);
                    setShowBuilderDropdown(false);
                  }}
                  className="w-full flex items-center justify-between px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white text-sm hover:bg-white/15 focus:outline-none focus:ring-2 focus:ring-brand-500 transition-colors"
                >
                  <span>
                    {selectedStatuses.length === 0 
                      ? 'All Status' 
                      : selectedStatuses.length === 1 
                      ? availableStatuses.find(s => s.value === selectedStatuses[0])?.label || selectedStatuses[0]
                      : `${selectedStatuses.length} statuses selected`
                    }
                  </span>
                  <ChevronDown className={`h-4 w-4 transition-transform ${showStatusDropdown ? 'rotate-180' : ''}`} />
                </button>
                
                {showStatusDropdown && (
                  <div className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-slate-800 border border-gray-300 dark:border-white/20 rounded-lg shadow-xl z-50 max-h-60 overflow-y-auto">
                    {availableStatuses.map((status) => {
                      const isSelected = selectedStatuses.includes(status.value);
                      return (
                        <button
                          key={status.value}
                          onClick={() => {
                            const newStatuses = isSelected
                              ? selectedStatuses.filter(s => s !== status.value)
                              : [...selectedStatuses, status.value];
                            setSelectedStatuses(newStatuses);
                            setBuildPage(1);
                            updateURL({ statuses: newStatuses, page: 1 });
                          }}
                          className={`w-full text-left px-4 py-3 text-sm hover:bg-gray-100 dark:hover:bg-white/10 transition-colors flex items-center justify-between ${
                            isSelected 
                              ? 'bg-green-100 dark:bg-green-500/20 text-green-700 dark:text-green-300 font-semibold' 
                              : 'text-gray-700 dark:text-white/80'
                          }`}
                        >
                          <span>{status.label}</span>
                          {isSelected && (
                            <div className="w-2 h-2 bg-green-600 dark:bg-green-400 rounded-full"></div>
                          )}
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Clear Filters Button */}
              {(selectedBuilders.length > 0 || selectedStatuses.length > 0) && (
                <div className="flex items-end">
                  <button
                    onClick={() => {
                      setSelectedBuilders([]);
                      setSelectedStatuses([]);
                      setBuildPage(1);
                      updateURL({ builders: [], statuses: [], page: 1 });
                      setShowBuilderDropdown(false);
                      setShowStatusDropdown(false);
                    }}
                    className="px-4 py-3 bg-red-500/20 hover:bg-red-500/30 text-red-300 border border-red-500/30 rounded-lg text-sm font-medium transition-colors whitespace-nowrap"
                  >
                    Clear Filters
                  </button>
                </div>
              )}
            </div>
          </div>

          {builds.length === 0 ? (
            <p className="text-white/60 text-center py-8">No build history available.</p>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-white/10">
                      <th className="text-left py-3 px-2 text-white/60 font-medium">Builder</th>
                      <th className="text-left py-3 px-2 text-white/60 font-medium">Build #</th>
                      <th className="text-left py-3 px-2 text-white/60 font-medium">Start Time</th>
                      <th className="text-left py-3 px-2 text-white/60 font-medium">Duration</th>
                      <th className="text-left py-3 px-2 text-white/60 font-medium">Watcher</th>
                      <th className="text-left py-3 px-2 text-white/60 font-medium">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {builds.map((build) => (
                      <tr key={build.id} className="border-b border-white/5 hover:bg-white/5">
                        <td className="py-3 px-2">
                          <div className="font-mono text-sm">
                            {build.builder_name?.display_name || build.buildername || '—'}
                          </div>
                        </td>
                        <td className="py-3 px-2">
                          {build.build_id && build.builder_name?.name ? (
                            <a
                              href={getBuildUrl(build.builder_name.name, build.build_id)}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-brand-600 dark:text-brand-300 hover:text-brand-700 dark:hover:text-brand-200 flex items-center gap-1"
                            >
                              {build.build_id}
                              <ExternalLink className="h-3 w-3" />
                            </a>
                          ) : (
                            <span className="text-white/60">—</span>
                          )}
                        </td>
                        <td className="py-3 px-2">
                          <div className="text-white/80">
                            {formatDate(build.time_start)}
                          </div>
                          <div className="text-xs text-white/60">
                            {build.time_start && new Date(build.time_start).toLocaleTimeString()}
                          </div>
                        </td>
                        <td className="py-3 px-2">
                          <span className="text-white/80">
                            {formatElapsedTime(build.time_elapsed)}
                          </span>
                        </td>
                        <td className="py-3 px-2">
                          {build.watcher_id && build.builder_name?.name ? (
                            <a
                              href={getWatcherUrl(build.builder_name.name, build.watcher_id)}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-brand-600 dark:text-brand-300 hover:text-brand-700 dark:hover:text-brand-200 flex items-center gap-1"
                            >
                              {build.watcher_id}
                              <ExternalLink className="h-3 w-3" />
                            </a>
                          ) : (
                            <span className="text-white/60">—</span>
                          )}
                        </td>
                        <td className="py-3 px-2">
                          <div className={`flex items-center gap-2 ${getBuildStatusColor(build.status)}`}>
                            {getBuildStatusIcon(build.status)}
                            <span className="font-medium">
                              {build.status || 'Unknown'}
                            </span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {totalBuilds > buildsPerPage && (
                <div className="flex items-center justify-between mt-6 pt-4 border-t border-white/10">
                  <div className="text-sm text-white/60">
                    Showing {((buildPage - 1) * buildsPerPage) + 1} to {Math.min(buildPage * buildsPerPage, totalBuilds)} of {totalBuilds} builds
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => {
                        const newPage = Math.max(1, buildPage - 1);
                        setBuildPage(newPage);
                        updateURL({ page: newPage });
                      }}
                      disabled={buildPage === 1}
                      className="px-3 py-2 bg-white/10 hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-sm transition-colors"
                    >
                      Previous
                    </button>
                    
                    <span className="px-3 py-2 text-sm text-white/80">
                      Page {buildPage} of {Math.ceil(totalBuilds / buildsPerPage)}
                    </span>
                    
                    <button
                      onClick={() => {
                        const newPage = buildPage + 1;
                        setBuildPage(newPage);
                        updateURL({ page: newPage });
                      }}
                      disabled={buildPage >= Math.ceil(totalBuilds / buildsPerPage)}
                      className="px-3 py-2 bg-white/10 hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-sm transition-colors"
                    >
                      Next
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {activeTab === 'stats' && (
        <div className="space-y-6">
          {/* Stats Header & Duration Selector */}
          <div className="card">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
              <h2 className="text-xl font-semibold">Installation Statistics</h2>
              
              {/* Duration Selector */}
              <div className="flex flex-wrap gap-2">
                {[
                  { days: 7, label: '7 days' },
                  { days: 30, label: '30 days' },
                  { days: 90, label: '90 days' },
                  { days: 180, label: '180 days' },
                  { days: 365, label: '365 days' }
                ].map(({ days, label }) => {
                  const isSelected = days === selectedDuration;
                  return (
                    <button
                      key={days}
                      onClick={() => setSelectedDuration(days)}
                      className={`px-3 py-2 text-sm rounded-lg transition-colors ${
                        isSelected
                          ? 'bg-brand-500/30 text-brand-700 dark:text-brand-200 border border-brand-500 dark:border-brand-400/50 font-semibold'
                          : 'bg-gray-100 dark:bg-white/5 text-gray-600 dark:text-white/70 hover:bg-gray-200 dark:hover:bg-white/10 border border-gray-300 dark:border-white/20'
                      }`}
                    >
                      {label}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Main Stats Grid */}
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
              <div className="bg-gradient-to-br from-brand-500/20 to-brand-600/10 border border-brand-500/30 rounded-xl p-6">
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 bg-brand-500/20 rounded-lg">
                    <Download className="h-5 w-5 text-brand-400" />
                  </div>
                  <div>
                    <p className="text-sm text-white/60">Total Installations</p>
                    <p className="text-2xl font-bold text-brand-600 dark:text-brand-300">
                      {(() => {
                        if (portStatistics?.result?.length > 0) {
                          const total = portStatistics.result.reduce((sum: number, item: any) => sum + (item.count || 0), 0);
                          return total.toLocaleString();
                        }
                        return portStats?.all?.toLocaleString() || '—';
                      })()}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-green-500/20 to-green-600/10 border border-green-500/30 rounded-xl p-6">
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 bg-green-500/20 rounded-lg">
                    <Users className="h-5 w-5 text-green-400" />
                  </div>
                  <div>
                    <p className="text-sm text-white/60">Requested Installations</p>
                    <p className="text-2xl font-bold text-green-300">
                      {portStats?.requested?.toLocaleString() || '—'}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/10 border border-purple-500/30 rounded-xl p-6">
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 bg-purple-500/20 rounded-lg">
                    <Monitor className="h-5 w-5 text-purple-400" />
                  </div>
                  <div>
                    <p className="text-sm text-white/60">Most Installed on macOS Version</p>
                    <p className="text-lg font-bold text-purple-300">
                      {(() => {
                        if (osVersionStats?.result?.length > 0) {
                          const sortedOS = [...osVersionStats.result]
                            .sort((a: any, b: any) => (b.count || 0) - (a.count || 0));
                          const topOS = sortedOS[0];
                          if (topOS?.submission__os_version) {
                            const totalCount = osVersionStats.result.reduce((sum: number, item: any) => sum + (item.count || 0), 0);
                            const percentage = totalCount > 0 ? ((topOS.count || 0) / totalCount * 100).toFixed(1) : '0.0';
                            return `${topOS.submission__os_version} (${percentage}%)`;
                          }
                          return '—';
                        }
                        return '—';
                      })()}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-orange-500/20 to-orange-600/10 border border-orange-500/30 rounded-xl p-6">
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 bg-orange-500/20 rounded-lg">
                    <Package className="h-5 w-5 text-orange-400" />
                  </div>
                  <div>
                    <p className="text-sm text-white/60">Most Popular Version</p>
                    <p className="text-2xl font-bold text-orange-300">
                      {(() => {
                        if (portVersionStats?.result?.length > 0) {
                          const sortedVersions = [...portVersionStats.result]
                            .sort((a: any, b: any) => (b.count || 0) - (a.count || 0));
                          const topVersion = sortedVersions[0];
                          if (topVersion?.version) {
                            const totalCount = portVersionStats.result.reduce((sum: number, item: any) => sum + (item.count || 0), 0);
                            const percentage = totalCount > 0 ? ((topVersion.count || 0) / totalCount * 100).toFixed(1) : '0.0';
                            return `${topVersion.version} (${percentage}%)`;
                          }
                          return '—';
                        }
                        return '—';
                      })()}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Charts Grid */}
          <div className="grid gap-6 lg:grid-cols-2">
            {/* macOS Versions Chart */}
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">macOS Versions</h3>
              <div className="h-64">
                {osVersionLoading ? (
                  <div className="h-full flex items-center justify-center bg-white/5 rounded-lg border border-white/10">
                    <div className="text-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-500 mx-auto mb-2"></div>
                      <p className="text-white/60 text-sm">Loading...</p>
                    </div>
                  </div>
                ) : osVersionStats?.result && osVersionStats.result.length > 0 ? (
                  <Bar 
                    data={createBarChartData(osVersionStats.result, 'submission__os_version', 'count', 'macOS Versions')} 
                    options={chartOptions} 
                  />
                ) : (
                  <div className="h-full flex items-center justify-center bg-white/5 rounded-lg border border-white/10">
                    <div className="text-center">
                      <BarChart3 className="h-12 w-12 text-white/40 mx-auto mb-2" />
                      <p className="text-white/60">No data available</p>
                      <p className="text-xs text-white/40 mt-1">Distribution of macOS versions</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Port Versions Chart */}
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Port Versions</h3>
              <div className="h-64">
                {portVersionLoading ? (
                  <div className="h-full flex items-center justify-center bg-white/5 rounded-lg border border-white/10">
                    <div className="text-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-500 mx-auto mb-2"></div>
                      <p className="text-white/60 text-sm">Loading...</p>
                    </div>
                  </div>
                ) : portVersionStats?.result && portVersionStats.result.length > 0 ? (
                  <Bar 
                    data={createBarChartData(portVersionStats.result, 'version', 'count', 'Port Versions')} 
                    options={chartOptions} 
                  />
                ) : (
                  <div className="h-full flex items-center justify-center bg-white/5 rounded-lg border border-white/10">
                    <div className="text-center">
                      <BarChart3 className="h-12 w-12 text-white/40 mx-auto mb-2" />
                      <p className="text-white/60">No data available</p>
                      <p className="text-xs text-white/40 mt-1">Version usage statistics</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Xcode Versions Chart */}
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Xcode Versions</h3>
              <div className="h-64">
                {xcodeVersionLoading ? (
                  <div className="h-full flex items-center justify-center bg-white/5 rounded-lg border border-white/10">
                    <div className="text-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-500 mx-auto mb-2"></div>
                      <p className="text-white/60 text-sm">Loading...</p>
                    </div>
                  </div>
                ) : xcodeVersionStats?.result && xcodeVersionStats.result.length > 0 ? (
                  <Bar 
                    data={createStackedBarChartData(xcodeVersionStats.result, 'Xcode Versions')} 
                    options={{
                      ...chartOptions,
                      plugins: {
                        ...chartOptions.plugins,
                        legend: {
                          display: false
                        }
                      },
                      scales: {
                        x: {
                          stacked: true,
                          ticks: {
                            color: '#fff'
                          },
                          grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                          }
                        },
                        y: {
                          stacked: true,
                          ticks: {
                            color: '#fff'
                          },
                          grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                          }
                        }
                      }
                    }} 
                  />
                ) : (
                  <div className="h-full flex items-center justify-center bg-white/5 rounded-lg border border-white/10">
                    <div className="text-center">
                      <Code className="h-12 w-12 text-white/40 mx-auto mb-2" />
                      <p className="text-white/60">No data available</p>
                      <p className="text-xs text-white/40 mt-1">Xcode version distribution</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* CLT Versions Chart */}
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">CLT Versions</h3>
              <div className="h-64">
                {cltVersionLoading ? (
                  <div className="h-full flex items-center justify-center bg-white/5 rounded-lg border border-white/10">
                    <div className="text-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-500 mx-auto mb-2"></div>
                      <p className="text-white/60 text-sm">Loading...</p>
                    </div>
                  </div>
                ) : cltVersionStats?.result && cltVersionStats.result.length > 0 ? (
                  <Bar 
                    data={createCltStackedBarChartData(cltVersionStats.result, 'CLT Versions')} 
                    options={{
                      ...chartOptions,
                      plugins: {
                        ...chartOptions.plugins,
                        legend: {
                          display: false
                        }
                      },
                      scales: {
                        x: {
                          stacked: true,
                          ticks: {
                            color: '#fff'
                          },
                          grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                          }
                        },
                        y: {
                          stacked: true,
                          ticks: {
                            color: '#fff'
                          },
                          grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                          }
                        }
                      }
                    }} 
                  />
                ) : (
                  <div className="h-full flex items-center justify-center bg-white/5 rounded-lg border border-white/10">
                    <div className="text-center">
                      <Code className="h-12 w-12 text-white/40 mx-auto mb-2" />
                      <p className="text-white/60">No data available</p>
                      <p className="text-xs text-white/40 mt-1">Command Line Tools versions</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Variants Table */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Variants Usage</h3>
            {variantsLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-500 mx-auto mb-2"></div>
                <p className="text-white/60 text-sm">Loading...</p>
              </div>
            ) : variantsStats?.result && variantsStats.result.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-white/10">
                      <th className="text-left py-3 px-2 text-white/60 font-medium">Variant</th>
                      <th className="text-right py-3 px-2 text-white/60 font-medium">Count</th>
                      <th className="text-right py-3 px-2 text-white/60 font-medium">Percentage</th>
                    </tr>
                  </thead>
                  <tbody>
                    {variantsStats.result.map((variant: any, index: number) => {
                      const total = variantsStats.result.reduce((sum: number, v: any) => sum + (v.count || 0), 0);
                      const percentage = total > 0 ? ((variant.count / total) * 100).toFixed(1) : '0.0';
                      
                      return (
                        <tr key={index} className="border-b border-white/5 hover:bg-white/5">
                          <td className="py-3 px-2">
                            <span className="font-mono text-brand-600 dark:text-brand-300 font-semibold">+{variant.variants || 'default'}</span>
                          </td>
                          <td className="py-3 px-2 text-right text-white/80">
                            {variant.count?.toLocaleString() || 0}
                          </td>
                          <td className="py-3 px-2 text-right text-white/60">
                            {percentage}%
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-8 text-white/60">
                <BarChart3 className="h-12 w-12 mx-auto mb-2 text-white/40" />
                <p>No variant usage data available</p>
              </div>
            )}
          </div>

          {/* Monthly Statistics */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Monthly Statistics</h3>
            <p className="text-sm text-white/60 mb-6">Installation trends over time</p>
            
            <div className="space-y-6">
              {/* Monthly Installations Chart */}
              <div>
                <h4 className="text-md font-medium mb-3 text-white/80">Port installations by month</h4>
                <div className="h-64">
                  {monthlyLoading ? (
                    <div className="h-full flex items-center justify-center bg-white/5 rounded-lg border border-white/10">
                      <div className="text-center">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-500 mx-auto mb-2"></div>
                        <p className="text-white/60 text-sm">Loading...</p>
                      </div>
                    </div>
                  ) : monthlyStats?.result && monthlyStats.result.length > 0 ? (
                    <Line 
                      data={createLineChartData(monthlyStats.result, 'Installations')} 
                      options={chartOptions} 
                    />
                  ) : (
                    <div className="h-full flex items-center justify-center bg-white/5 rounded-lg border border-white/10">
                      <div className="text-center">
                        <BarChart3 className="h-12 w-12 text-white/40 mx-auto mb-2" />
                        <p className="text-white/60">No monthly data available</p>
                        <p className="text-xs text-white/40 mt-1">Installation volume by month</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Version Percentage Chart */}
              <div>
                <h4 className="text-md font-medium mb-3 text-white/80">Percentage of installations per version per month</h4>
                <div className="h-64">
                  {monthlyVersionLoading ? (
                    <div className="h-full flex items-center justify-center bg-white/5 rounded-lg border border-white/10">
                      <div className="text-center">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-500 mx-auto mb-2"></div>
                        <p className="text-white/60 text-sm">Loading...</p>
                      </div>
                    </div>
                  ) : monthlyVersionStats?.result && monthlyVersionStats.result.length > 0 ? (
                    <Line 
                      data={createMonthlyPercentageChartData(monthlyVersionStats.result, 'Version %')} 
                      options={{
                        ...chartOptions,
                        plugins: {
                          ...chartOptions.plugins,
                          legend: {
                            display: false,
                            labels: {
                              color: '#fff'
                            }
                          }
                        },
                        scales: {
                          x: {
                            ticks: {
                              color: '#fff'
                            },
                            grid: {
                              color: 'rgba(255, 255, 255, 0.1)'
                            }
                          },
                          y: {
                            min: 0,
                            max: 100,
                            ticks: {
                              color: '#fff',
                              callback: function(value: any) {
                                return value + '%';
                              }
                            },
                            grid: {
                              color: 'rgba(255, 255, 255, 0.1)'
                            }
                          }
                        }
                      }} 
                    />
                  ) : (
                    <div className="h-full flex items-center justify-center bg-white/5 rounded-lg border border-white/10">
                      <div className="text-center">
                        <BarChart3 className="h-12 w-12 text-white/40 mx-auto mb-2" />
                        <p className="text-white/60">No version data available</p>
                        <p className="text-xs text-white/40 mt-1">Version distribution trends</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

        </div>
      )}




      {activeTab === 'tickets' && (
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Tickets List - Takes 2 columns */}
          <div className="lg:col-span-2">
            {ticketsLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-500"></div>
                <span className="ml-3 text-white/60">Loading tickets...</span>
              </div>
            ) : ticketsData.length > 0 ? (
              <div className="space-y-3">
                {ticketsData.map((ticket, index) => (
                  <div key={index} className="p-4 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3 mb-2">
                          <a
                            href={ticket.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-brand-600 dark:text-brand-300 hover:text-brand-700 dark:hover:text-brand-200 font-medium flex items-center gap-1"
                          >
                            {ticket.id}
                            <ExternalLink className="h-3 w-3" />
                          </a>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            ticket.priority === 'high' 
                              ? 'bg-red-500/20 text-red-600 dark:text-red-300'
                              : ticket.priority === 'medium'
                              ? 'bg-yellow-500/20 text-yellow-700 dark:text-yellow-300'
                              : 'bg-blue-500/20 text-blue-700 dark:text-blue-300'
                          }`}>
                            {ticket.type}
                          </span>
                        </div>
                        <p className="text-white/80 text-sm line-clamp-2">
                          {ticket.title}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Bug className="h-12 w-12 text-white/40 mx-auto mb-4" />
                <p className="text-white/60">No open tickets found</p>
                <p className="text-white/40 text-sm mt-2">This port has no reported issues</p>
              </div>
            )}
          </div>

          {/* Actions Sidebar */}
          <div className="space-y-3">
            <a
              href={`https://trac.macports.org/report/16?max=1000&PORT=(%5E%7C%5Cs%7C,)${portName}($%7C%5Cs%7C,)`}
              target="_blank"
              rel="noopener noreferrer"
              className="block p-4 bg-white/5 hover:bg-white/10 rounded-lg border border-white/10 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Bug className="h-5 w-5 text-brand-400" />
                  <div>
                    <div className="font-medium text-white">View All Tickets</div>
                    <div className="text-xs text-white/60">Browse complete list</div>
                  </div>
                </div>
                <ExternalLink className="h-4 w-4 text-white/60" />
              </div>
            </a>
            
            <a
              href={`https://trac.macports.org/newticket?port=${portName}`}
              target="_blank"
              rel="noopener noreferrer"
              className="block p-4 bg-white/5 hover:bg-white/10 rounded-lg border border-white/10 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Wrench className="h-5 w-5 text-green-400" />
                  <div>
                    <div className="font-medium text-white">Report Issue</div>
                    <div className="text-xs text-white/60">Create new ticket</div>
                  </div>
                </div>
                <ExternalLink className="h-4 w-4 text-white/60" />
              </div>
            </a>
          </div>
        </div>
      )}

      {activeTab === 'health' && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Port Health</h2>
          {healthLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-500"></div>
              <span className="ml-3 text-white/60">Loading port health...</span>
            </div>
          ) : healthData.length > 0 ? (
            <div className="space-y-3">
              {healthData.map((builder, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors">
                  <div className="flex items-center gap-3">
                    {builder.status === 'success' ? (
                      <CheckCircle className="h-5 w-5 text-green-400" />
                    ) : builder.status === 'failure' ? (
                      <AlertCircle className="h-5 w-5 text-red-400" />
                    ) : (
                      <Clock className="h-5 w-5 text-yellow-400" />
                    )}
                    <div>
                      <div className="font-medium text-white">
                        {builder.name}
                      </div>
                      {builder.fileCount > 0 && (
                        <button
                          onClick={() => fetchBuildFiles(builder.buildId, builder.name)}
                          className="text-xs text-brand-600 dark:text-brand-300 hover:text-brand-700 dark:hover:text-brand-200 underline cursor-pointer"
                        >
                          Files ({builder.fileCount.toLocaleString()})
                        </button>
                      )}
                    </div>
                  </div>
                  {builder.url && (
                    <a
                      href={builder.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-brand-600 dark:text-brand-300 hover:text-brand-700 dark:hover:text-brand-200 flex items-center gap-1"
                    >
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  )}
                </div>
              ))}
              <div className="text-xs text-white/40 text-right pt-2">
                <Clock className="inline h-3 w-3 mr-1" />
                No history in app's database
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <Shield className="h-12 w-12 text-white/40 mx-auto mb-4" />
              <p className="text-white/60">No health data available</p>
            </div>
          )}
        </div>
      )}
    </div>
  );

  // Files Modal Component
  const FilesModal = () => {
    if (!showFilesModal) return null;
    
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <div className="bg-slate-800 rounded-lg border border-white/20 w-full max-w-4xl max-h-[80vh] overflow-hidden">
          <div className="flex items-center justify-between p-6 border-b border-white/10">
            <h3 className="text-lg font-semibold text-white">
              Files ({selectedBuilderName})
            </h3>
            <button
              onClick={() => {
                setShowFilesModal(false);
                setBuildFiles([]);
                setSelectedBuildId(null);
                setSelectedBuilderName('');
              }}
              className="text-white/60 hover:text-white"
            >
              <X className="h-6 w-6" />
            </button>
          </div>
          
          <div className="p-6 overflow-auto max-h-[60vh]">
            {filesLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-500"></div>
                <span className="ml-3 text-white/60">Loading files...</span>
              </div>
            ) : buildFiles.length > 0 ? (
              <div className="space-y-2">
                {buildFiles.map((file, index) => (
                  <div key={index} className="p-3 bg-white/5 rounded border border-white/10 text-sm font-mono text-white/80">
                    {file}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Package className="h-12 w-12 text-white/40 mx-auto mb-4" />
                <p className="text-white/60">No files found</p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* View Toggle */}
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-4">
          <a href="/ports" className="text-white/60 hover:text-white text-sm">
            ← Back to Ports
          </a>
        </div>
        
        <button
          onClick={toggleViewMode}
          className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
        >
          {viewMode === 'basic' ? (
            <>
              <Settings className="h-4 w-4" />
              Advanced View
            </>
          ) : (
            <>
              <Eye className="h-4 w-4" />
              Basic View
            </>
          )}
        </button>
      </div>

      {/* Content */}
      {viewMode === 'basic' ? <BasicView /> : <AdvancedView />}
      
      {/* Files Modal */}
      <FilesModal />
    </div>
  );
}