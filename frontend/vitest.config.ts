import { fileURLToPath } from "node:url";

import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) },
  },
  test: {
    environment: "happy-dom",
    globals: true,
    setupFiles: ["./src/test-setup.ts"],
    // The generated client is not ours to test, and coverage over 6 000 generated lines
    // would report a number about openapi-typescript rather than about this application.
    coverage: { exclude: ["src/api/generated/**", "**/*.config.ts"] },
    // `expectTypeOf` is **erased at runtime**. Without this block a type assertion is a
    // test that can never fail — proven by asserting `exposure_years` is a `number` and
    // watching it pass. `*.test-d.ts` files are type-checked, not executed.
    typecheck: {
      enabled: true,
      include: ["src/**/*.test-d.ts"],
      tsconfig: "./tsconfig.app.json",
    },
  },
});
