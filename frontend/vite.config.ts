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
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        // **Development identity, injected here rather than in the client.** The platform
        // refuses an unauthenticated request (`07` §3.7), and the SPA sends no credential
        // — so before this the browser got 401 on every request while every view and its
        // tests passed. The tests stub `fetch`; nothing exercised the real transport.
        //
        // It belongs in the proxy because a browser must never be able to choose its own
        // workspace: putting these headers in `client.ts` would ship a credential the user
        // can edit in devtools, and the code path would then exist in the production
        // bundle. Here it lives in the dev server only, and the deployed build has no way
        // to reach it. Real OIDC in the SPA landed with W6b-10 — the browser authenticates
        // through the real flow. This proxy injects only the workspace pin, which goes
        // when W6b-11 lands the selector (removal never precedes replacement).
        configure(proxy) {
          const workspace = process.env.GIP_DEV_WORKSPACE_ID;
          if (!workspace) {
            console.warn(
              "\n  GIP_DEV_WORKSPACE_ID is unset — the API will"
              + "\n  answer 401 to everything. `uv run python examples/fremtpl2/seed.py`"
              + "\n  prints it.\n",
            );
            return;
          }
          proxy.on("proxyReq", (request) => {
            request.setHeader("x-dev-workspace-id", workspace);
          });
        },
      },
    },
  },
});
