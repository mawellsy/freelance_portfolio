import argparse
import re
import unicodedata
from pathlib import Path

import pandas as pd


# ---------- Helpers: cleaning functions ----------

def normalize_column_names(columns):
    """
    Normalize column names:
    - remove non-breaking spaces
    - strip spaces
    - lowercase
    - replace non-alphanumeric with '_'
    - collapse multiple '_' and strip leading/trailing '_'
    """
    cols = (
        columns
        .str.replace("\xa0", " ", regex=False)
        .str.strip()
        .str.lower()
        .str.replace(r"[^0-9a-zA-Z]+", "_", regex=True)
        .str.replace(r"_+", "_", regex=True)
        .str.strip("_")
    )
    return cols


def clean_money(value):
    """
    Convert strings like '$780,000,000[4]' -> 780000000.0
    Returns pandas.NA for empty/invalid values.
    """
    if pd.isna(value):
        return pd.NA
    s = str(value)
    s = re.sub(r"\$|,", "", s)       # remove $ and commas
    s = re.sub(r"\[.*?\]", "", s)    # remove [4], [15][a], etc
    s = s.strip()
    return float(s) if s else pd.NA


def clean_int(value):
    """
    Extract an integer from messy values like:
    '7[2]', '2[10]', '1970-01-01 00:00:00.000000056'
    Returns pandas.NA if no digits.
    """
    if pd.isna(value):
        return pd.NA
    s = str(value)
    # prefer the last group of digits
    m = re.search(r"(\d+)$", s)
    if m:
        return int(m.group(1))
    digits = re.findall(r"\d+", s)
    if digits:
        return int(digits[0])
    return pd.NA

def clean_ref(value):
    """
    Turn '[1]', '[15][a]' into just '1', '15'.
    Returns pandas.NA if there are no digits.
    """
    if pd.isna(value):
        return pd.NA
    s = str(value)
    m = re.search(r"(\d+)", s)
    return m.group(1) if m else pd.NA


def clean_text(value):
    """
    For text-like columns (titles, names):
    - remove bracket refs [4], [15][a]
    - drop weird unicode symbols (†, ‡, etc.)
    - keep letters, digits, spaces, and basic punctuation
    """
    if pd.isna(value):
        return value
    text = str(value)
    # remove [4], [15][a] etc.
    text = re.sub(r"\[.*?\]", "", text)
    # remove symbol category chars
    cleaned = "".join(
        ch for ch in text
        if unicodedata.category(ch)[0] != "S"
    )
    # optionally, you can restrict to a safe charset:
    cleaned = re.sub(r"[^\w\s\-&.,'!?]", "", cleaned)
    return cleaned.strip()


# ---------- Core cleaning pipeline ----------

def clean_csv(
    input_path: Path,
    output_path: Path,
    money_cols=None,
    int_cols=None,
    text_cols=None,
):
    money_cols = money_cols or []
    int_cols = int_cols or []
    text_cols = text_cols or []

    print(f"Reading: {input_path}")
    df = pd.read_csv(input_path)

    original_shape = df.shape

    # 1. Normalize column names
    df.columns = normalize_column_names(df.columns)

    # map user-given names (which should already match normalized form)
    normalized_cols = set(df.columns)

    money_cols = [c for c in money_cols if c in normalized_cols]
    int_cols = [c for c in int_cols if c in normalized_cols]
    text_cols = [c for c in text_cols if c in normalized_cols]

    # 2. Clean numeric money columns
    for col in money_cols:
        df[col] = df[col].apply(clean_money)

    # 3. Clean integer-like columns
    for col in int_cols:
        df[col] = df[col].apply(clean_int)

    # 4. Clean text-like columns
    for col in text_cols:
        df[col] = df[col].apply(clean_text)

    # 5. Optional: sort by rank if we have it
    if "rank" in df.columns:
        df = df.sort_values("rank")

        # Clean ref column if present
    if "ref" in df.columns:
        df["ref"] = df["ref"].apply(clean_ref)

    # 6. Save
    output_path = output_path.with_suffix(".csv")
    df.to_csv(output_path, index=False)

    # 7. Small report
    print("\n=== Cleaning report ===")
    print(f"Rows, columns (before): {original_shape}")
    print(f"Rows, columns (after) : {df.shape}")
    print(f"Money columns cleaned : {money_cols or 'None'}")
    print(f"Int columns cleaned   : {int_cols or 'None'}")
    print(f"Text columns cleaned  : {text_cols or 'None'}")
    print(f"\nPreview (head):")
    print(df.head())
    print(f"\nSaved cleaned file to: {output_path.resolve()}")


# ---------- CLI interface ----------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generic CSV cleaner using pandas."
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to input CSV file.",
    )
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Path to output CSV file (CSV extension will be added if missing).",
    )
    parser.add_argument(
        "--money-cols",
        help="Comma-separated list of column names to treat as money.",
    )
    parser.add_argument(
        "--int-cols",
        help="Comma-separated list of column names to treat as integers.",
    )
    parser.add_argument(
        "--text-cols",
        help="Comma-separated list of column names to clean as text.",
    )
    return parser.parse_args()


def parse_list(arg_value):
    if not arg_value:
        return []
    # split by comma and strip spaces
    return [item.strip().lower() for item in arg_value.split(",") if item.strip()]


def main():
    args = parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    money_cols = parse_list(args.money_cols)
    int_cols = parse_list(args.int_cols)
    text_cols = parse_list(args.text_cols)

    clean_csv(
        input_path=input_path,
        output_path=output_path,
        money_cols=money_cols,
        int_cols=int_cols,
        text_cols=text_cols,
    )


if __name__ == "__main__":
    main()
