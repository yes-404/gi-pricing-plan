import { expectTypeOf } from "vitest";

import type { EbmFitResult, GbmFitResult, Model } from "../models";
import { ebmFit, gbmFit } from "../models";

// A runtime assertion cannot check a narrowing. These belong in a `.test-d.ts`, where
// vitest's typecheck runs them, and nowhere else: `expectTypeOf` is erased at runtime, so
// in a `.test.ts` it is a line that can never fail.
expectTypeOf(gbmFit).returns.toEqualTypeOf<GbmFitResult | null>();
expectTypeOf(ebmFit).returns.toEqualTypeOf<EbmFitResult | null>();
expectTypeOf<Model["fit_result"]>().toBeNullable();
