"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  type DatasetKind,
  generateDataset,
} from "@/lib/playground/datasets";
import {
  type ActivationKind,
  PlaygroundNetwork,
  renderDecisionBoundary,
  renderPoints,
} from "@/lib/playground/nn";

const CANVAS = 420;

export function PlaygroundApp() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const netRef = useRef<PlaygroundNetwork | null>(null);
  const dataRef = useRef(generateDataset("circle", 200));
  const rafRef = useRef<number | null>(null);

  const [dataset, setDataset] = useState<DatasetKind>("circle");
  const [hidden, setHidden] = useState("4,4");
  const [activation, setActivation] = useState<ActivationKind>("tanh");
  const [learningRate, setLearningRate] = useState(0.03);
  const [playing, setPlaying] = useState(false);
  const [loss, setLoss] = useState(0);
  const [step, setStep] = useState(0);

  const rebuildNet = useCallback(() => {
    const hiddenSizes = hidden
      .split(",")
      .map((s) => parseInt(s.trim(), 10))
      .filter((n) => !Number.isNaN(n) && n > 0);
    netRef.current = new PlaygroundNetwork(
      [2, ...hiddenSizes, 1],
      activation,
      learningRate
    );
    setStep(0);
    setLoss(0);
  }, [hidden, activation, learningRate]);

  useEffect(() => {
    rebuildNet();
  }, [rebuildNet]);

  useEffect(() => {
    dataRef.current = generateDataset(dataset, 200);
    rebuildNet();
  }, [dataset, rebuildNet]);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    const net = netRef.current;
    if (!canvas || !net) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    renderDecisionBoundary(ctx, net, CANVAS, CANVAS);
    renderPoints(ctx, dataRef.current, CANVAS, CANVAS);
  }, []);

  useEffect(() => {
    draw();
  }, [draw, step]);

  useEffect(() => {
    if (!playing) {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      return;
    }

    const tick = () => {
      const net = netRef.current;
      if (!net) return;
      const batch = dataRef.current;
      const sample = batch.sort(() => Math.random() - 0.5).slice(0, 20);
      const l = net.trainStep(sample);
      setLoss(l);
      setStep((s) => s + 1);
      draw();
      rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [playing, draw]);

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_280px]">
      <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
        <canvas
          ref={canvasRef}
          width={CANVAS}
          height={CANVAS}
          className="mx-auto block rounded-md border border-slate-700"
        />
        <p className="mt-3 text-center text-xs text-slate-500">
          Decision boundary updates while training (M5.1 Playground)
        </p>
      </div>

      <aside className="space-y-4 rounded-lg border border-slate-800 bg-slate-900/40 p-4">
        <h2 className="text-sm font-medium text-slate-200">Controls</h2>

        <label className="block text-xs text-slate-400">
          Dataset
          <select
            className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1.5 text-sm"
            value={dataset}
            onChange={(e) => setDataset(e.target.value as DatasetKind)}
          >
            <option value="circle">Circle</option>
            <option value="xor">XOR</option>
            <option value="spiral">Spiral</option>
          </select>
        </label>

        <label className="block text-xs text-slate-400">
          Hidden layers (comma-separated)
          <input
            className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1.5 font-mono text-sm"
            value={hidden}
            onChange={(e) => setHidden(e.target.value)}
          />
        </label>

        <label className="block text-xs text-slate-400">
          Activation
          <select
            className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1.5 text-sm"
            value={activation}
            onChange={(e) => setActivation(e.target.value as ActivationKind)}
          >
            <option value="tanh">Tanh</option>
            <option value="relu">ReLU</option>
            <option value="sigmoid">Sigmoid</option>
          </select>
        </label>

        <label className="block text-xs text-slate-400">
          Learning rate ({learningRate.toFixed(3)})
          <input
            type="range"
            min={0.001}
            max={0.2}
            step={0.001}
            value={learningRate}
            onChange={(e) => setLearningRate(parseFloat(e.target.value))}
            className="mt-2 w-full"
          />
        </label>

        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => setPlaying((p) => !p)}
            className="flex-1 rounded-md bg-cyan-600 px-3 py-2 text-sm font-medium text-white hover:bg-cyan-500"
          >
            {playing ? "Pause" : "Train"}
          </button>
          <button
            type="button"
            onClick={() => {
              rebuildNet();
              draw();
            }}
            className="rounded-md border border-slate-600 px-3 py-2 text-sm text-slate-300 hover:border-slate-400"
          >
            Reset
          </button>
        </div>

        <dl className="grid grid-cols-2 gap-2 text-xs">
          <div>
            <dt className="text-slate-500">Step</dt>
            <dd className="font-mono text-slate-200">{step}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Loss</dt>
            <dd className="font-mono text-slate-200">{loss.toFixed(4)}</dd>
          </div>
        </dl>
      </aside>
    </div>
  );
}
