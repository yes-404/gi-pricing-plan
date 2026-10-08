// The twelve-step `valid_algorithm()` of backend/tests/test_rating_algorithms.py (the server-side fixture), typed.
import type { RatingAlgorithmDraft } from "@/api/ratingAlgorithms";

export const valid: RatingAlgorithmDraft = {
  "slug": "motor-gb",
  "version": 1,
  "input_contract": [
    {
      "name": "driver_age",
      "type": "int",
      "nullable": false,
      "min": 17,
      "max": 99
    },
    {
      "name": "effective_date",
      "type": "date",
      "nullable": false
    },
    {
      "name": "channel",
      "type": "enum",
      "domain": [
        "direct",
        "broker"
      ],
      "nullable": false
    }
  ],
  "outputs": [
    {
      "name": "payable_premium_minor",
      "type": "money_minor",
      "required": true
    }
  ],
  "steps": [
    {
      "step_id": "s_in_age",
      "type": "input",
      "label": "Driver age",
      "input_name": "driver_age",
      "on_missing": "error",
      "produces": "driver_age"
    },
    {
      "step_id": "s_in_eff",
      "type": "input",
      "label": "Effective date",
      "input_name": "effective_date",
      "on_missing": "error",
      "produces": "effective_date"
    },
    {
      "step_id": "s_in_channel",
      "type": "input",
      "label": "Channel",
      "input_name": "channel",
      "on_missing": "error",
      "produces": "channel"
    },
    {
      "step_id": "s_area",
      "type": "lookup",
      "label": "Area",
      "reference_table_ref": "reference_table:ons-postcode-directory@7",
      "key_expr": [
        "channel"
      ],
      "as_at": "effective_date",
      "on_miss": "error",
      "consumes": [
        "channel",
        "effective_date"
      ],
      "produces": "rating_area"
    },
    {
      "step_id": "s_rp",
      "type": "model_call",
      "label": "Risk premium",
      "model_ref": "model:motor-ad-frequency@7",
      "mode": "exact",
      "feature_map": {
        "driver_age": "driver_age",
        "rating_area": "rating_area"
      },
      "consumes": [
        "driver_age",
        "rating_area"
      ],
      "produces": [
        "risk_premium_minor",
        "peril_risk_premium"
      ]
    },
    {
      "step_id": "s_expense",
      "type": "table",
      "label": "Expense",
      "rate_table_ref": "rate_table:motor-expense@3",
      "key_expr": [
        "channel"
      ],
      "on_miss": "default",
      "consumes": [
        "channel"
      ],
      "produces": "expense_factor"
    },
    {
      "step_id": "s_office",
      "type": "expression",
      "label": "Office premium",
      "expr": "risk_premium_minor * expense_factor",
      "result_type": "money_minor",
      "consumes": [
        "risk_premium_minor",
        "expense_factor"
      ],
      "produces": "office_premium_minor"
    },
    {
      "step_id": "s_minprem",
      "type": "constraint",
      "label": "Min premium",
      "condition": "office_premium_minor >= 100",
      "on_violation": "clamp",
      "clamp_bounds": {
        "min": "100"
      },
      "reason_code": "MIN_PREMIUM_APPLIED",
      "consumes": [
        "office_premium_minor"
      ],
      "produces": "office_premium_minor"
    },
    {
      "step_id": "s_out_office",
      "type": "output",
      "label": "Office premium",
      "output_name": "office_premium_minor",
      "rounding": {
        "mode": "half_even",
        "dp": 0
      },
      "consumes": [
        "office_premium_minor"
      ]
    },
    {
      "step_id": "s_payable",
      "type": "expression",
      "label": "Payable premium value",
      "expr": "office_premium_minor * 1",
      "result_type": "money_minor",
      "consumes": [
        "office_premium_minor"
      ],
      "produces": "payable_value"
    },
    {
      "step_id": "s_out",
      "type": "output",
      "label": "Payable premium",
      "output_name": "payable_premium_minor",
      "rounding": {
        "mode": "half_even",
        "dp": 0
      },
      "consumes": [
        "payable_value"
      ]
    }
  ],
  "sub_graphs": []
}
;
