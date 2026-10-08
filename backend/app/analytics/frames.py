"""Convert analytics records into the stable DataFrame shapes used by analyses."""

from collections.abc import Sequence

import pandas as pd


def build_frame(records: Sequence[dict], columns: list[str]) -> pd.DataFrame:
    return pd.DataFrame(records, columns=columns)
