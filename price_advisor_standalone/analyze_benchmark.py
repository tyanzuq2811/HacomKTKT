import json, sys
sys.stdout.reconfigure(encoding='utf-8')

d = json.load(open(r'd:\Intern_LAB\Million_Dolar_Rearch\HacomKTKT\price_advisor_standalone\wandb\run-20260630_210712-zejh45m3\files\media\table\benchmark_results_0_4e01beda8a71c7b50525.table.json', 'r', encoding='utf-8'))
rows = d['data']
# columns: 0=Mô tả, 1=Đơn vị, 2=Giá thực tế, 3=Gợi ý thấp, 4=Gợi ý cao, 5=Đúng khoảng?, 6=Latency, 7=Lập luận

errors = [r for r in rows if r[5] == False and r[3] == 0 and r[4] == 0]
false_range = [r for r in rows if r[5] == False and not (r[3] == 0 and r[4] == 0)]
true_range = [r for r in rows if r[5] == True]

print(f"=== BENCHMARK 300 - gemma-4-31b-it ===")
print(f"Total: {len(rows)}")
print(f"True range (correct): {len(true_range)} ({len(true_range)/len(rows)*100:.1f}%)")
print(f"False range (AI wrong): {len(false_range)} ({len(false_range)/len(rows)*100:.1f}%)")
print(f"Errors (API crash): {len(errors)} ({len(errors)/len(rows)*100:.1f}%)")
print()

# Analyze latency
lats = [r[6] for r in rows if r[6] > 0]
print(f"Latency: avg={sum(lats)/len(lats):.1f}s, min={min(lats):.1f}s, max={max(lats):.1f}s")
print()

# Error details
print("=== ERRORS (API fail) ===")
for r in errors:
    reason = r[7][:100] if r[7] else "N/A"
    print(f"  [{r[0][:50]}] => {reason}")
print()

# False range: check how many are edge cases (actual == price_low or price_high)
edge_cases = []
genuine_miss = []
for r in false_range:
    actual, low, high = r[2], r[3], r[4]
    if actual == low or actual == high or abs(actual - low) <= 2 or abs(actual - high) <= 2:
        edge_cases.append(r)
    else:
        genuine_miss.append(r)

print(f"=== FALSE RANGE BREAKDOWN ===")
print(f"  Edge cases (off by <=2 VND): {len(edge_cases)}")
print(f"  Genuine misses: {len(genuine_miss)}")
print()

print("=== GENUINE MISSES (top 30) ===")
for r in genuine_miss[:30]:
    actual, low, high = r[2], r[3], r[4]
    if actual < low:
        miss_pct = (low - actual) / actual * 100
        direction = "UNDER"
    else:
        miss_pct = (actual - high) / actual * 100
        direction = "OVER"
    print(f"  {r[0][:55]:55s} | actual={actual:>12,} | range={low:>12,}-{high:>12,} | {direction} by {miss_pct:.1f}%")
