"use client";

import { useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";

export default function SearchRedirect() {
  const searchParams = useSearchParams();
  const router = useRouter();

  useEffect(() => {
    // Parse old search URL and redirect to new /ports with proper filters
    const selectedFacets = searchParams.get("selected_facets");
    const query = searchParams.get("q");
    const installedFile = searchParams.get("installed_file");
    
    const newParams = new URLSearchParams();
    
    // Handle query
    if (query) {
      newParams.set("q", query);
    }
    
    // Handle installed_file
    if (installedFile) {
      newParams.set("installed_file", installedFile);
    }
    
    // Parse selected_facets (e.g., "maintainers_exact:ryandesign")
    if (selectedFacets) {
      const facetParts = selectedFacets.split(":");
      if (facetParts.length === 2) {
        const [facetType, facetValue] = facetParts;
        
        if (facetType === "maintainers_exact") {
          newParams.set("maintainers", facetValue);
        } else if (facetType === "categories_exact") {
          newParams.set("categories", facetValue);
        }
      }
    }
    
    // Redirect to /ports with the converted parameters
    const newUrl = `/ports${newParams.toString() ? `?${newParams.toString()}` : ""}`;
    router.replace(newUrl);
  }, [searchParams, router]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-500 mx-auto mb-4"></div>
        <p className="text-gray-600 dark:text-white/70">Redirecting...</p>
      </div>
    </div>
  );
}

