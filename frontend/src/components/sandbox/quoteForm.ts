import type { RatingAlgorithm } from "@/api/ratingAlgorithms";
import type { QuotePurpose } from "@/api/score";

/** One declared Rating Input (03 FR-213), as the algorithm read returns it. */
export type ContractField = RatingAlgorithm["input_contract"][number];

/** What the form holds per field: a text box's string, or a checkbox's boolean. */
export type RawValue = string | boolean;

/** What the form emits on a valid submit: the typed inputs and the Quote Context's own two fields. */
export interface QuoteFormSubmit {
  readonly inputs: Record<string, unknown>;
  readonly purpose: QuotePurpose;
  readonly effective_date: string;
}

export interface BuiltInputs {
  /** The typed `inputs` object of the Quote Context; a blank nullable field is `null`. */
  readonly inputs: Record<string, unknown>;
  /** Field name to a message, for what could not be typed. Empty means submittable. */
  readonly problems: Record<string, string>;
}

const INTEGER = /^-?\d+$/;
const DECIMAL = /^-?\d+(\.\d+)?$/;

/**
 * Type each field's raw value, and nothing more (FR-213).
 *
 * The client reads a number as a number and refuses what is not one; it does **not** re-check
 * `min`, `max`, `pattern` or `domain`. The platform owns those rules and answers a violation
 * with `INPUT_CONTRACT_VIOLATION` naming the field (FR-255), which the sandbox shows
 * verbatim. A second copy here would be a rule defined twice.
 *
 * A `decimal` goes as a JSON number because the contract check accepts `int`, `float` or
 * `Decimal` and refuses a string (`score.py` `_validate_inputs`). An input is not money
 * (money is `*_minor`, an integer), so this crosses no FR-10 line.
 */
export function buildInputs(
  fields: readonly ContractField[],
  raw: Readonly<Record<string, RawValue | undefined>>,
): BuiltInputs {
  const inputs: Record<string, unknown> = {};
  const problems: Record<string, string> = {};
  for (const field of fields) {
    const value = raw[field.name];
    if (field.type === "bool") {
      inputs[field.name] = value === true;
      continue;
    }
    const text = typeof value === "string" ? value.trim() : "";
    if (text === "") {
      if (field.nullable) inputs[field.name] = null;
      else problems[field.name] = "Required";
      continue;
    }
    if (field.type === "int") {
      if (INTEGER.test(text) && Number.isSafeInteger(Number(text))) inputs[field.name] = Number(text);
      else problems[field.name] = "Enter a whole number";
    } else if (field.type === "decimal") {
      if (DECIMAL.test(text) && Number.isFinite(Number(text))) inputs[field.name] = Number(text);
      else problems[field.name] = "Enter a number";
    } else {
      inputs[field.name] = text;
    }
  }
  return { inputs, problems };
}
