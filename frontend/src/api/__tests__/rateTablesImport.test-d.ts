import { expectTypeOf, it } from "vitest";

import type { operations } from "../generated/schema";
import { confirmImport, previewImport } from "../rateTables";

type Import = operations["import_rate_table_api_v1_rate_tables__slug___version__import_post"]["responses"];

// GUARDs (green before the switch: the composed type is structurally equal to the generated one).
it("previewImport resolves to the 200 ImportPreview", () => {
  expectTypeOf(previewImport).returns.resolves.toEqualTypeOf<Import[200]["content"]["application/json"]>();
});

it("confirmImport resolves to the 201 RateTableVersion", () => {
  expectTypeOf(confirmImport).returns.resolves.toEqualTypeOf<Import[201]["content"]["application/json"]>();
});
