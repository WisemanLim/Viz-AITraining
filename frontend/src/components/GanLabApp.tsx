"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { sampleNoise, sampleRing } from "@/lib/gan-lab/data";
import {
  GanLabModel,
  renderDiscriminatorField,
  renderPoints,
} from "@/lib/gan-lab/gan";

const CANVAS = 420;
const BATCH = 64;

export function GanLabApp() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const modelRef = useRef<GanLabModel | null>(null);
  const realRef = useRef(sampleRing(120));
  const fakeRef = useRef<{ x: number; y: number }[]>([]);
  const rafRef = useRef<number | null>(null);

  const [lrG, setLrG] = useState(0.003);
  const [lrD, setLrD] = useState(0.003);
  const [playing, setPlaying] = useState(false);
  const [dLoss, setDLoss] = useState(0);
  const [gLoss, setGLoss] = useState(0);
  const [step, setStep] = useState(0);

  const paint = useCallback(() => {
    const canvas = canvasRef.current;
    const model = modelRef.current;
    if (!canvas || !model) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    renderDiscriminatorField(ctx, model, CANVAS, CANVAS);
    renderPoints(ctx, realRef.current, CANVAS, CANVAS, "#34d399");
    renderPoints(ctx, fakeRef.current, CANVAS, CANVAS, "#c084fc");
  }, []);

  const rebuild = useCallback(() => {
    modelRef.current = new GanLabModel(lrG, lrD);
    fakeRef.current = [];
    setStep(0);
    setDLoss(0);
    setGLoss(0);
    paint();
  }, [lrG, lrD, paint]);

  useEffect(() => {
    rebuild();
  }, [rebuild]);

  useEffect(() => {
    if (!playing) {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      return;
    }
    const tick = () => {
      const model = modelRef.current;
      if (model) {
        const noise = sampleNoise(BATCH);
        fakeRef.current = model.trainStep(realRef.current, noise);
        setDLoss(model.dLoss);
        setGLoss(model.gLoss);
        setStep(model.step);
        paint();
      }
      rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [playing, paint]);

  return (
    <div className="grid gap-6 lg:grid-cols-[420px_1fr]">
      <div className="overflow-hidden rounded-lg border border-slate-800 bg-slate-900/40">
        <canvas ref={canvasRef} width={CANVAS} height={CANVAS} className="block w-full" />
        <p className="border-t border-slate-800 px-3 py-2 text-xs text-slate-500">
          Green = real ring · Purple = generator · Background = discriminator score
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">GAN Lab</h1>
          <p className="mt-1 text-sm text-slate-400">
            Adversarial training demo — generator vs discriminator on a 2D ring (M5.2).
          </p>
        </div>

        <label className="block text-sm">
          <span className="text-slate-400">Generator LR</span>
          <input
            type="range"
            min={0.0005}
            max={0.01}
            step={0.0005}
            value={lrG}
            onChange={(e) => setLrG(parseFloat(e.target.value))}
            className="mt-1 w-full"
          />
          <span className="font-mono text-xs text-slate-500">{lrG.toFixed(4)}</span>
        </label>

        <label className="block text-sm">
          <span className="text-slate-400">Discriminator LR</span>
          <input
            type="range"
            min={0.0005}
            max={0.01}
            step={0.0005}
            value={lrD}
            onChange={(e) => setLrD(parseFloat(e.target.value))}
            className="mt-1 w-full"
          />
          <span className="font-mono text-xs text-slate-500">{lrD.toFixed(4)}</span>
        </label>

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => setPlaying((p) => !p)}
            className="rounded-md bg-cyan-600 px-4 py-2 text-sm font-medium hover:bg-cyan-500"
          >
            {playing ? "Pause" : "Train"}
          </button>
          <button
            type="button"
            onClick={rebuild}
            className="rounded-md border border-slate-600 px-4 py-2 text-sm text-slate-300 hover:border-slate-400"
          >
            Reset
          </button>
        </div>

        <div className="grid grid-cols-3 gap-3 font-mono text-xs">
          <div className="rounded border border-slate-800 bg-slate-900/50 p-3">
            <p className="text-slate-500">Step</p>
            <p className="mt-1 text-lg text-slate-200">{step}</p>
          </div>
          <div className="rounded border border-slate-800 bg-slate-900/50 p-3">
            <p className="text-slate-500">D loss</p>
            <p className="mt-1 text-lg text-emerald-400">{dLoss.toFixed(3)}</p>
          </div>
          <div className="rounded border border-slate-800 bg-slate-900/50 p-3">
            <p className="text-slate-500">G loss</p>
            <p className="mt-1 text-lg text-violet-400">{gLoss.toFixed(3)}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
