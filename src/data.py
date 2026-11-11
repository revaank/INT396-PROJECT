"""Loading and validation helpers for the Dataful TB dataset."""
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "dataful_20833" / "year-state-sector-and-risk-factor-wise-cases-of-tb.csv"
METADATA_PATH = DATA_PATH.with_name("metadata.csv")
ALL_INDIA_LABELS = {"all india", "india"}


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load rows while retaining blank values as missing, never as zero."""
    if not path.exists():
        raise FileNotFoundError(f"TB dataset not found: {path}")
    data = pd.read_csv(path)
    required = {"year", "state", "risk_factor", "parameter", "sector", "value", "unit"}
    missing_columns = required.difference(data.columns)
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {', '.join(sorted(missing_columns))}")
    data["year"] = pd.to_numeric(data["year"], errors="coerce").astype("Int64")
    data["value"] = pd.to_numeric(data["value"], errors="coerce")
    return data


def regional_data(data: pd.DataFrame) -> pd.DataFrame:
    """Return state/UT records only; the national aggregate is not a region."""
    labels = data["state"].astype(str).str.strip().str.casefold()
    return data.loc[~labels.isin(ALL_INDIA_LABELS)].copy()


def get_quality_summary(data: pd.DataFrame) -> dict:
    regional = regional_data(data)
    key = ["year", "state", "risk_factor", "parameter", "sector"]
    return {
        "rows": int(len(data)),
        "regions": int(regional["state"].nunique()),
        "years": sorted(int(y) for y in data["year"].dropna().unique()),
        "missing_values": int(data["value"].isna().sum()),
        "blank_notes": int(data["note"].isna().sum()) if "note" in data.columns else 0,
        "duplicate_keys": int(data.duplicated(key, keep=False).sum()),
        "negative_values": int((data["value"] < 0).sum()),
        "units": sorted(data["unit"].dropna().astype(str).unique().tolist()),
    }


def available_values(data: pd.DataFrame, column: str, **filters) -> list:
    view = data
    for key, value in filters.items():
        view = view.loc[view[key] == value]
    return sorted(view[column].dropna().unique().tolist())


def regional_feature_matrix(data: pd.DataFrame, year: int, risk_factor: str, sector: str):
    """Pivot comparable parameters into state rows; missing cells remain missing."""
    subset = regional_data(data)
    subset = subset.loc[
        (subset["year"] == year)
        & (subset["risk_factor"] == risk_factor)
        & (subset["sector"] == sector)
    ]
    matrix = subset.pivot_table(index="state", columns="parameter", values="value", aggfunc="first")
    matrix = matrix.dropna(axis=1, how="all")
    complete = matrix.dropna(axis=0, how="any")
    return matrix, complete
