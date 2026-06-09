"use client";

import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import type { Architecture3DLayout } from "@/lib/types";

type Props = {
  layout: Architecture3DLayout;
};

function hueColor(hue: string, activation: number): THREE.Color {
  const t = 0.35 + activation * 0.65;
  if (hue === "input") return new THREE.Color(0.2 * t, 0.75 * t, 0.95 * t);
  if (hue === "output") return new THREE.Color(0.75 * t, 0.5 * t, 0.98 * t);
  return new THREE.Color(0.98 * t, 0.55 * t, 0.25 * t);
}

function weightColor(weight: number, pulse: number): THREE.Color {
  const w = Math.min(Math.abs(weight), 1);
  const t = 0.25 + w * 0.75 * pulse;
  return new THREE.Color(0.1 * (1 - t), 0.7 * t + 0.2 * pulse, 0.85 * t + 0.15);
}

export function Architecture3DViewer({ layout }: Props) {
  const mountRef = useRef<HTMLDivElement>(null);
  const [animateWeights, setAnimateWeights] = useState(true);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    const width = mount.clientWidth;
    const height = 420;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0f172a);

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    const centerZ = layout.bounds.z / 2;
    camera.position.set(3.5, 2.5, centerZ + 4);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    mount.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 0, centerZ);
    controls.enableDamping = true;
    controls.update();

    scene.add(new THREE.AmbientLight(0xffffff, 0.55));
    const dir = new THREE.DirectionalLight(0xffffff, 0.85);
    dir.position.set(4, 6, 8);
    scene.add(dir);

    const sphereGeo = new THREE.SphereGeometry(0.12, 16, 16);

    for (const node of layout.nodes) {
      const mat = new THREE.MeshStandardMaterial({
        color: hueColor(node.hue, node.activation),
        emissive: hueColor(node.hue, node.activation).multiplyScalar(0.25),
      });
      const mesh = new THREE.Mesh(sphereGeo, mat);
      mesh.position.set(node.position[0], node.position[1], node.position[2]);
      scene.add(mesh);
    }

    for (const layer of layout.layers) {
      const geo = new THREE.BoxGeometry(0.1, layout.bounds.y, 0.1);
      const mat = new THREE.MeshBasicMaterial({
        color: 0x334155,
        transparent: true,
        opacity: 0.35,
      });
      const pillar = new THREE.Mesh(geo, mat);
      pillar.position.set(layer.position[0], layer.position[1], layer.position[2]);
      scene.add(pillar);
    }

    type EdgeAnim = {
      line: THREE.Line;
      material: THREE.LineBasicMaterial;
      weight: number;
      points: THREE.Vector3[];
      phase: number;
      flow: THREE.Mesh | null;
    };

    const edgeAnims: EdgeAnim[] = [];
    const maxWeight = Math.max(
      ...layout.edges.map((e) => Math.abs(e.weight)),
      0.01,
    );

    for (let ei = 0; ei < layout.edges.length; ei++) {
      const edge = layout.edges[ei];
      const points = edge.points.map(
        (p) => new THREE.Vector3(p[0], p[1], p[2]),
      );
      const wNorm = Math.abs(edge.weight) / maxWeight;
      const mat = new THREE.LineBasicMaterial({
        color: weightColor(edge.weight, 1),
        transparent: true,
        opacity: 0.2 + wNorm * 0.55,
        linewidth: 1,
      });
      const geo = new THREE.BufferGeometry().setFromPoints(points);
      const line = new THREE.Line(geo, mat);
      scene.add(line);

      let flow: THREE.Mesh | null = null;
      if (wNorm > 0.15) {
        const flowGeo = new THREE.SphereGeometry(0.04 + wNorm * 0.04, 8, 8);
        const flowMat = new THREE.MeshBasicMaterial({
          color: 0x22d3ee,
          transparent: true,
          opacity: 0.85,
        });
        flow = new THREE.Mesh(flowGeo, flowMat);
        flow.position.copy(points[0]);
        scene.add(flow);
      }

      edgeAnims.push({
        line,
        material: mat,
        weight: edge.weight,
        points,
        phase: ei * 0.7,
        flow,
      });
    }

    scene.add(new THREE.GridHelper(6, 12, 0x1e293b, 0x1e293b));

    const clock = new THREE.Clock();
    let frame = 0;
    const animate = () => {
      frame = requestAnimationFrame(animate);
      const t = clock.getElapsedTime();

      if (animateWeights) {
        for (const ea of edgeAnims) {
          const wNorm = Math.abs(ea.weight) / maxWeight;
          const pulse = 0.55 + 0.45 * Math.sin(t * 2.2 + ea.phase);
          ea.material.opacity = 0.15 + wNorm * 0.65 * pulse;
          ea.material.color.copy(weightColor(ea.weight, pulse));

          if (ea.flow && ea.points.length >= 2) {
            const travel = (Math.sin(t * 1.8 + ea.phase) + 1) / 2;
            ea.flow.position.lerpVectors(ea.points[0], ea.points[1], travel);
            ea.flow.scale.setScalar(0.8 + wNorm * pulse * 0.5);
          }
        }
      }

      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    const onResize = () => {
      const w = mount.clientWidth;
      camera.aspect = w / height;
      camera.updateProjectionMatrix();
      renderer.setSize(w, height);
    };
    window.addEventListener("resize", onResize);

    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("resize", onResize);
      controls.dispose();
      sphereGeo.dispose();
      for (const ea of edgeAnims) {
        ea.line.geometry.dispose();
        ea.material.dispose();
        ea.flow?.geometry.dispose();
        (ea.flow?.material as THREE.Material | undefined)?.dispose();
      }
      renderer.dispose();
      mount.removeChild(renderer.domElement);
    };
  }, [layout, animateWeights]);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between gap-2">
        <p className="text-xs text-slate-500">
          Drag to rotate · scroll to zoom · edge weight pulse animation
        </p>
        <label className="flex cursor-pointer items-center gap-2 text-xs text-slate-400">
          <input
            type="checkbox"
            checked={animateWeights}
            onChange={(e) => setAnimateWeights(e.target.checked)}
            className="accent-cyan-400"
          />
          Animate weights
        </label>
      </div>
      <div
        ref={mountRef}
        className="h-[420px] w-full overflow-hidden rounded-lg border border-slate-800 bg-slate-950"
      />
    </div>
  );
}
