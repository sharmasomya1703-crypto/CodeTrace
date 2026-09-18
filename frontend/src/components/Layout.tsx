import { Link, NavLink } from "react-router-dom";
import type { ReactNode } from "react";

const links = [
  { to: "/", label: "Home" },
  { to: "/algorithms", label: "Library" },
  { to: "/visualize", label: "Visualizer" },
  { to: "/compare", label: "Compare" },
  { to: "/problems", label: "Problems" },
  { to: "/about", label: "About" },
];

export function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-ink/10 backdrop-blur-sm bg-paper/70 sticky top-0 z-20">
        <div className="max-w-6xl mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-3">
          <Link to="/" className="font-display text-2xl text-ink tracking-tight">
            CodeTrace
          </Link>
          <nav className="flex flex-wrap gap-1">
            {links.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                className={({ isActive }) =>
                  [
                    "px-3 py-1.5 text-sm rounded-md transition-colors",
                    isActive ? "bg-ink text-paper" : "text-slate hover:bg-ink/5",
                  ].join(" ")
                }
              >
                {l.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 py-8">{children}</main>
      <footer className="border-t border-ink/10 py-4 text-center text-sm text-slate">
        Open source · Runs locally · No AI API required
      </footer>
    </div>
  );
}
