/** Copie les ressources statiques dans dist après compilation TypeScript. */
import { cp, copyFile, mkdir } from "node:fs/promises";

await mkdir("dist/styles", { recursive: true });
await copyFile("index.html", "dist/index.html");
await cp("src/styles", "dist/styles", { recursive: true });
