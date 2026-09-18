import type { VizEvent } from "../types";

type Props = {
  graph: Record<string, unknown>;
  events: VizEvent[];
  index: number;
  current: VizEvent | null;
  weighted?: boolean;
};

function collectNodes(graph: Record<string, unknown>): string[] {
  return Object.keys(graph);
}

export function GraphVisualizer({ graph, events, index, current, weighted }: Props) {
  const nodes = collectNodes(graph);
  const visited = new Set<string>();
  let frontier: string[] = [];
  const distances: Record<string, number | null> = {};

  for (let i = 0; i <= index && i < events.length; i++) {
    const ev = events[i];
    if (ev.type === "visit" && ev.node) visited.add(ev.node);
    if (ev.type === "enqueue" && ev.queue) frontier = ev.queue;
    if (ev.type === "dequeue" && ev.queue) frontier = ev.queue;
    if (ev.type === "push" && ev.stack) frontier = ev.stack;
    if (ev.type === "pop" && ev.stack) frontier = ev.stack;
    if (ev.type === "relax_edge" && ev.to !== undefined) {
      distances[ev.to] = ev.new_distance ?? null;
    }
    if (ev.type === "visit" && ev.node && ev.distance !== undefined) {
      distances[ev.node] = ev.distance;
    }
  }

  const n = Math.max(nodes.length, 1);
  const positions = nodes.map((node, i) => {
    const angle = (2 * Math.PI * i) / n - Math.PI / 2;
    return {
      id: node,
      x: 200 + Math.cos(angle) * 140,
      y: 160 + Math.sin(angle) * 110,
    };
  });
  const posMap = Object.fromEntries(positions.map((p) => [p.id, p]));

  const edges: Array<{ from: string; to: string; label?: string }> = [];
  for (const [from, raw] of Object.entries(graph)) {
    const list = raw as unknown[];
    for (const item of list) {
      if (Array.isArray(item)) {
        edges.push({ from, to: String(item[0]), label: String(item[1]) });
      } else {
        edges.push({ from, to: String(item) });
      }
    }
  }

  const activeNode = current?.node ?? current?.to ?? current?.from;

  return (
    <div className="w-full overflow-x-auto">
      <svg viewBox="0 0 400 320" className="w-full max-w-xl mx-auto">
        {edges.map((e, i) => {
          const a = posMap[e.from];
          const b = posMap[e.to];
          if (!a || !b) return null;
          const active =
            current?.type === "relax_edge" && current.from === e.from && current.to === e.to;
          return (
            <g key={i}>
              <line
                x1={a.x}
                y1={a.y}
                x2={b.x}
                y2={b.y}
                stroke={active ? "#0d9488" : "#94a3b8"}
                strokeWidth={active ? 3 : 1.5}
              />
              {weighted && e.label && (
                <text
                  x={(a.x + b.x) / 2}
                  y={(a.y + b.y) / 2 - 6}
                  className="fill-slate text-[10px]"
                  textAnchor="middle"
                >
                  {e.label}
                </text>
              )}
            </g>
          );
        })}
        {positions.map((p) => {
          const isVisited = visited.has(p.id);
          const inFrontier = frontier.includes(p.id);
          const isActive = activeNode === p.id;
          return (
            <g key={p.id}>
              <circle
                cx={p.x}
                cy={p.y}
                r={18}
                className="transition-all duration-200"
                fill={isActive ? "#0d9488" : isVisited ? "#0369a1" : inFrontier ? "#38bdf8" : "#0f2744"}
                opacity={0.9}
              />
              <text
                x={p.x}
                y={p.y + 4}
                textAnchor="middle"
                className="fill-paper text-xs font-mono font-medium"
              >
                {p.id}
              </text>
              {distances[p.id] !== undefined && distances[p.id] !== null && (
                <text
                  x={p.x}
                  y={p.y + 32}
                  textAnchor="middle"
                  className="fill-slate text-[10px] font-mono"
                >
                  d={distances[p.id]}
                </text>
              )}
            </g>
          );
        })}
      </svg>
      <p className="text-sm text-slate text-center">
        Frontier: [{frontier.join(", ")}] · Visited: {visited.size}
      </p>
    </div>
  );
}
