import { resolve } from "path";
import fs from "fs";
import { defineConfig, externalizeDepsPlugin } from "electron-vite";
import react from "@vitejs/plugin-react";
import type { Plugin, ViteDevServer } from "vite";
import type { IncomingMessage, ServerResponse } from "http";

function servePublicWasmPlugin(): Plugin {
  return {
    name: "serve-public-wasm",
    configureServer(server: ViteDevServer) {
      server.middlewares.use((req: IncomingMessage, res: ServerResponse, next: () => void) => {
        const rawUrl = req.url ? req.url.split("?")[0] : "";
        if (
          rawUrl.endsWith("/ort-wasm-simd-threaded.mjs") ||
          rawUrl.endsWith("/vad.worklet.bundle.min.js") ||
          rawUrl === "/ort-wasm-simd-threaded.mjs" ||
          rawUrl === "/vad.worklet.bundle.min.js"
        ) {
          const fileName = rawUrl.substring(rawUrl.lastIndexOf("/") + 1);
          const filePath = resolve(__dirname, "src/renderer/public", fileName);
          if (fs.existsSync(filePath)) {
            res.setHeader("Content-Type", "application/javascript");
            return fs.createReadStream(filePath).pipe(res);
          }
        }
        next();
      });
    },
  };
}

export default defineConfig({
  main: {
    plugins: [externalizeDepsPlugin()],
    build: {
      rollupOptions: {
        input: {
          index: resolve(__dirname, "src/main/index.ts"),
        },
      },
    },
  },
  preload: {
    plugins: [externalizeDepsPlugin()],
    build: {
      rollupOptions: {
        input: {
          index: resolve(__dirname, "src/preload/index.ts"),
        },
      },
    },
  },
  renderer: {
    root: "src/renderer",
    server: {
      hmr: {
        overlay: false,
      },
    },
    plugins: [react(), servePublicWasmPlugin()],
    build: {
      rollupOptions: {
        input: {
          index: resolve(__dirname, "src/renderer/index.html"),
        },
      },
    },
  },
});
