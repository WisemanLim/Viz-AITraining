export type Point2D = { x: number; y: number };

export function sampleRing(n: number, radius = 0.55): Point2D[] {
  const pts: Point2D[] = [];
  for (let i = 0; i < n; i++) {
    const angle = Math.random() * Math.PI * 2;
    const r = radius + (Math.random() - 0.5) * 0.08;
    pts.push({ x: Math.cos(angle) * r, y: Math.sin(angle) * r });
  }
  return pts;
}

export function sampleUniform(n: number): Point2D[] {
  return Array.from({ length: n }, () => ({
    x: Math.random() * 2 - 1,
    y: Math.random() * 2 - 1,
  }));
}

export function sampleNoise(n: number): number[][] {
  return Array.from({ length: n }, () => [
    Math.random() * 2 - 1,
    Math.random() * 2 - 1,
  ]);
}
