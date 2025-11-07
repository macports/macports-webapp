export default function Footer() {
  return (
    <footer className="mt-16 border-t border-gray-200 dark:border-white/10 bg-white/60 dark:bg-slate-950/60">
      <div className="container py-6 text-center">
        <a
          className="text-sm text-gray-600 dark:text-white/70 hover:text-gray-900 dark:hover:text-white transition-colors"
          href="https://www.macports.org"
          target="_blank"
          rel="noreferrer"
        >
          MacPorts Home
        </a>
      </div>
    </footer>
  );
}
