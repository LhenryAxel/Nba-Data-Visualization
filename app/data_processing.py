import pandas as pd


def load_csv(filepath: str) -> pd.DataFrame:
    """Load a CSV file and return a DataFrame."""
    df = pd.read_csv(filepath)
    print(f"CSV loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def load_json(filepath: str) -> pd.DataFrame:
    """Load a JSON file and return a DataFrame."""
    df = pd.read_json(filepath)
    print(f"JSON loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the NBA dataset."""
    initial_len = len(df)

    df = df.drop_duplicates()

    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    df = df.dropna(subset=["player_name"])

    if "college" in df.columns:
        df["college"] = df["college"].fillna("Unknown")

    if "draft_round" in df.columns:
        df["draft_round"] = pd.to_numeric(df["draft_round"], errors="coerce")

    if "draft_number" in df.columns:
        df["draft_number"] = pd.to_numeric(df["draft_number"], errors="coerce")

    if "ts_pct" in df.columns:
        df = df[(df["ts_pct"] >= 0) & (df["ts_pct"] <= 1)]

    if "usg_pct" in df.columns:
        df = df[(df["usg_pct"] > 0) & (df["usg_pct"] <= 1)]

    if "gp" in df.columns:
        df = df[df["gp"] > 10]

    print(f"Removed rows: {initial_len - len(df)}")
    return df.reset_index(drop=True)


def enrich_data(df: pd.DataFrame) -> pd.DataFrame:
    """Create calculated columns for better analysis."""
    df["pts_per_game_level"] = pd.cut(
        df["pts"],
        bins=[0, 5, 10, 20, 50],
        labels=["Low", "Role Player", "Good Scorer", "Elite Scorer"],
        include_lowest=True
    )

    df["age_group"] = pd.cut(
        df["age"],
        bins=[18, 23, 28, 33, 50],
        labels=["Young", "Prime", "Experienced", "Veteran"],
        include_lowest=True
    )

    df["reb_per_cm"] = df["reb"] / df["player_height"]
    df["ast_to_pts_ratio"] = df["ast"] / df["pts"].replace(0, 1)

    return df