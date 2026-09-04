"""Test fixture and helper for d4 slug extraction from YAML front matter."""

from __future__ import annotations

import re
from pathlib import Path


def extract_title_from_yaml_header(text: str) -> str | None:
    """Extract the title field value from a YAML front-matter header.

    The header must be at the start of the file and contain a `title:` line.
    Returns None if no title is found.
    """
    # Match lines starting with "title:" at the beginning of the file
    match = re.search(r"^title:\s+(.+?)$", text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def test_extract_title_from_yaml():
    """Test the title extraction function."""
    yaml_header = """---
id: PL-00066
title: wf-01 Something Important
status: active
---

Body content here.
"""
    title = extract_title_from_yaml_header(yaml_header)
    assert title == "wf-01 Something Important"


def test_extract_title_without_quotes():
    """Test extraction when title has no quotes."""
    yaml_header = "title: My Test Title\nstatus: active\n"
    title = extract_title_from_yaml_header(yaml_header)
    assert title == "My Test Title"


def test_extract_title_with_em_dash():
    """Test extraction with em dash in title."""
    yaml_header = "title: PL-00066 — Test Plan\nid: PL-00066\n"
    title = extract_title_from_yaml_header(yaml_header)
    assert title == "PL-00066 — Test Plan"
