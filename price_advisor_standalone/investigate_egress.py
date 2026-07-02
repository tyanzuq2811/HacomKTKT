import pandas as pd
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv(r'runtime\hacom_price_refs.csv')
print(f"Columns: {list(df.columns)}")
print(f"Total rows: {len(df)}")

# Search for banned words in ALL columns
pattern = re.compile(r'hacom|nhà thầu|nha thau|project|contractor|mall|dự án|du an', re.IGNORECASE)

matches = []
for idx, row in df.iterrows():
    for col in df.columns:
        val = str(row[col])
        found = pattern.findall(val)
        if found:
            matches.append((idx, col, found, val[:100]))

print(f"\nTotal cells matching banned words: {len(matches)}")
for m in matches[:20]:
    print(f"  Row {m[0]}, Column '{m[1]}': matched {m[2]} => '{m[3]}'")

# Now specifically search for "Bồn hóa chất" and "Hộp giấy vệ sinh"
print("\n=== Searching for 'Bồn hóa chất' ===")
mask1 = df.apply(lambda row: row.astype(str).str.contains('Bồn hóa chất', case=False, na=False).any(), axis=1)
if mask1.sum() > 0:
    for idx, row in df[mask1].iterrows():
        for col in df.columns:
            val = str(row[col])
            if pattern.search(val):
                print(f"  Row {idx}, Col '{col}': {val[:120]}")

print("\n=== Searching for 'Hộp giấy vệ sinh' ===")
mask2 = df.apply(lambda row: row.astype(str).str.contains('Hộp giấy vệ sinh', case=False, na=False).any(), axis=1)
if mask2.sum() > 0:
    for idx, row in df[mask2].iterrows():
        for col in df.columns:
            val = str(row[col])
            if pattern.search(val):
                print(f"  Row {idx}, Col '{col}': {val[:120]}")
