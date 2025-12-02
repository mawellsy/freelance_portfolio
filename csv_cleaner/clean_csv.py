import pandas as pd
import re
import unicodedata


# ---------- 1. Read original messy file ----------

INPUT_FILE = "messy_data.csv"
OUTPUT_FILE = "clean_data.csv"

df = pd.read_csv(INPUT_FILE)


# ---------- 2. Normalize column names ----------

# - remove weird non-breaking spaces
# - strip spaces
# - lowercase
# - replace non-alphanumeric with '_'
# - collapse multiple '_' and strip leading/trailing '_'
df.columns = (
    df.columns
      .str.replace("\xa0", " ", regex=False)
      .str.strip()
      .str.lower()
      .str.replace(r"[^0-9a-zA-Z]+", "_", regex=True)
      .str.replace(r"_+", "_", regex=True)
      .str.strip("_")
)

# Example result:
# rank, peak, all_time_peak, actual_gross, adjusted_gross_in_2022_dollars,
# artist, tour_title, year_s, shows, average_gross, ref


# ---------- 3. Helpers ----------

def clean_money(s):
    """
    Convert strings like '$780,000,000[4]' -> 780000000.0
    Returns pandas.NA for empty/invalid values.
    """
    if pd.isna(s):
        return pd.NA
    s = str(s)
    # remove $ and commas
    s = re.sub(r"\$|,", "", s)
    # remove [4], [15][a], etc
    s = re.sub(r"\[.*?\]", "", s)
    s = s.strip()
    return float(s) if s else pd.NA


def clean_int(s):
    """
    Extract an integer from messy values like:
    '7[2]', '2[10]', '1970-01-01 00:00:00.000000056'
    Returns pandas.NA if no digits.
    """
    if pd.isna(s):
        return pd.NA
    s = str(s)
    # prefer the last group of digits
    m = re.search(r"(\d+)$", s)
    if m:
        return int(m.group(1))
    digits = re.findall(r"\d+", s)
    if digits:
        return int(digits[0])
    return pd.NA


def clean_title(text):
    """
    Remove bracket refs and weird unicode symbols from titles.
    Keeps letters, digits, spaces, and basic punctuation like - & , . ' !
    """
    if pd.isna(text):
        return text
    text = str(text)
    # remove [4], [15][a], etc.
    text = re.sub(r"\[.*?\]", "", text)
    # remove weird chars: anything not word, space, or basic punctuation
    text = re.sub(r"[^\w\s\-&.,'!?]", "", text)
    return text.strip()


def strip_bracket_refs(text):
    """
    Remove [4], [15][a] style bracketed references from strings.
    """
    if pd.isna(text):
        return text
    text = str(text)
    return re.sub(r"\[.*?\]", "", text).strip()


# ---------- 4. Clean currency / numeric columns ----------

# any column with 'gross' in its name is treated as money
money_cols = [c for c in df.columns if "gross" in c]
for col in money_cols:
    df[col] = df[col].apply(clean_money)

# integer-like columns
int_cols = ["rank", "peak", "all_time_peak", "shows"]
for col in int_cols:
    if col in df.columns:
        df[col] = df[col].apply(clean_int)

# optional: clean ref column to remove brackets and keep just number
if "ref" in df.columns or "ref_" in df.columns:
    ref_col = "ref" if "ref" in df.columns else "ref_"
    df[ref_col] = df[ref_col].apply(strip_bracket_refs)


# ---------- 5. Clean text columns (titles etc.) ----------

if "tour_title" in df.columns:
    df["tour_title"] = df["tour_title"].apply(clean_title)

if "artist" in df.columns:
    df["artist"] = df["artist"].apply(clean_title)



# ---------- 6. Optional: sort by rank ----------

if "rank" in df.columns:
    df = df.sort_values("rank")


# ---------- 7. Save cleaned CSV & show preview ----------

df.to_csv(OUTPUT_FILE, index=False)

print(f"Saved cleaned file to {OUTPUT_FILE}")
print(df.head())