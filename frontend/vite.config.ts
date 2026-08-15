import { fileURLToPath, URL } from "node:url";

import tailwindcss from "@tailwindcss/vite";
import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) },
  },
  server: {
    // The API is served separately (see deploy/README.md). Proxying rather than pointing
    // the client at an absolute origin keeps the browser same-origin, so nothing here
    // depends on CORS being configured — and the deployed build, served behind one host,
    // behaves the same way as the dev server.
    proxy: {
      "/api": { target: "http://localhost:8000", changeOrigin: true },
    },
  },
});
