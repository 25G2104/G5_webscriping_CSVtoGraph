"""
    pip install pandas matplotlib

    このスクリプトと同じフォルダに 2015.csv〜2025.csv を配置してください。

"""

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 日本語フォント設定
def set_japanese_font():
    candidates = [
        "Hiragino Sans",
        "Hiragino Kaku Gothic ProN",
        "IPAexGothic",
        "Noto Sans CJK JP",
        "Yu Gothic",
    ]
    available = {f.name for f in fm.fontManager.ttflist}
    for font in candidates:
        if font in available:
            plt.rcParams["font.family"] = font
            return
    plt.rcParams["font.family"] = "sans-serif"

set_japanese_font()
plt.rcParams["axes.unicode_minus"] = False

# CSVファイル読み込み
data_dir = os.path.dirname(os.path.abspath(__file__))
csv_files = sorted(glob.glob(os.path.join(data_dir, "[0-9][0-9][0-9][0-9].csv")))

frames = []
for path in csv_files:
    year = int(os.path.basename(path).replace(".csv", ""))
    df = pd.read_csv(path, encoding="utf-8-sig")
    df["年"] = year
    frames.append(df)

all_data = pd.concat(frames, ignore_index=True)

# 視聴回数を数値に変換（カンマ除去）
all_data["視聴回数"] = (
    all_data["視聴回数"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .str.replace("，", "", regex=False)
    .pipe(pd.to_numeric, errors="coerce")
)

# 検索キーワード × 年 で集計
grouped = (
    all_data.groupby(["検索キーワード", "年"])["視聴回数"]
    .agg(合計視聴回数="sum", 平均視聴回数="mean", 動画本数="count")
    .reset_index()
)

keywords = grouped["検索キーワード"].unique()
years = sorted(grouped["年"].unique())

# ---- グラフ描画 ----
fig, axes = plt.subplots(2, 1, figsize=(14, 10))
fig.suptitle("検索キーワード別 年別視聴回数推移", fontsize=16, fontweight="bold")

colors = plt.cm.tab10.colors

# 上段: 合計視聴回数（折れ線）
ax1 = axes[0]
for i, kw in enumerate(keywords):
    sub = grouped[grouped["検索キーワード"] == kw].sort_values("年")
    ax1.plot(sub["年"], sub["合計視聴回数"] / 1_000_000, marker="o", label=kw, color=colors[i % len(colors)])
    for _, row in sub.iterrows():
        ax1.annotate(
            f"{row['合計視聴回数'] / 1_000_000:.1f}M",
            (row["年"], row["合計視聴回数"] / 1_000_000),
            textcoords="offset points", xytext=(0, 6), fontsize=7, ha="center",
        )

ax1.set_title("合計視聴回数（単位: 百万回）", fontsize=12)
ax1.set_xlabel("年")
ax1.set_ylabel("視聴回数（百万回）")
ax1.set_xticks(years)
ax1.legend()
ax1.grid(axis="y", linestyle="--", alpha=0.5)

# 下段: 平均視聴回数（棒グラフ）
ax2 = axes[1]
width = 0.8 / len(keywords)
x = range(len(years))

for i, kw in enumerate(keywords):
    sub = grouped[grouped["検索キーワード"] == kw].sort_values("年")
    sub = sub.set_index("年").reindex(years, fill_value=0).reset_index()
    offset = (i - (len(keywords) - 1) / 2) * width
    bars = ax2.bar(
        [xi + offset for xi in x],
        sub["平均視聴回数"] / 10_000,
        width=width,
        label=kw,
        color=colors[i % len(colors)],
        alpha=0.85,
    )

ax2.set_title("1動画あたり平均視聴回数（単位: 万回）", fontsize=12)
ax2.set_xlabel("年")
ax2.set_ylabel("平均視聴回数（万回）")
ax2.set_xticks(list(x))
ax2.set_xticklabels(years)
ax2.legend()
ax2.grid(axis="y", linestyle="--", alpha=0.5)

plt.tight_layout()
output_path = os.path.join(data_dir, "youtube_analysis.png")
plt.savefig(output_path, dpi=150, bbox_inches="tight")
print(f"グラフを保存しました: {output_path}")

# 集計結果をCSV出力
summary_path = os.path.join(data_dir, "youtube_summary.csv")
grouped.to_csv(summary_path, index=False, encoding="utf-8-sig")
print(f"集計データを保存しました: {summary_path}")

