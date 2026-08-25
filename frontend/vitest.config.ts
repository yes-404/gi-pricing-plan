import { fileURLToPath } from "node:url";

import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) },
  },
  // `builtinObjectives.test.ts` reads `pricing_core/modelling/gbm.py` through Vite's
  // `?raw`, and that file is outside `frontend/`, which Vite denies by default. The
  // allow-list is **narrowed to that one directory** rather than opened to the repository
  // root: the guard needs one file, and a test suite that can read anything on disk is a
  // different thing from one that can read a named module's source.
  //
  // Listing `allow` at all replaces Vite's default, so the frontend root is named here
  // too — without it every ordinary import under `src/` would be denied.
  server: {
    fs: {
      allow: [
        fileURLToPath(new URL("./", import.meta.url)),
        fileURLToPath(
          new URL("../packages/pricing-core/src/pricing_core/modelling", import.meta.url),
        ),
        // OQ-MODEL-37's second surface: `FITTABLE_OBJECTIVE_STATUSES` is a *subset* of a
        // generated enum, which no field type can express, so the divergence test is the
        // whole of the interim rather than a stopgap beside a better fix.
        fileURLToPath(
          new URL("../packages/model-schema/src/model_schema", import.meta.url),
        ),
      ],
    },
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
