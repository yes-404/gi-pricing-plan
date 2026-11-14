import js from "@eslint/js";
import pluginVue from "eslint-plugin-vue";
import { defineConfigWithVueTs, vueTsConfigs } from "@vue/eslint-config-typescript";

export default defineConfigWithVueTs(
  {
    name: "app/files",
    files: ["**/*.{ts,mts,tsx,vue}"],
  },
  {
    // Generated from `model-schema` and never edited (`CLAUDE.md` §2). Linting it to our
    // rules would produce churn on every regeneration and break that promise.
    name: "app/ignores",
    ignores: ["dist/**", "coverage/**", "src/api/generated/**"],
  },
  js.configs.recommended,
  pluginVue.configs["flat/recommended"],
  vueTsConfigs.recommended,
  {
    // `00` FR-14: the SPA is a pure client of the documented OpenAPI surface. Every request
    // goes through `src/api/` (the one fetch seam, `client.ts`, and the generated types);
    // nothing else may call `fetch`, import `axios`, or write an `/api/v1` path. Lives in the
    // frontend toolchain, not a pytest scan, because `frontend.yml` is path-filtered and a
    // frontend-only PR is exactly the one that could add a raw call.
    name: "app/pure-api-client",
    files: ["src/**/*.{ts,mts,tsx,vue}"],
    ignores: ["src/api/**", "**/__tests__/**", "**/*.test.ts"],
    rules: {
      "no-restricted-globals": [
        "error",
        { name: "fetch", message: "Call the API through src/api (FR-14); never fetch directly." },
      ],
      "no-restricted-imports": [
        "error",
        { paths: [{ name: "axios", message: "Call the API through src/api (FR-14)." }] },
      ],
      "no-restricted-syntax": [
        "error",
        {
          selector: "Literal[value=/^\\/api\\/v1/]",
          message: "An /api/v1 path belongs in src/api (FR-14).",
        },
        {
          selector: "TemplateElement[value.raw=/^\\/api\\/v1/]",
          message: "An /api/v1 path belongs in src/api (FR-14).",
        },
      ],
    },
  },
);
