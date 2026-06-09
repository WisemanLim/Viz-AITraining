"use client";

type Props = {
  polling: boolean;
  lastUpdated: Date | null;
  intervalSec: number;
};

export function LiveIndicator({ polling, lastUpdated, intervalSec }: Props) {
  return (
    <div className="flex items-center gap-2 text-xs text-slate-400">
      <span
        className={`inline-block h-2 w-2 rounded-full ${
          polling ? "animate-pulse bg-emerald-400" : "bg-slate-600"
        }`}
        aria-hidden
      />
      <span>
        {polling
          ? intervalSec > 0
            ? `Live · ${intervalSec}s refresh`
            : "Live · WebSocket"
          : "Paused"}
        {lastUpdated
          ? ` · ${lastUpdated.toLocaleTimeString()}`
          : ""}
      </span>
    </div>
  );
}
