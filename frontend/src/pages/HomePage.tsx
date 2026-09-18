import { Link } from "react-router-dom";

export function HomePage() {
  return (
    <div>
      <section className="relative overflow-hidden rounded-none min-h-[70vh] flex flex-col justify-end pb-12">
        <div
          className="absolute inset-0 -mx-4 md:-mx-[calc((100vw-100%)/2+1rem)]"
          style={{
            backgroundImage:
              "linear-gradient(120deg, rgba(20,33,61,0.88), rgba(20,33,61,0.55)), url('https://images.unsplash.com/photo-1515879218367-8466d910aaa4?auto=format&fit=crop&w=1600&q=80')",
            backgroundSize: "cover",
            backgroundPosition: "center",
          }}
          aria-hidden
        />
        <div className="relative z-10 max-w-2xl text-paper px-1 animate-[fadeUp_0.7s_ease]">
          <p className="font-display text-5xl md:text-6xl mb-3">CodeTrace</p>
          <h1 className="text-xl md:text-2xl font-sans font-semibold mb-3">
            See algorithms move — then test your own Python
          </h1>
          <p className="text-paper/85 mb-6 max-w-xl">
            Step-by-step visualization, side-by-side comparison, and local solution
            evaluation. No AI API. No paid service.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link to="/visualize" className="btn-accent">
              Open visualizer
            </Link>
            <Link to="/problems" className="btn-ghost">
              Try a problem
            </Link>
          </div>
        </div>
      </section>

      <section className="mt-16 grid md:grid-cols-3 gap-10">
        {[
          {
            title: "Visualize",
            body: "Replay structured events: compares, swaps, visits, and edge relaxations.",
            to: "/visualize",
          },
          {
            title: "Compare",
            body: "Run two algorithms on the same input and chart how metrics grow with size.",
            to: "/compare",
          },
          {
            title: "Evaluate",
            body: "Submit Python solutions. Scoring comes from real tests in a subprocess runner.",
            to: "/problems",
          },
        ].map((item, i) => (
          <Link
            key={item.title}
            to={item.to}
            className="group block"
            style={{ animation: `fadeUp 0.6s ease ${0.1 * i}s both` }}
          >
            <h2 className="font-display text-2xl text-ink mb-2 group-hover:text-accent transition-colors">
              {item.title}
            </h2>
            <p className="text-slate">{item.body}</p>
          </Link>
        ))}
      </section>

      <style>{`
        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(12px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}
