import { fileURLToPath, URL } from "node:url";

import tailwindcss from "@tailwindcss/vite";
import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) },
  },
  build: {
    // Just above the isolated ECharts chunk (663 kB), so that chunk stops warning on every
    // build while anything *new* crossing the line still does. The right response to a
    // second heavy dependency is another `manualChunks` entry, not another raise here —
    // a threshold nudged up per offender is one nobody reads.
    chunkSizeWarningLimit: 700,
    rollupOptions: {
      output: {
        // ECharts is ~600 kB and belongs to more than one view: `02`'s diagnostics and
        // `05`'s dashboards need it too (`docs/skills-map.md` §5). In its own chunk it is
        // fetched once and cached, rather than duplicated into every view that charts.
        // The routes are lazy anyway, so nobody pays for it before opening a chart.
        // The function form, not the object form: this Rollup types `manualChunks` as
        // `ManualChunksFunction` and rejects the record shape outright.
        manualChunks(id: string): string | undefined {
          return /node_modules[\\/](echarts|vue-echarts|zrender)/.test(id)
            ? "echarts"
            : undefined;
        },
      },
    },
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
