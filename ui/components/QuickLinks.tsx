export default function QuickLinks() {
  const links = [
    {
      title: "Browse All Ports",
      desc: "Explore thousands of packages available for macOS.",
      href: "/ports",
      cta: "Browse Ports",
      external: false
    },
    {
      title: "Search Packages",
      desc: "Find exactly what you're looking for quickly.",
      href: "/search",
      cta: "Start Searching",
      external: false
    },
    {
      title: "Install MacPorts",
      desc: "Get started by installing MacPorts on your Mac.",
      href: "https://www.macports.org/install.php",
      cta: "Install",
      external: true
    },
    {
      title: "Documentation",
      desc: "Learn how to use MacPorts and manage ports.",
      href: "https://guide.macports.org/",
      cta: "Read Docs",
      external: true
    },
    {
      title: "Categories",
      desc: "Browse ports organized by category.",
      href: "/categories",
      cta: "View Categories",
      external: false
    },
    {
      title: "Maintainers",
      desc: "Meet the people who maintain MacPorts packages.",
      href: "/maintainers",
      cta: "View Maintainers",
      external: false
    }
  ];

  return (
    <section className="space-y-4">
      <h2 className="text-xl font-semibold">Quick Links</h2>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {links.map((l) => (
          <a
            key={l.title}
            className="card group dark:hover:bg-white/10 hover:bg-gray-50 transition-all duration-200 hover:scale-[1.02]"
            href={l.href}
            target={l.external ? "_blank" : undefined}
            rel={l.external ? "noreferrer" : undefined}
          >
            <div className="flex h-full flex-col">
              <h3 className="text-lg font-semibold">{l.title}</h3>
              <p className="mt-1 flex-1 text-sm text-gray-600 dark:text-white/70">{l.desc}</p>
              <div className="mt-4">
                <span className="btn-primary">{l.cta}</span>
              </div>
            </div>
          </a>
        ))}
      </div>
    </section>
  );
}
