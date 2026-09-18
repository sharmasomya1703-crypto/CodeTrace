import { applyArrayEvents, activeIndices } from "./arrayState";
import type { VizEvent } from "../types";

type Props = {
  initial: number[];
  events: VizEvent[];
  index: number;
  current: VizEvent | null;
};

export function ArrayVisualizer({ initial, events, index, current }: Props) {
  const values = applyArrayEvents(initial, events, index);
  const active = activeIndices(current);
  const max = Math.max(1, ...values.map((v) => Math.abs(v)), 1);

  return (
    <div className="flex items-end gap-1.5 h-56 w-full overflow-x-auto px-1">
      {values.map((value, i) => {
        const height = Math.max(12, (Math.abs(value) / max) * 180);
        const isActive = active.has(i);
        const role = current?.role;
        const highlighted =
          current?.type === "highlight" &&
          ((current.indices?.includes(i) ?? false) || current.index === i);
        return (
          <div key={i} className="flex flex-col items-center gap-1 min-w-[2rem]">
            <div
              className={[
                "w-8 rounded-t-md transition-all duration-200",
                isActive
                  ? "bg-accent"
                  : highlighted
                    ? role === "sorted"
                      ? "bg-sea"
                      : "bg-ink/70"
                    : "bg-ink/40",
              ].join(" ")}
              style={{ height }}
              title={`index ${i}: ${value}`}
            />
            <span className="font-mono text-xs text-slate">{value}</span>
          </div>
        );
      })}
      {values.length === 0 && (
        <p className="text-slate self-center">Empty array</p>
      )}
    </div>
  );
}
