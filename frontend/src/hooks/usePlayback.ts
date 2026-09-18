import { useCallback, useEffect, useRef, useState } from "react";
import type { VizEvent } from "../types";

export function usePlayback(events: VizEvent[], defaultSpeed = 400) {
  const [index, setIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(defaultSpeed);
  const timer = useRef<number | null>(null);

  const reset = useCallback(() => {
    setPlaying(false);
    setIndex(0);
  }, []);

  const stepForward = useCallback(() => {
    setIndex((i) => Math.min(i + 1, Math.max(events.length - 1, 0)));
  }, [events.length]);

  useEffect(() => {
    reset();
  }, [events, reset]);

  useEffect(() => {
    if (!playing) {
      if (timer.current) window.clearInterval(timer.current);
      return;
    }
    timer.current = window.setInterval(() => {
      setIndex((i) => {
        if (i >= events.length - 1) {
          setPlaying(false);
          return i;
        }
        return i + 1;
      });
    }, speed);
    return () => {
      if (timer.current) window.clearInterval(timer.current);
    };
  }, [playing, speed, events.length]);

  const current = events[index] ?? null;
  const visible = events.slice(0, index + 1);

  return {
    index,
    current,
    visible,
    playing,
    speed,
    setSpeed,
    play: () => setPlaying(true),
    pause: () => setPlaying(false),
    toggle: () => setPlaying((p) => !p),
    stepForward,
    reset,
    setIndex,
  };
}
