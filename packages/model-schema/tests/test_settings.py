"""`07` §3.8 FR-446's four layers: the order a `SettingSource` declares (`RL-1311` item 2)."""

from __future__ import annotations

import pytest

from model_schema.settings import SettingSource


@pytest.mark.req("FR-446")
def test_setting_source_orders_the_four_layers_highest_precedence_first() -> None:
    assert list(SettingSource) == [
        SettingSource.ENV,
        SettingSource.ENVIRONMENT_SETTING,
        SettingSource.WORKSPACE,
        SettingSource.DEFAULT,
    ]
    assert SettingSource.ENVIRONMENT_SETTING.value == "environment_setting"
