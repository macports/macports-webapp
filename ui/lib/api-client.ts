import { API_BASE, apiUrl } from './api';
import type { 
  Port, 
  PortDetail, 
  Category, 
  Maintainer, 
  Build, 
  Stats, 
  APIResponse, 
  SearchResult, 
  AutocompleteResult,
  PortInstallation,
  EnhancedStats,
  PopularPort
} from './types';

export class MacPortsAPI {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl.replace(/\/+$/, '');
  }

  private async fetch<T>(path: string, params?: Record<string, string | string[]>): Promise<T> {
    const url = new URL(`${this.baseUrl}${path}`);
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (Array.isArray(value)) {
          // For arrays, add multiple query params with the same name (OR logic)
          value.forEach(v => {
            if (v) url.searchParams.append(key, v);
          });
        } else if (value) {
          url.searchParams.append(key, value);
        }
      });
    }

    const response = await fetch(url.toString());
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
    
    return response.json();
  }

  // Ports
  async getPorts(params?: {
    search?: string;

    categories?: string;
    'maintainers__github'?: string;
    limit?: number;
    page?: number;
    ordering?: string;
  }): Promise<APIResponse<Port>> {
    const searchParams: Record<string, string> = {};
    
    if (params?.search) searchParams.search = params.search;
    if (params?.categories) searchParams.categories = params.categories;
    if (params?.['maintainers__github']) searchParams['maintainers__github'] = params['maintainers__github'];
    if (params?.limit) searchParams.limit = params.limit.toString();
    if (params?.page) searchParams.page = params.page.toString();
    if (params?.ordering) searchParams.ordering = params.ordering;

    return this.fetch<APIResponse<Port>>('/ports/', searchParams);
  }

  async getPort(name: string): Promise<PortDetail> {
    return this.fetch<PortDetail>(`/ports/${encodeURIComponent(name)}/`);
  }

  // Categories
  async getCategories(): Promise<APIResponse<Category>> {
    return this.fetch<APIResponse<Category>>('/category/');
  }

  async getCategory(name: string): Promise<Category> {
    return this.fetch<Category>(`/category/${encodeURIComponent(name)}/`);
  }

  // Maintainers
  async getMaintainers(): Promise<APIResponse<Maintainer>> {
    return this.fetch<APIResponse<Maintainer>>('/maintainer/');
  }

  async getMaintainer(github: string): Promise<Maintainer> {
    return this.fetch<Maintainer>(`/maintainer/${encodeURIComponent(github)}/`);
  }

  // Build History
  async getBuilds(params?: {
    port_name?: string;
    builder_name?: string | string[];
    status?: string | string[];
    page?: number;
    page_size?: number;
  }): Promise<APIResponse<Build>> {
    const searchParams: Record<string, string | string[]> = {};
    
    if (params?.port_name) searchParams.port_name = params.port_name;
    
    if (params?.builder_name) {
      // Pass arrays directly for OR logic, single values as strings
      searchParams['builder_name__name'] = params.builder_name;
    }
    
    if (params?.status) {
      // Pass arrays directly for OR logic, single values as strings
      searchParams.status = params.status;
    }
    
    if (params?.page) searchParams.page = params.page.toString();
    if (params?.page_size) searchParams.page_size = params.page_size.toString();
    
    // Ensure proper ordering by time_start (newest first)
    searchParams.ordering = '-time_start';

    return this.fetch<APIResponse<Build>>('/builds/', searchParams);
  }

  async getBuild(id: number): Promise<Build> {
    return this.fetch<Build>(`/builds/${id}/`);
  }

  // Autocomplete APIs
  async autocompleteCategories(query: string): Promise<Category[]> {
    const response = await this.fetch<APIResponse<Category>>('/autocomplete/category/', { q: query });
    return response.results || [];
  }

  async autocompleteMaintainers(query: string): Promise<Maintainer[]> {
    const response = await this.fetch<APIResponse<Maintainer>>('/autocomplete/maintainer/', { q: query });
    return response.results || [];
  }

  async autocompletePorts(query: string): Promise<AutocompleteResult[]> {
    const response = await this.fetch<any>('/autocomplete/port/', { q: query, name: 'on' });
    
    // Handle different response formats
    if (Array.isArray(response)) {
      return response.map(item => 
        typeof item === 'string' 
          ? { name: item }
          : { name: item.name || item.port || item.portname, description: item.description }
      );
    }
    
    return response.results || response.ports || [];
  }

  async autocompleteCategory(query: string): Promise<AutocompleteResult[]> {
    const response = await this.fetch<any>('/autocomplete/category/', { q: query });
    return Array.isArray(response) ? response : response.results || [];
  }

  async autocompleteMaintainer(query: string): Promise<AutocompleteResult[]> {
    const response = await this.fetch<any>('/autocomplete/maintainer/', { q: query });
    return Array.isArray(response) ? response : response.results || [];
  }

  async autocompleteVariant(query: string): Promise<AutocompleteResult[]> {
    const response = await this.fetch<any>('/autocomplete/variant/', { q: query });
    return Array.isArray(response) ? response : response.results || [];
  }

  // Stats
  async getStats(): Promise<Stats> {
    return this.fetch<Stats>('/stats/');
  }

  // Port-specific stats
  async getPortStats(name: string, params?: {
    days?: number;
    days_ago?: number;
    property?: string[];
    sort_by?: string;
  }): Promise<any> {
    const searchParams: Record<string, string | string[]> = { name };
    
    if (params?.days) searchParams.days = params.days.toString();
    if (params?.days_ago) searchParams.days_ago = params.days_ago.toString();
    if (params?.sort_by) searchParams.sort_by = params.sort_by;
    if (params?.property) searchParams.property = params.property;

    return this.fetch<any>('/statistics/port', searchParams);
  }

  // Get port installation count
  async getPortInstallCount(name: string, days: number = 30): Promise<{requested: number, all: number}> {
    const response = await this.getPortStats(name, { days });
    return response.result?.[0] || { requested: 0, all: 0 };
  }

  // Get port monthly statistics
  async getPortMonthlyStats(name: string, includeVersions: boolean = false): Promise<any> {
    const searchParams: Record<string, string> = { name };
    if (includeVersions) searchParams.include_versions = 'yes';
    
    return this.fetch<any>('/statistics/port/monthly', searchParams);
  }


  // Get port health information
  async getPortHealth(name: string): Promise<any> {
    // Fetch HTML from Django view (not API endpoint)
    const baseUrl = this.baseUrl.replace('/api/v1', '');
    const response = await fetch(`${baseUrl}/port/${name}/health/?port_name=${name}`);
    return response.text();
  }

  // Get port trac tickets
  async getPortTickets(name: string): Promise<any> {
    // Fetch HTML from Django view (not API endpoint)
    const baseUrl = this.baseUrl.replace('/api/v1', '');
    const response = await fetch(`${baseUrl}/port/${name}/tickets/?port_name=${name}`);
    return response.text();
  }

  async getBuildFiles(buildId: string): Promise<any> {
    return this.fetch<any>(`/files/${buildId}/`);
  }

  // Search API using Haystack
  async search(params: {
    name?: string;
    description?: string;
    categories?: string;
    maintainers?: string;
    files?: string;
    limit?: number;
    page?: number;
  }): Promise<APIResponse<SearchResult>> {
    const searchParams: Record<string, string> = {};
    
    if (params.name) searchParams.name = params.name;
    if (params.description) searchParams.description = params.description;
    if (params.categories) searchParams.categories = params.categories;
    if (params.maintainers) searchParams.maintainers = params.maintainers;
    if (params.files) searchParams.files = params.files;
    if (params.limit) searchParams.limit = params.limit.toString();
    if (params.page) searchParams.page = params.page.toString();

    return this.fetch<APIResponse<SearchResult>>('/search/', searchParams);
  }

  // Stats API methods
  async getEnhancedStats(): Promise<EnhancedStats> {
    return this.fetch<EnhancedStats>('/statistics/enhanced');
  }

  async getGeneralStats(params?: {
    days?: number;
    days_ago?: number;
    property?: string[];
    sort_by?: string;
  }): Promise<any> {
    // Build URL manually to support multiple 'property' parameters
    const urlParams = new URLSearchParams();
    if (params?.days) urlParams.append('days', params.days.toString());
    if (params?.days_ago) urlParams.append('days_ago', params.days_ago.toString());
    if (params?.sort_by) urlParams.append('sort_by', params.sort_by);
    if (params?.property) {
      params.property.forEach(prop => {
        urlParams.append('property', prop);
      });
    }
    
    const url = apiUrl(`/statistics/?${urlParams.toString()}`);
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`);
    }
    return response.json();
  }

  async getPopularPorts(params?: {
    days?: number;
    limit?: number;
  }): Promise<PopularPort[]> {
    const searchParams: Record<string, string> = {};
    if (params?.days) searchParams.days = params.days.toString();
    if (params?.limit) searchParams.limit = params.limit.toString();
    
    return this.fetch<PopularPort[]>('/statistics/popular', searchParams);
  }
}

// Default API client instance
export const api = new MacPortsAPI();
