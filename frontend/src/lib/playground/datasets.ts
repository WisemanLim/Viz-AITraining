export type DataPoint = { x: number; y: number; label: number };

export type DatasetKind = "circle" | "xor" | "spiral";

function randn() {
  const u = 1 - Math.random();
  const v = Math.random();
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
}

export function generateDataset(kind: DatasetKind, n: number): DataPoint[] {
  const points: DataPoint[] = [];
  for (let i = 0; i < n; i++) {
    if (kind === "circle") {
      const angle = Math.random() * Math.PI * 2;
      const r = Math.random() * 0.45;
      const cx = Math.cos(angle) * r;
      const cy = Math.sin(angle) * r;
      const label = cx * cx + cy * cy < 0.12 ? 1 : 0;
      points.push({ x: cx, y: cy, label });
    } else if (kind === "xor") {
      const x = Math.random() * 2 - 1;
      const y = Math.random() * 2 - 1;
      const label = (x > 0) !== (y > 0) ? 1 : 0;
      points.push({ x, y, label });
    } else {
      const t = (i / n) * Math.PI * 4;
      const noise = randn() * 0.08;
      const r = 0.35 + (i % 2) * 0.15;
      points.push({
        x: Math.cos(t) * r + noise,
        y: Math.sin(t) * r + noise,
        label: i % 2,
      });
    }
  }
  return points;
}
