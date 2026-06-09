import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Viz-AITraining",
  description: "ML/DL training visualization dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-950 text-slate-100 antialiased">
        <header className="border-b border-slate-800 bg-slate-950/90 backdrop-blur">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
            <Link href="/" className="flex items-center gap-2">
              <span className="text-lg font-semibold tracking-tight">
                Viz-AITraining
              </span>
              <span className="rounded bg-cyan-950 px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wider text-cyan-400">
                Dashboard
              </span>
            </Link>
            <nav className="flex items-center gap-4 text-sm">
              <Link href="/" className="text-slate-400 hover:text-cyan-400">
                Runs
              </Link>
              <Link href="/compare" className="text-slate-400 hover:text-cyan-400">
                Compare
              </Link>
              <Link href="/graphs" className="text-slate-400 hover:text-cyan-400">
                Graphs
              </Link>
              <Link href="/playground" className="text-slate-400 hover:text-cyan-400">
                Playground
              </Link>
              <Link href="/gan-lab" className="text-slate-400 hover:text-cyan-400">
                GAN Lab
              </Link>
              <a
                href={`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/docs`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-slate-400 hover:text-cyan-400"
              >
                API Docs ↗
              </a>
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
      </body>
    </html>
  );
}
