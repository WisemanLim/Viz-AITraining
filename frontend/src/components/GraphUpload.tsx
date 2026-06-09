"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { uploadOnnxGraph } from "@/lib/api";

type Props = {
  runId?: string;
  onUploaded?: () => void;
};

export function GraphUpload({ runId, onUploaded }: Props) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFile(file: File) {
    if (!file.name.toLowerCase().endsWith(".onnx")) {
      setError("Please select a .onnx file");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const graph = await uploadOnnxGraph(file, runId);
      onUploaded?.();
      router.push(`/graphs/${graph.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="rounded-lg border border-dashed border-slate-700 bg-slate-900/30 p-6">
      <label className="flex cursor-pointer flex-col items-center gap-2">
        <span className="text-sm font-medium text-slate-300">
          Import ONNX model
        </span>
        <span className="text-xs text-slate-500">
          .onnx files up to 50MB — layers, ops, and tensor shapes
        </span>
        <input
          type="file"
          accept=".onnx"
          className="hidden"
          disabled={busy}
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) handleFile(f);
            e.target.value = "";
          }}
        />
        <span className="mt-2 rounded-md bg-cyan-600 px-4 py-2 text-sm font-medium text-white hover:bg-cyan-500">
          {busy ? "Importing…" : "Choose file"}
        </span>
      </label>
      {error && (
        <p className="mt-3 text-center text-xs text-red-400">{error}</p>
      )}
    </div>
  );
}
