// Common types for MacPorts API responses

export interface Port {
  name: string;
  version?: string | null;
  description?: string | null;
  long_description?: string | null;
  homepage?: string | null;
  categories?: string[] | null;
  maintainers?: Maintainer[] | null;
  variants?: (string | Variant)[] | null;  // Can be either strings or objects
  dependencies?: DependencyGroup[] | null;
  conflicts?: string[] | null;
  replaced_by?: string | null;
  license?: string | null;
  platforms?: string[] | null;
  version_updated_at?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
  active?: boolean;
  livecheck?: LivecheckInfo;
  buildbot?: BuildbotInfo;
}

export interface PortDetail extends Port {
  closedmaintainer?: boolean;
  notes?: string | null;
  submitter?: string | null;
  openmaintainer?: boolean;
  epochdate?: string | null;
  portdir?: string | null;
  active_version?: string | null;
  replaced_by?: string | null;
  depends_on?: DependencyGroup[];
  stats?: {
    requested?: number;
    total_count?: number;
  };
}

export interface DependencyGroup {
  type: string;
  ports: string[];
}

export interface Category {
  name: string;
  description?: string | null;
  ports_count?: number;
}

export interface Maintainer {
  name?: string;
  domain?: string;
  github?: string;
  email?: string;
  ports_count?: number;
}

export interface Variant {
  variant: string;  // Changed from 'name' to 'variant' to match Django serializer
  description?: string | null;
  port?: string;
}

export interface Dependency {
  type: 'lib' | 'build' | 'run' | 'test' | 'fetch' | 'extract' | 'patch' | 'configure';
  name: string;
}

export interface LivecheckInfo {
  has_check?: boolean;
  error?: string | null;
  last_updated?: string | null;
  version?: string | null;
  result?: string | null;
}

export interface BuildbotInfo {
  no_failures?: boolean;
  all_builds?: boolean;
}

export interface Build {
  id: number;
  port_name: string;
  time_start?: string | null;
  time_elapsed?: number | null;
  builder_name?: {
    name: string;
    display_name: string;
  };
  buildername?: string;
  build_id?: number;
  status?: string;
  watcher_id?: number | null;
  files?: BuildFile[];
}

export interface BuildFile {
  id: number;
  build: number;
  path: string;
}

export interface Stats {
  port_installations: PortInstallation[];
  total_unique_users?: number;
  total_installations?: number;
  last_updated?: string;
}

export interface PortInstallation {
  port: string;
  requested_count?: number;
  total_count: number;
  req_count?: number; // Alternative name from API
}

export interface EnhancedStats {
  current_week: number;
  last_week: number;
  total_submissions: number;
  total_unique_users: number;
  total_ports: number;
}

export interface PopularPort {
  port: string;
  total_count: number;
  req_count: number;
}

export interface APIResponse<T> {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results: T[];
}

export interface SearchResult {
  name: string;
  description?: string | null;
  categories?: string[];
  maintainers?: string[];
  score?: number;
}

export interface AutocompleteResult {
  name: string;
  description?: string | null;
}
