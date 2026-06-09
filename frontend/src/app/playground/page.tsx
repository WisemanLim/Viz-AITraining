import { PlaygroundApp } from "@/components/PlaygroundApp";

export default function PlaygroundPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">NN Playground</h1>
        <p className="mt-2 max-w-2xl text-sm text-slate-400">
          TensorFlow Playground–style 2D classification demo. Adjust hidden
          layers, activation, and learning rate — watch the decision boundary
          evolve in real time (PRD M5.1).
        </p>
      </div>
      <PlaygroundApp />
    </div>
  );
}
