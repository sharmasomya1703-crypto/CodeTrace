type Props = {
  playing: boolean;
  speed: number;
  onPlay: () => void;
  onPause: () => void;
  onStep: () => void;
  onReset: () => void;
  onSpeed: (ms: number) => void;
};

export function PlaybackControls({
  playing,
  speed,
  onPlay,
  onPause,
  onStep,
  onReset,
  onSpeed,
}: Props) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      {!playing ? (
        <button type="button" className="btn-primary" onClick={onPlay}>
          Start
        </button>
      ) : (
        <button type="button" className="btn-primary" onClick={onPause}>
          Pause
        </button>
      )}
      <button type="button" className="btn-secondary" onClick={onStep}>
        Step
      </button>
      <button type="button" className="btn-secondary" onClick={onReset}>
        Reset
      </button>
      <label className="flex items-center gap-2 text-sm text-slate">
        Speed
        <input
          type="range"
          min={50}
          max={1000}
          step={50}
          value={speed}
          onChange={(e) => onSpeed(Number(e.target.value))}
        />
        <span className="font-mono w-14">{speed}ms</span>
      </label>
    </div>
  );
}
