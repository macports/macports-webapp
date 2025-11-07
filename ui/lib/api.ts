export const API_BASE =
  (process.env.NEXT_PUBLIC_MACPORTS_API_BASE &&
    process.env.NEXT_PUBLIC_MACPORTS_API_BASE.trim()) ||
  "https://ports.macports.org/api/v1";

export function apiUrl(path: string): string {
  // Ensure single slash join
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE.replace(/\/+$/, "")}${p}`;
}
