"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api-client";
import type { Port, Category, Maintainer, SearchResult } from "@/lib/types";
import { 
  Search, 
  Package, 
  Tag, 
  User,
  Filter,
  ChevronLeft, 
  ChevronRight,
  Grid3X3,
  List,
  SortAsc,
  SortDesc,
  X,
  Github,
  Mail,
  FileText,
  ChevronDown
} from "lucide-react";

type DisplayMode = 'grid' | 'list';
type SortOption = 'name';

export default function AllPortsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  // URL State Management
  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [searchInput, setSearchInput] = useState(searchParams.get('q') || '');

  const [displayMode, setDisplayMode] = useState<DisplayMode>(() => {
    // Check localStorage first, then URL, then default to 'grid'
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('macports-display-mode') as DisplayMode;
      if (stored === 'grid' || stored === 'list') return stored;
    }
    return (searchParams.get('display') as DisplayMode) || 'grid';
  });
  const [sortBy, setSortBy] = useState<SortOption>(
    (searchParams.get('sort') as SortOption) || 'name'
  );
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>(
    (searchParams.get('order') as 'asc' | 'desc') || 'asc'
  );
  const [selectedCategory, setSelectedCategory] = useState(searchParams.get('category') || '');
  const [selectedMaintainer, setSelectedMaintainer] = useState(searchParams.get('maintainer') || '');
  const [installedFile, setInstalledFile] = useState(searchParams.get('file') || '');
  const [showActiveOnly, setShowActiveOnly] = useState(
    searchParams.get('active') !== 'false' // default to true unless explicitly set to false
  );
  const [currentPage, setCurrentPage] = useState(
    parseInt(searchParams.get('page') || '1')
  );

  // Filter dropdown states
  const [showCategoryDropdown, setShowCategoryDropdown] = useState(false);
  const [showMaintainerDropdown, setShowMaintainerDropdown] = useState(false);
  const [categorySearch, setCategorySearch] = useState('');
  const [maintainerSearch, setMaintainerSearch] = useState('');
  const [filteredCategories, setFilteredCategories] = useState<Category[]>([]);
  const [filteredMaintainers, setFilteredMaintainers] = useState<Maintainer[]>([]);

  // Data State
  const [ports, setPorts] = useState<Port[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [maintainers, setMaintainers] = useState<Maintainer[]>([]);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);

  const limit = 24;
  const totalPages = Math.ceil(totalCount / limit);

  // Update URL function
  const updateURL = useCallback(() => {
    const params = new URLSearchParams();
    if (query) params.set('q', query);
    if (displayMode !== 'grid') params.set('display', displayMode);
    if (sortBy !== 'name') params.set('sort', sortBy);
    if (sortOrder !== 'asc') params.set('order', sortOrder);
    if (selectedCategory) params.set('category', selectedCategory);
    if (selectedMaintainer) params.set('maintainer', selectedMaintainer);
    if (installedFile) params.set('file', installedFile);
    if (!showActiveOnly) params.set('active', 'false'); // only add to URL if false
    if (currentPage !== 1) params.set('page', currentPage.toString());

    const newUrl = `${window.location.pathname}${params.toString() ? '?' + params.toString() : ''}`;
    window.history.replaceState({}, '', newUrl);
  }, [query, displayMode, sortBy, sortOrder, selectedCategory, selectedMaintainer, installedFile, showActiveOnly, currentPage]);

  // Fetch data based on current state
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {


        // All ports view or search
        if (query && query.trim()) {
          // Use search API for text queries
          const response = await api.search({
            name: query.trim(),
            limit,
            page: currentPage
          });
          
          // Sort search results to prioritize exact name matches
          const sortedResults = response.results.sort((a, b) => {
            const queryLower = query.trim().toLowerCase();
            const aNameLower = a.name.toLowerCase();
            const bNameLower = b.name.toLowerCase();
            
            // Exact match gets highest priority
            const aExact = aNameLower === queryLower;
            const bExact = bNameLower === queryLower;
            if (aExact && !bExact) return -1;
            if (!aExact && bExact) return 1;
            
            // Prefix match gets second priority
            const aPrefix = aNameLower.startsWith(queryLower);
            const bPrefix = bNameLower.startsWith(queryLower);
            if (aPrefix && !bPrefix) return -1;
            if (!aPrefix && bPrefix) return 1;
            
            // Finally by alphabetical order
            return aNameLower.localeCompare(bNameLower);
          });
          
          setSearchResults(sortedResults);
          setTotalCount(response.count || 0);
        } else {
          // All ports view - use ports API for everything
          const hasFileSearch = installedFile && installedFile.trim();
          
          if (hasFileSearch) {
            // Use search API for file search
            const response = await api.search({
              files: installedFile.trim(),
              limit,
              page: currentPage
            });
            setSearchResults(response.results);
            setTotalCount(response.count || 0);
          } else {
            if (query && query.trim()) {
              // Use search API for text queries - search primarily by name
              const response = await api.search({
                name: query.trim(),
                limit,
                page: currentPage
              });

              
              // Sort search results to prioritize exact name matches
              const sortedResults = response.results.sort((a, b) => {
                const queryLower = query.trim().toLowerCase();
                const aNameLower = a.name.toLowerCase();
                const bNameLower = b.name.toLowerCase();
                
                // Exact match gets highest priority
                const aExact = aNameLower === queryLower;
                const bExact = bNameLower === queryLower;
                if (aExact && !bExact) return -1;
                if (!aExact && bExact) return 1;
                
                // Prefix match gets second priority
                const aPrefix = aNameLower.startsWith(queryLower);
                const bPrefix = bNameLower.startsWith(queryLower);
                if (aPrefix && !bPrefix) return -1;
                if (!aPrefix && bPrefix) return 1;
                
                // Finally by alphabetical order
                return aNameLower.localeCompare(bNameLower);
              });
              
              setSearchResults(sortedResults);
              setTotalCount(response.count || 0);
            } else {
              // Use ports API for browsing with filters (no text search)
              const params: any = { limit, page: currentPage };
              
              // Add filters - these need to use the correct Django field names
              if (selectedCategory) {
                params.categories = selectedCategory;
              }
              if (selectedMaintainer) {
                params['maintainers__github'] = selectedMaintainer;
              }
              
              // Add active filter
              if (showActiveOnly) {
                params.active = 'true';
              }
              
              // Convert sort options to API format
              if (sortBy === 'name') {
                params.ordering = sortOrder === 'desc' ? '-name' : 'name';
              } else if (sortBy === 'updated') {
                params.ordering = sortOrder === 'desc' ? '-version_updated_at' : 'version_updated_at';
              }

              const response = await api.getPorts(params);
              
              setPorts(response.results);
              setTotalCount(response.count || 0);
            }
          }
        }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load data");
    } finally {
      setLoading(false);
    }
  }, [query, selectedCategory, selectedMaintainer, installedFile, showActiveOnly, currentPage, limit, sortBy, sortOrder]);

  // Effects
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    updateURL();
  }, [updateURL]);

  // Debounced search for autocomplete
  const searchCategories = useCallback(async (searchTerm: string) => {
    if (searchTerm.length > 0) {
      try {
        const results = await api.autocompleteCategories(searchTerm);
        setFilteredCategories(results);
      } catch (error) {
        console.error('Category search failed:', error);
        setFilteredCategories([]);
      }
    } else {
      // Load all categories when no search term
      try {
        const response = await api.getCategories();
        setFilteredCategories(response.results || []);
      } catch (error) {
        console.error('Failed to load categories:', error);
        setFilteredCategories([]);
      }
    }
  }, []);

  const searchMaintainers = useCallback(async (searchTerm: string) => {
    if (searchTerm.length > 0) {
      try {
        const results = await api.autocompleteMaintainers(searchTerm);
        setFilteredMaintainers(results);
      } catch (error) {
        console.error('Maintainer search failed:', error);
        setFilteredMaintainers([]);
      }
    } else {
      // Load first 10 maintainers when no search term
      try {
        const response = await api.getMaintainers();
        // Limit to first 10 maintainers
        setFilteredMaintainers((response.results || []).slice(0, 10));
      } catch (error) {
        console.error('Failed to load maintainers:', error);
        setFilteredMaintainers([]);
      }
    }
  }, []);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element;
      if (!target.closest('.relative')) {
        setShowCategoryDropdown(false);
        setShowMaintainerDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Initialize filtered lists when dropdown opens
  useEffect(() => {
    if (showCategoryDropdown) {
      searchCategories(categorySearch);
    }
  }, [showCategoryDropdown, searchCategories, categorySearch]);

  useEffect(() => {
    if (showMaintainerDropdown) {
      searchMaintainers(maintainerSearch);
    }
  }, [showMaintainerDropdown, searchMaintainers, maintainerSearch]);

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      if (showCategoryDropdown) {
        searchCategories(categorySearch);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [categorySearch, showCategoryDropdown, searchCategories]);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (showMaintainerDropdown) {
        searchMaintainers(maintainerSearch);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [maintainerSearch, showMaintainerDropdown, searchMaintainers]);

  // Debounce main search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setQuery(searchInput);
      setCurrentPage(1);
    }, 500); // 500ms delay for search
    return () => clearTimeout(timer);
  }, [searchInput]);

  // Save display mode preference to localStorage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('macports-display-mode', displayMode);
    }
  }, [displayMode]);


  // Handlers
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchData();
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const clearFilters = () => {
    setSelectedCategory('');
    setSelectedMaintainer('');
    setInstalledFile('');
    setQuery('');
    setSearchInput('');
    setCurrentPage(1);
  };

  const clearFilter = (filterType: 'category' | 'maintainer' | 'file' | 'query') => {
    switch (filterType) {
      case 'category':
        setSelectedCategory('');
        break;
      case 'maintainer':
        setSelectedMaintainer('');
        break;
      case 'file':
        setInstalledFile('');
        break;
      case 'query':
        setQuery('');
        setSearchInput('');
        break;
    }
    setCurrentPage(1);
  };

  const hasActiveFilters = selectedCategory || selectedMaintainer || installedFile || query;

  // Component renderers
  const PortCard = ({ port }: { port: Port | SearchResult }) => {
    const isSearchResult = 'score' in port;
    const isExactMatch = query && port.name.toLowerCase() === query.toLowerCase();
    const isPrefixMatch = query && port.name.toLowerCase().startsWith(query.toLowerCase()) && !isExactMatch;
    
    if (displayMode === 'list') {
      return (
        <a
          href={`/port/${encodeURIComponent(port.name)}`}
          className="block group bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-lg hover:bg-gray-50 dark:hover:bg-white/10 hover:border-gray-300 dark:hover:border-white/20 transition-all duration-200 p-4"
        >
          <div className="flex items-center justify-between gap-4">
            {/* Left: Name and match indicators */}
            <div className="flex items-center gap-3 min-w-0 flex-1">
              <Package className="h-5 w-5 text-brand-300 shrink-0" />
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-semibold text-lg truncate">{port.name}</h3>
                  {isSearchResult && isExactMatch && (
                    <span className="px-2 py-1 bg-green-500/20 text-green-700 dark:text-green-300 text-xs rounded-full font-medium shrink-0">
                      EXACT
                    </span>
                  )}
                  {isSearchResult && isPrefixMatch && (
                    <span className="px-2 py-1 bg-blue-500/20 text-blue-700 dark:text-blue-300 text-xs rounded-full shrink-0">
                      PREFIX
                    </span>
                  )}
                  {isSearchResult && port.score !== undefined && !isExactMatch && !isPrefixMatch && (
                    <span className="px-2 py-1 bg-brand-500/20 text-brand-600 dark:text-brand-300 text-xs rounded-full shrink-0">
                      {Math.round(port.score * 100)}%
                    </span>
                  )}
                </div>
                {port.description && (
                  <p className="text-sm text-gray-600 dark:text-white/70 line-clamp-1">
                    {port.description}
                  </p>
                )}
              </div>
            </div>
            
            {/* Center: Categories and maintainers */}
            <div className="flex items-center gap-3 shrink-0">
              <div className="flex flex-wrap gap-1 max-w-xs">
                {port.categories?.slice(0, 2).map((category) => (
                  <span key={category} className="tag-info text-xs">
                    <Tag className="h-3 w-3" />
                    {category}
                  </span>
                ))}
                {port.categories && port.categories.length > 2 && (
                  <span className="text-xs text-gray-500 dark:text-white/50">
                    +{port.categories.length - 2}
                  </span>
                )}
              </div>
              {isSearchResult && port.maintainers && port.maintainers.length > 0 && (
                <div className="flex flex-wrap gap-1 max-w-xs">
                  {port.maintainers.slice(0, 1).map((maintainer) => (
                    <span key={maintainer} className="tag-muted text-xs">
                      <User className="h-3 w-3" />
                      {maintainer}
                    </span>
                  ))}
                  {port.maintainers.length > 1 && (
                    <span className="text-xs text-gray-500 dark:text-white/50">
                      +{port.maintainers.length - 1}
                    </span>
                  )}
                </div>
              )}
            </div>
            
            {/* Right: View arrow */}
            <div className="shrink-0 text-xs text-gray-400 dark:text-white/50 group-hover:text-gray-600 dark:group-hover:text-white/70 transition-colors">
              View →
            </div>
          </div>
        </a>
      );
    }
    
    // Grid view (original layout)
    return (
      <a
        href={`/port/${encodeURIComponent(port.name)}`}
        className="card group dark:hover:bg-white/10 hover:bg-gray-50 transition-all duration-200 hover:scale-[1.02]"
      >
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 mb-2">
              <Package className="h-5 w-5 text-brand-300" />
              <h3 className="font-semibold text-lg">{port.name}</h3>
              {isSearchResult && isExactMatch && (
                <span className="px-2 py-1 bg-green-500/20 text-green-700 dark:text-green-300 text-xs rounded-full font-medium">
                  EXACT MATCH
                </span>
              )}
              {isSearchResult && isPrefixMatch && (
                <span className="px-2 py-1 bg-blue-500/20 text-blue-700 dark:text-blue-300 text-xs rounded-full">
                  PREFIX
                </span>
              )}
              {isSearchResult && port.score !== undefined && !isExactMatch && !isPrefixMatch && (
                <span className="px-2 py-1 bg-brand-500/20 text-brand-600 dark:text-brand-300 text-xs rounded-full">
                  {Math.round(port.score * 100)}% match
                </span>
              )}
            </div>
            
            {port.description && (
              <p className="text-sm text-gray-600 dark:text-white/70 mb-3 line-clamp-2">
                {port.description}
              </p>
            )}
            
            <div className="flex flex-wrap gap-2 text-xs">
              {port.categories?.slice(0, 3).map((category) => (
                <span
                  key={category}
                  className="tag-info"
                >
                  <Tag className="h-3 w-3" />
                  {category}
                </span>
              ))}
              {isSearchResult && port.maintainers?.slice(0, 2).map((maintainer) => (
                <span
                  key={maintainer}
                  className="tag-muted"
                >
                  <User className="h-3 w-3" />
                  {maintainer}
                </span>
              ))}
            </div>
          </div>
          
          <div className="shrink-0 text-xs text-gray-400 dark:text-white/50 group-hover:text-gray-600 dark:group-hover:text-white/70 transition-colors">
            View →
          </div>
        </div>
      </a>
    );
  };

  const CategoryCard = ({ category }: { category: Category }) => (
    <div className="card group dark:hover:bg-white/10 hover:bg-gray-50 transition-all duration-200">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 mb-2">
            <Tag className="h-5 w-5 text-brand-300" />
            <h3 className="font-semibold text-lg">{category.name}</h3>
          </div>
          
          {category.description && (
            <p className="text-sm text-gray-600 dark:text-white/70 mb-3 line-clamp-2">
              {category.description}
            </p>
          )}
          
          <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-white/60">
            <Package className="h-4 w-4" />
            <span>
              {category.ports_count 
                ? `${category.ports_count.toLocaleString()} port${category.ports_count !== 1 ? 's' : ''}` 
                : 'Ports available'
              }
            </span>
          </div>
        </div>
        
        <div className="flex gap-2">
          <button
            onClick={() => {
              setSelectedCategory(category.name);
              setCurrentPage(1);
            }}
            className="px-3 py-1 bg-brand-500 hover:bg-brand-600 text-white text-xs rounded-full transition-colors"
          >
            Browse Ports
          </button>
        </div>
      </div>
    </div>
  );

  const MaintainerCard = ({ maintainer }: { maintainer: Maintainer }) => (
    <div className="card group dark:hover:bg-white/10 hover:bg-gray-50 transition-all duration-200">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 mb-2">
            <User className="h-5 w-5 text-brand-300" />
            <h3 className="font-semibold text-lg truncate">
              {maintainer.name || maintainer.github || maintainer.email || 'Unknown'}
            </h3>
          </div>
          
          <div className="space-y-2 text-sm">
            {maintainer.github && (
              <a
                href={`https://github.com/${maintainer.github}`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-brand-600 dark:text-brand-300 hover:text-brand-700 dark:hover:text-brand-200 transition-colors"
                onClick={(e) => e.stopPropagation()}
              >
                <Github className="h-4 w-4" />
                @{maintainer.github}
              </a>
            )}
            
            {maintainer.email && (
              <div className="flex items-center gap-2 text-gray-600 dark:text-white/70">
                <Mail className="h-4 w-4" />
                <span className="truncate">{maintainer.email}</span>
              </div>
            )}
          </div>
          
          <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-white/60 mt-3">
            <Package className="h-4 w-4" />
            <span>
              {maintainer.ports_count 
                ? `${maintainer.ports_count.toLocaleString()} port${maintainer.ports_count !== 1 ? 's' : ''}` 
                : 'Maintainer'
              }
            </span>
          </div>
        </div>
        
        {maintainer.github && (
          <button
            onClick={() => {
              setSelectedMaintainer(maintainer.github!);
              setCurrentPage(1);
            }}
            className="px-3 py-1 bg-brand-500 hover:bg-brand-600 text-white text-xs rounded-full transition-colors"
          >
            View Ports
          </button>
        )}
      </div>
    </div>
  );

  // Get current data to display
  const getCurrentData = () => {
    // If we have a text query or file search, show search results
    if ((query && query.trim()) || (installedFile && installedFile.trim())) {
      return searchResults;
    }
    
    // Otherwise show ports (which may be filtered by category/maintainer)
    return ports;
  };

  const currentData = getCurrentData();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-4">
        <h1 className="text-3xl font-bold">All Ports</h1>
        <p className="text-gray-600 dark:text-white/70">
          Discover, search, and explore the complete MacPorts ecosystem
        </p>
      </div>

      {/* Search & Filters */}
      <div className="card relative z-10 overflow-visible">
        <div className="space-y-4 overflow-visible">
          {/* Main Search Bar - Ports Only */}
          <form onSubmit={handleSearch} className="flex gap-2">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400 dark:text-white/40" />
              <input
                type="text"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                placeholder="Search port names and descriptions..."
                className="w-full pl-11 pr-4 py-3 bg-white dark:bg-white/10 border border-gray-300 dark:border-white/20 rounded-lg text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-white/40 focus:outline-none focus:border-brand-400 text-lg"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="btn-primary px-6 disabled:opacity-50"
            >
              {loading ? (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  Searching...
                </div>
              ) : (
                'Search'
              )}
            </button>
          </form>

          {/* Filters Row */}
          <div className="flex flex-wrap gap-3 relative z-50">
              {/* Category Filter */}
              <div className="relative z-[100]">
                <button
                  type="button"
                  onClick={() => {
                    setShowCategoryDropdown(!showCategoryDropdown);
                    setShowMaintainerDropdown(false);
                  }}
                  className={`flex items-center gap-2 px-3 py-2 border rounded-lg text-sm transition-colors ${
                    selectedCategory
                      ? 'bg-brand-50 dark:bg-brand-900/20 border-brand-300 dark:border-brand-600 text-brand-700 dark:text-brand-300'
                      : 'bg-white dark:bg-white/10 border-gray-300 dark:border-white/20 hover:bg-gray-50 dark:hover:bg-white/5'
                  }`}
                >
                  <Tag className="h-4 w-4" />
                  <span>{selectedCategory || 'Category'}</span>
                  <ChevronDown className="h-4 w-4" />
                </button>
                {showCategoryDropdown && (
                  <div className="absolute top-full left-0 mt-1 w-64 bg-white dark:bg-gray-800 border border-gray-300 dark:border-white/20 rounded-lg shadow-xl z-[9999] max-h-60 overflow-y-auto">
                    <div className="p-2">
                      <input
                        type="text"
                        placeholder="Search categories..."
                        value={categorySearch}
                        onChange={(e) => setCategorySearch(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-white/20 rounded text-sm bg-white dark:bg-white/10 text-gray-900 dark:text-white"
                        autoFocus
                      />
                    </div>
                    <div className="max-h-40 overflow-y-auto">
                      {filteredCategories.length > 0 ? (
                        filteredCategories.map((category) => (
                          <button
                            key={category.name}
                            type="button"
                            onClick={() => {
                              setSelectedCategory(category.name);
                              setShowCategoryDropdown(false);
                              setCategorySearch('');
                              setCurrentPage(1);
                            }}
                            className="w-full text-left px-3 py-2 hover:bg-gray-100 dark:hover:bg-white/10 text-sm flex items-center justify-between"
                          >
                            <span>{category.name}</span>
                            <span className="text-gray-500 text-xs">
                              {category.ports_count?.toLocaleString() || 0}
                            </span>
                          </button>
                        ))
                      ) : (
                        <div className="px-3 py-2 text-sm text-gray-500 dark:text-white/60 text-center">
                          {categorySearch ? 'No categories found' : 'Type to search categories...'}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Maintainer Filter */}
              <div className="relative z-[100]">
                <button
                  type="button"
                  onClick={() => {
                    setShowMaintainerDropdown(!showMaintainerDropdown);
                    setShowCategoryDropdown(false);
                  }}
                  className={`flex items-center gap-2 px-3 py-2 border rounded-lg text-sm transition-colors ${
                    selectedMaintainer
                      ? 'bg-brand-50 dark:bg-brand-900/20 border-brand-300 dark:border-brand-600 text-brand-700 dark:text-brand-300'
                      : 'bg-white dark:bg-white/10 border-gray-300 dark:border-white/20 hover:bg-gray-50 dark:hover:bg-white/5'
                  }`}
                >
                  <User className="h-4 w-4" />
                  <span>{selectedMaintainer || 'Maintainer'}</span>
                  <ChevronDown className="h-4 w-4" />
                </button>
                {showMaintainerDropdown && (
                  <div className="absolute top-full left-0 mt-1 w-64 bg-white dark:bg-gray-800 border border-gray-300 dark:border-white/20 rounded-lg shadow-xl z-[9999] max-h-60 overflow-y-auto">
                    <div className="p-2">
                      <input
                        type="text"
                        placeholder="Search maintainers..."
                        value={maintainerSearch}
                        onChange={(e) => setMaintainerSearch(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-white/20 rounded text-sm bg-white dark:bg-white/10 text-gray-900 dark:text-white"
                        autoFocus
                      />
                    </div>
                    <div className="max-h-40 overflow-y-auto">
                      {filteredMaintainers.length > 0 ? (
                        filteredMaintainers.map((maintainer, index) => {
                          const displayName = maintainer.name || maintainer.github || maintainer.email || 'Unknown';
                          const key = maintainer.github || maintainer.email || index;
                          return (
                            <button
                              key={key}
                              type="button"
                              onClick={() => {
                                setSelectedMaintainer(maintainer.github || '');
                                setShowMaintainerDropdown(false);
                                setMaintainerSearch('');
                                setCurrentPage(1);
                              }}
                              className="w-full text-left px-3 py-2 hover:bg-gray-100 dark:hover:bg-white/10 text-sm flex items-center justify-between"
                            >
                              <span>{displayName}</span>
                              {maintainer.ports_count && maintainer.ports_count > 0 && (
                                <span className="text-gray-500 text-xs">
                                  {maintainer.ports_count.toLocaleString()}
                                </span>
                              )}
                            </button>
                          );
                        })
                      ) : (
                        <div className="px-3 py-2 text-sm text-gray-500 dark:text-white/60 text-center">
                          {maintainerSearch ? 'No maintainers found' : 'Type to search maintainers...'}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Files Filter */}
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-gray-500" />
                <input
                  type="text"
                  value={installedFile}
                  onChange={(e) => setInstalledFile(e.target.value)}
                  placeholder="Search installed files..."
                  className="px-3 py-2 border border-gray-300 dark:border-white/20 rounded-lg text-sm bg-white dark:bg-white/10 w-48"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      setCurrentPage(1);
                      fetchData();
                    }
                  }}
                />
              </div>

              {/* Active Ports Only Toggle */}
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showActiveOnly}
                  onChange={(e) => {
                    setShowActiveOnly(e.target.checked);
                    setCurrentPage(1);
                  }}
                  className="w-4 h-4 text-brand-500 bg-white dark:bg-white/10 border-gray-300 dark:border-white/20 rounded focus:ring-brand-400 focus:ring-2"
                />
                <span className="text-sm text-gray-700 dark:text-white/80 font-medium">
                  Active ports only
                </span>
              </label>
            </div>



          {/* Controls Row */}
          <div className="flex flex-wrap items-center justify-between gap-4">
            {/* Display & Sort Controls */}
            <div className="flex items-center gap-4">
              {/* Display Mode */}
              <div className="flex gap-1 border border-gray-300 dark:border-white/20 rounded-lg p-1">
                <button
                  type="button"
                  onClick={() => setDisplayMode('grid')}
                  className={`p-1.5 rounded transition-colors ${
                    displayMode === 'grid'
                      ? 'bg-brand-500 text-white'
                      : 'text-gray-600 dark:text-white/60 hover:text-gray-900 dark:hover:text-white'
                  }`}
                >
                  <Grid3X3 className="h-4 w-4" />
                </button>
                <button
                  type="button"
                  onClick={() => setDisplayMode('list')}
                  className={`p-1.5 rounded transition-colors ${
                    displayMode === 'list'
                      ? 'bg-brand-500 text-white'
                      : 'text-gray-600 dark:text-white/60 hover:text-gray-900 dark:hover:text-white'
                  }`}
                >
                  <List className="h-4 w-4" />
                </button>
              </div>

              {/* Sort Controls */}
              <div className="flex items-center gap-2">
                <span className="px-3 py-1.5 bg-white dark:bg-white/10 border border-gray-300 dark:border-white/20 rounded text-sm text-gray-700 dark:text-white/80">
                  Sort by Name
                </span>
                <button
                  type="button"
                  onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                  className="p-1.5 border border-gray-300 dark:border-white/20 rounded hover:bg-gray-100 dark:hover:bg-white/10"
                >
                  {sortOrder === 'asc' ? <SortAsc className="h-4 w-4" /> : <SortDesc className="h-4 w-4" />}
                </button>
              </div>
            </div>

            {/* Active Filters & Clear */}
            {hasActiveFilters && (
              <div className="flex items-center gap-2">
                <div className="flex flex-wrap gap-2 text-sm">
                  {query && (
                    <span className="tag-info">
                      Search: {query}
                      <button
                        type="button"
                        onClick={() => clearFilter('query')}
                        className="ml-1 hover:text-red-600"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  )}
                  {selectedCategory && (
                    <span className="tag-info">
                      Category: {selectedCategory}
                      <button
                        type="button"
                        onClick={() => clearFilter('category')}
                        className="ml-1 hover:text-red-600"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  )}
                  {selectedMaintainer && (
                    <span className="tag-info">
                      Maintainer: {selectedMaintainer}
                      <button
                        type="button"
                        onClick={() => clearFilter('maintainer')}
                        className="ml-1 hover:text-red-600"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  )}
                  {installedFile && (
                    <span className="tag-info">
                      File: {installedFile}
                      <button
                        type="button"
                        onClick={() => clearFilter('file')}
                        className="ml-1 hover:text-red-600"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  )}
                </div>
                <button
                  type="button"
                  onClick={clearFilters}
                  className="px-3 py-1 text-sm text-red-600 hover:text-red-700 border border-red-200 hover:border-red-300 rounded"
                >
                  Clear All
                </button>
              </div>
            )}
          </div>
        </div>
      </div>


      {/* Results */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-brand-400"></div>
          <p className="mt-2 text-gray-500 dark:text-white/60">Loading...</p>
        </div>
      ) : error ? (
        <div className="card text-center py-12">
          <p className="text-red-500 dark:text-red-400">Error: {error}</p>
          <button
            onClick={fetchData}
            className="mt-4 btn-primary"
          >
            Try Again
          </button>
        </div>
      ) : currentData.length === 0 ? (
        <div className="card text-center py-12">
          <Package className="h-12 w-12 text-gray-400 dark:text-white/40 mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">No results found</h2>
          <p className="text-gray-600 dark:text-white/60 mb-4">
            {query 
              ? `No ports found matching "${query}"`
              : `No ports found with current filters`
            }
          </p>
          {hasActiveFilters && (
            <button onClick={clearFilters} className="btn-primary">
              Clear Filters
            </button>
          )}
        </div>
      ) : (
        <>
          {/* Results Header */}
          <div className="flex items-center justify-between">
            <div>
              <p className="text-lg font-semibold">
                {totalCount.toLocaleString()} port{totalCount !== 1 ? 's' : ''}
                {query && ` for "${query}"`}
              </p>
              <p className="text-sm text-gray-500 dark:text-white/60">
                Showing {((currentPage - 1) * limit) + 1}-{Math.min(currentPage * limit, totalCount)} of {totalCount.toLocaleString()}
              </p>
            </div>
          </div>

          {/* Results Grid */}
          <div className={`${
            displayMode === 'grid' 
              ? 'grid gap-4 sm:grid-cols-2 lg:grid-cols-3'
              : 'space-y-3'
          }`}>
            {currentData.map((item, index) => (
              <PortCard key={(item as Port).name} port={item as Port | SearchResult} />
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2">
              <button
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className="p-2 rounded border border-gray-300 dark:border-white/20 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-white/10"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              
              <div className="flex items-center gap-1">
                {Array.from({ length: Math.min(7, totalPages) }, (_, i) => {
                  let pageNum;
                  if (totalPages <= 7) {
                    pageNum = i + 1;
                  } else if (currentPage <= 4) {
                    pageNum = i + 1;
                  } else if (currentPage >= totalPages - 3) {
                    pageNum = totalPages - 6 + i;
                  } else {
                    pageNum = currentPage - 3 + i;
                  }
                  
                  if (pageNum < 1 || pageNum > totalPages) return null;
                  
                  return (
                    <button
                      key={pageNum}
                      onClick={() => handlePageChange(pageNum)}
                      className={`px-3 py-1 rounded text-sm transition-colors ${
                        pageNum === currentPage
                          ? 'bg-brand-500 text-white'
                          : 'border border-gray-300 dark:border-white/20 hover:bg-gray-100 dark:hover:bg-white/10'
                      }`}
                    >
                      {pageNum}
                    </button>
                  );
                })}
              </div>

              <button
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className="p-2 rounded border border-gray-300 dark:border-white/20 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-white/10"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
