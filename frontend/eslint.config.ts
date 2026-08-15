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
);
