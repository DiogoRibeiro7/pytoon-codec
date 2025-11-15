from __future__ import annotations

from __future__ import annotations

import json
import os
from pathlib import Path
from time import perf_counter

import pytest

from benchmarks.generate_payloads import generate_metrics
from pytoon_codec import ToonCodec

BASELINE_FILE = Path(__file__).with_name("perf_baseline.json")
BASELINE_FACTOR = 1.25


def _load_baseline() -> float:
    override = os.environ.get("PYTOON_PERF_BASELINE_PATH")
    path = Path(override) if override else BASELINE_FILE
    data = json.loads(path.read_text())
    return float(data["metrics_roundtrip_seconds"])


@pytest.mark.regression
def test_metrics_roundtrip_smoke_under_two_seconds() -> None:
    codec = ToonCodec()
    payload = generate_metrics(1_000)

    start = perf_counter()
    toon = codec.encode(payload)
    decoded = codec.decode(toon)
    elapsed = perf_counter() - start

    assert decoded == payload
    assert elapsed < 2.0, f"Encode+decode took {elapsed:.2f}s"

    baseline = _load_baseline()
    threshold = baseline * BASELINE_FACTOR
    assert elapsed <= threshold, (
        f"Encode+decode time {elapsed:.2f}s exceeded baseline {baseline:.2f}s"
    )
