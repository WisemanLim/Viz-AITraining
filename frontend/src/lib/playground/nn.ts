import type { DataPoint } from "./datasets";

export type ActivationKind = "tanh" | "relu" | "sigmoid";

type LayerCache = {
  input: number[];
  output: number[];
  preActivation: number[];
};

function activate(x: number, kind: ActivationKind): number {
  if (kind === "tanh") return Math.tanh(x);
  if (kind === "relu") return x > 0 ? x : 0;
  return 1 / (1 + Math.exp(-x));
}

function activateDeriv(x: number, kind: ActivationKind): number {
  if (kind === "tanh") {
    const t = Math.tanh(x);
    return 1 - t * t;
  }
  if (kind === "relu") return x > 0 ? 1 : 0;
  const s = 1 / (1 + Math.exp(-x));
  return s * (1 - s);
}

export class PlaygroundNetwork {
  sizes: number[];
  weights: number[][][];
  biases: number[][];
  activation: ActivationKind;
  learningRate: number;

  constructor(sizes: number[], activation: ActivationKind, learningRate: number) {
    this.sizes = sizes;
    this.activation = activation;
    this.learningRate = learningRate;
    this.weights = [];
    this.biases = [];
    for (let i = 0; i < sizes.length - 1; i++) {
      const out = sizes[i + 1];
      const inp = sizes[i];
      const w: number[][] = [];
      for (let o = 0; o < out; o++) {
        const row: number[] = [];
        for (let j = 0; j < inp; j++) {
          row.push((Math.random() - 0.5) * 0.8);
        }
        w.push(row);
      }
      this.weights.push(w);
      this.biases.push(Array.from({ length: out }, () => (Math.random() - 0.5) * 0.2));
    }
  }

  forward(x: number, y: number): number {
    return this.forwardRaw([x, y]).at(-1)!.output[0];
  }

  private forwardRaw(input: number[]): LayerCache[] {
    const caches: LayerCache[] = [];
    let current = input;
    for (let i = 0; i < this.weights.length; i++) {
      const w = this.weights[i];
      const b = this.biases[i];
      const pre: number[] = [];
      const out: number[] = [];
      for (let o = 0; o < w.length; o++) {
        let sum = b[o];
        for (let j = 0; j < current.length; j++) {
          sum += w[o][j] * current[j];
        }
        pre.push(sum);
        const isLast = i === this.weights.length - 1;
        out.push(isLast ? activate(sum, "sigmoid") : activate(sum, this.activation));
      }
      caches.push({ input: current, output: out, preActivation: pre });
      current = out;
    }
    return caches;
  }

  trainStep(batch: DataPoint[]): number {
    let loss = 0;
    const gradW = this.weights.map((layer) => layer.map((row) => row.map(() => 0)));
    const gradB = this.biases.map((layer) => layer.map(() => 0));

    for (const p of batch) {
      const caches = this.forwardRaw([p.x, p.y]);
      loss += -(
        p.label * Math.log(caches.at(-1)!.output[0] + 1e-8) +
        (1 - p.label) * Math.log(1 - caches.at(-1)!.output[0] + 1e-8)
      );

      let delta = caches.at(-1)!.output.map((o) => o - p.label);

      for (let i = this.weights.length - 1; i >= 0; i--) {
        const cache = caches[i];
        const nextDelta: number[] = new Array(cache.input.length).fill(0);

        for (let o = 0; o < this.weights[i].length; o++) {
          const d =
            i === this.weights.length - 1
              ? delta[o]
              : delta[o] * activateDeriv(cache.preActivation[o], this.activation);
          gradB[i][o] += d;
          for (let j = 0; j < cache.input.length; j++) {
            gradW[i][o][j] += d * cache.input[j];
            nextDelta[j] += d * this.weights[i][o][j];
          }
        }
        delta = nextDelta;
      }
    }

    const scale = this.learningRate / batch.length;
    for (let i = 0; i < this.weights.length; i++) {
      for (let o = 0; o < this.weights[i].length; o++) {
        this.biases[i][o] -= scale * gradB[i][o];
        for (let j = 0; j < this.weights[i][o].length; j++) {
          this.weights[i][o][j] -= scale * gradW[i][o][j];
        }
      }
    }

    return loss / batch.length;
  }
}

export function renderDecisionBoundary(
  ctx: CanvasRenderingContext2D,
  net: PlaygroundNetwork,
  width: number,
  height: number
) {
  const image = ctx.createImageData(width, height);
  for (let py = 0; py < height; py++) {
    for (let px = 0; px < width; px++) {
      const x = (px / width) * 2 - 1;
      const y = (py / height) * 2 - 1;
      const p = net.forward(x, y);
      const idx = (py * width + px) * 4;
      const r = Math.floor(255 * (1 - p));
      const b = Math.floor(255 * p);
      image.data[idx] = r;
      image.data[idx + 1] = Math.floor(40 + 80 * p);
      image.data[idx + 2] = b;
      image.data[idx + 3] = 255;
    }
  }
  ctx.putImageData(image, 0, 0);
}

export function renderPoints(
  ctx: CanvasRenderingContext2D,
  points: DataPoint[],
  width: number,
  height: number
) {
  for (const p of points) {
    const px = ((p.x + 1) / 2) * width;
    const py = ((p.y + 1) / 2) * height;
    ctx.beginPath();
    ctx.arc(px, py, 4, 0, Math.PI * 2);
    ctx.fillStyle = p.label === 1 ? "#22d3ee" : "#f472b6";
    ctx.fill();
    ctx.strokeStyle = "#0f172a";
    ctx.lineWidth = 1;
    ctx.stroke();
  }
}
