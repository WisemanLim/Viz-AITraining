import type { Point2D } from "./data";

type Layer = { w: number[][]; b: number[] };

function relu(x: number): number {
  return x > 0 ? x : 0;
}

function reluDeriv(pre: number): number {
  return pre > 0 ? 1 : 0;
}

function sigmoid(x: number): number {
  return 1 / (1 + Math.exp(-Math.max(-20, Math.min(20, x))));
}

function initLayer(inSize: number, outSize: number, scale = 0.5): Layer {
  const w: number[][] = [];
  for (let o = 0; o < outSize; o++) {
    w.push(
      Array.from({ length: inSize }, () => (Math.random() - 0.5) * scale),
    );
  }
  return { w, b: Array.from({ length: outSize }, () => (Math.random() - 0.5) * 0.05) };
}

function matVec(layer: Layer, input: number[]): number[] {
  return layer.w.map((row, o) =>
    row.reduce((sum, w, i) => sum + w * input[i], layer.b[o]),
  );
}

type DiscCache = {
  input: number[];
  h1Pre: number[];
  h1: number[];
  h2Pre: number[];
  h2: number[];
  outPre: number[];
  score: number;
};

type GenCache = {
  z: number[];
  h1Pre: number[];
  h1: number[];
  h2Pre: number[];
  h2: number[];
  outPre: number[];
  point: Point2D;
};

export class GanLabModel {
  g1: Layer;
  g2: Layer;
  gOut: Layer;
  d1: Layer;
  d2: Layer;
  dOut: Layer;
  lrG: number;
  lrD: number;
  dLoss = 0;
  gLoss = 0;
  step = 0;

  constructor(lrG = 0.003, lrD = 0.003) {
    this.lrG = lrG;
    this.lrD = lrD;
    this.g1 = initLayer(2, 12);
    this.g2 = initLayer(12, 12);
    this.gOut = initLayer(12, 2);
    this.d1 = initLayer(2, 12);
    this.d2 = initLayer(12, 12);
    this.dOut = initLayer(12, 1);
  }

  generate(noise: number[][]): Point2D[] {
    return noise.map((z) => this.forwardGen(z).point);
  }

  discriminate(point: Point2D): number {
    return this.forwardDisc([point.x, point.y]).score;
  }

  trainStep(realBatch: Point2D[], noiseBatch: number[][]): Point2D[] {
    this.dLoss = this.trainDiscriminator(realBatch, noiseBatch);
    this.gLoss = this.trainGenerator(noiseBatch);
    this.step += 1;
    return this.generate(noiseBatch);
  }

  private forwardGen(z: number[]): GenCache {
    const h1Pre = matVec(this.g1, z);
    const h1 = h1Pre.map(relu);
    const h2Pre = matVec(this.g2, h1);
    const h2 = h2Pre.map(relu);
    const outPre = matVec(this.gOut, h2);
    return {
      z,
      h1Pre,
      h1,
      h2Pre,
      h2,
      outPre,
      point: { x: Math.tanh(outPre[0]), y: Math.tanh(outPre[1]) },
    };
  }

  private forwardDisc(input: number[]): DiscCache {
    const h1Pre = matVec(this.d1, input);
    const h1 = h1Pre.map(relu);
    const h2Pre = matVec(this.d2, h1);
    const h2 = h2Pre.map(relu);
    const outPre = matVec(this.dOut, h2);
    return { input, h1Pre, h1, h2Pre, h2, outPre, score: sigmoid(outPre[0]) };
  }

  private trainDiscriminator(real: Point2D[], noise: number[][]): number {
    let loss = 0;
    const gD1 = initLayer(this.d1.w[0].length, this.d1.w.length);
    const gD2 = initLayer(this.d2.w[0].length, this.d2.w.length);
    const gDOut = initLayer(this.dOut.w[0].length, this.dOut.w.length);
    let n = 0;

    const acc = (input: number[], target: number) => {
      const cache = this.forwardDisc(input);
      loss +=
        -(target * Math.log(cache.score + 1e-8) +
          (1 - target) * Math.log(1 - cache.score + 1e-8));
      const deltaOut = cache.score - target;
      this.backpropDisc(cache, deltaOut, gD1, gD2, gDOut);
      n += 1;
    };

    for (const p of real) acc([p.x, p.y], 1);
    for (const z of noise) {
      const fake = this.forwardGen(z);
      acc([fake.point.x, fake.point.y], 0);
    }

    const scale = this.lrD / n;
    this.apply(this.d1, gD1, scale);
    this.apply(this.d2, gD2, scale);
    this.apply(this.dOut, gDOut, scale);
    return loss / n;
  }

