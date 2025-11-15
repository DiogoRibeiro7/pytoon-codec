from __future__ import annotations

from time import perf_counter

import pytest

from benchmarks.generate_payloads import generate_metrics
from pytoon_codec import ToonCodec


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

    # TODO: Track historical timings and fail if the rolling baseline regresses by >25%.