  private trainGenerator(noise: number[][]): number {
    let loss = 0;
    const gG1 = initLayer(this.g1.w[0].length, this.g1.w.length);
    const gG2 = initLayer(this.g2.w[0].length, this.g2.w.length);
    const gGOut = initLayer(this.gOut.w[0].length, this.gOut.w.length);

    for (const z of noise) {
      const gen = this.forwardGen(z);
      const disc = this.forwardDisc([gen.point.x, gen.point.y]);
      loss += -Math.log(disc.score + 1e-8);

      const deltaOut = -1 / (disc.score + 1e-8);
      const deltaScore = deltaOut * disc.score * (1 - disc.score);
      const deltaPoint = this.backpropDiscToInput(disc, deltaScore);
      const deltaOutPre = [
        deltaPoint[0] * (1 - gen.point.x * gen.point.x),
        deltaPoint[1] * (1 - gen.point.y * gen.point.y),
      ];
      this.backpropGen(gen, deltaOutPre, gG1, gG2, gGOut);
    }

    const scale = this.lrG / noise.length;
    this.apply(this.g1, gG1, scale);
    this.apply(this.g2, gG2, scale);
    this.apply(this.gOut, gGOut, scale);
    return loss / noise.length;
  }

  private backpropDisc(
    cache: DiscCache,
    deltaOut: number,
    g1: Layer,
    g2: Layer,
    gOut: Layer,
  ) {
    gOut.b[0] += deltaOut;
    for (let i = 0; i < cache.h2.length; i++) {
      gOut.w[0][i] += deltaOut * cache.h2[i];
    }

    const deltaH2 = cache.h2.map((_, j) => {
      const dh = deltaOut * this.dOut.w[0][j] * reluDeriv(cache.h2Pre[j]);
      g2.b[j] += dh;
      for (let i = 0; i < cache.h1.length; i++) {
        g2.w[j][i] += dh * cache.h1[i];
      }
      return dh;
    });

    cache.h1.forEach((_, o) => {
      let d = 0;
      for (let j = 0; j < cache.h2.length; j++) {
        d += deltaH2[j] * this.d2.w[j][o];
      }
      const dh = d * reluDeriv(cache.h1Pre[o]);
      g1.b[o] += dh;
      for (let i = 0; i < cache.input.length; i++) {
        g1.w[o][i] += dh * cache.input[i];
      }
    });
  }

  private backpropDiscToInput(cache: DiscCache, deltaScore: number): number[] {
    const deltaH2 = cache.h2.map((_, o) => {
      return deltaScore * this.dOut.w[0][o] * reluDeriv(cache.h2Pre[o]);
    });
    const deltaInput = [0, 0];
    cache.h1.forEach((_, o) => {
      const d =
        deltaH2.reduce((sum, dh, j) => sum + dh * this.d2.w[j][o], 0) *
        reluDeriv(cache.h1Pre[o]);
      for (let i = 0; i < 2; i++) deltaInput[i] += d * this.d1.w[o][i];
    });
    return deltaInput;
  }

  private backpropGen(
    cache: GenCache,
    deltaOutPre: number[],
    g1: Layer,
    g2: Layer,
    gOut: Layer,
  ) {
    deltaOutPre.forEach((d, o) => {
      gOut.b[o] += d;
      for (let i = 0; i < cache.h2.length; i++) gOut.w[o][i] += d * cache.h2[i];
    });

    const deltaH2 = cache.h2.map((_, o) => {
      const d = deltaOutPre.reduce((sum, dout, j) => sum + dout * this.gOut.w[j][o], 0);
      g2.b[o] += d * reluDeriv(cache.h2Pre[o]);
      for (let i = 0; i < cache.h1.length; i++) {
        g2.w[o][i] += d * reluDeriv(cache.h2Pre[o]) * cache.h1[i];
      }
      return d * reluDeriv(cache.h2Pre[o]);
    });

    cache.h1.forEach((_, o) => {
      const d = deltaH2.reduce((sum, dh, j) => sum + dh * this.g2.w[j][o], 0);
      g1.b[o] += d * reluDeriv(cache.h1Pre[o]);
      for (let i = 0; i < cache.z.length; i++) {
        g1.w[o][i] += d * reluDeriv(cache.h1Pre[o]) * cache.z[i];
      }
    });
  }

  private apply(layer: Layer, grad: Layer, scale: number) {
    layer.b = layer.b.map((b, i) => b - scale * grad.b[i]);
    layer.w = layer.w.map((row, o) =>
      row.map((w, i) => w - scale * grad.w[o][i]),
    );
  }
}

export function renderDiscriminatorField(
  ctx: CanvasRenderingContext2D,
  model: GanLabModel,
  width: number,
  height: number,
) {
  const image = ctx.createImageData(width, height);
  for (let py = 0; py < height; py++) {
    for (let px = 0; px < width; px++) {
      const x = (px / width) * 2 - 1;
      const y = (py / height) * 2 - 1;
      const p = model.discriminate({ x, y });
      const idx = (py * width + px) * 4;
      image.data[idx] = Math.floor(25 + 35 * (1 - p));
      image.data[idx + 1] = Math.floor(15 + 50 * p);
      image.data[idx + 2] = Math.floor(35 + 170 * p);
      image.data[idx + 3] = 255;
    }
  }
  ctx.putImageData(image, 0, 0);
}

export function renderPoints(
  ctx: CanvasRenderingContext2D,
  points: Point2D[],
  width: number,
  height: number,
  color: string,
) {
  for (const p of points) {
    const px = ((p.x + 1) / 2) * width;
    const py = ((p.y + 1) / 2) * height;
    ctx.beginPath();
    ctx.arc(px, py, 3.5, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
  }
}
