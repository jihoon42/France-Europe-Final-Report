# -*- coding: utf-8 -*-
"""
EU 공간 불평등 — 심화 분석 (재현 가능)
  1) σ-수렴: 인구가중 log(1인당GDP) 표준편차의 추이
  2) 국가 내 발산의 국가별 기여: 2024년 within-Theil 성분을 국가별로 분해 → 프랑스 최대
  3) 일드프랑스(FR10) vs 프랑스 나머지 상대비 추이
입력: eu_nuts2_panel_clean.csv, eu_nuts2_pop.csv (동일 폴더)
출력: fig5_within_by_country.png  + 콘솔 수치
출처: Eurostat nama_10r_2gdp, demo_r_pjangrp3. 저자 계산.
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
plt.rcParams.update({"figure.dpi": 130, "font.size": 11, "axes.grid": True,
                     "grid.alpha": .25, "axes.spines.top": False, "axes.spines.right": False})

P = pd.read_csv(os.path.join(HERE, "eu_nuts2_panel_clean.csv")).pivot_table(
        index="code", columns="year", values="gdp_pc_pps")
ctry = pd.Series(P.index.str[:2], index=P.index)
w = pd.read_csv(os.path.join(HERE, "eu_nuts2_pop.csv")).set_index("code")["pop"].reindex(P.index)
w = w.fillna(w.median())
YEARS = [y for y in P.columns if 2000 <= y <= 2024]

# 1) σ-수렴 (인구가중 log GDP 표준편차)
def wstd(y, wt):
    m = np.average(y, weights=wt)
    return np.sqrt(np.average((y - m) ** 2, weights=wt))
sigma = {yr: wstd(np.log(P[yr].values), w.values) for yr in YEARS}
print(f"[σ-수렴] 인구가중 log GDP 표준편차: {YEARS[0]} {sigma[YEARS[0]]:.3f} → "
      f"{YEARS[-1]} {sigma[YEARS[-1]]:.3f}  ({(sigma[YEARS[-1]]/sigma[YEARS[0]]-1)*100:+.0f}%)")

# 2) 국가 내 발산의 국가별 기여 (인구가중 within-Theil 성분), 2024
def within_contrib(yr):
    y = P[yr].values; inc = w.values * y; Y = inc.sum()
    out = {}
    for g in np.unique(ctry.values):
        m = ctry.values == g
        if m.sum() < 2:      # 단일 NUTS-2 국가는 국가 내 분해 불가
            continue
        Sg = inc[m].sum() / Y
        Yg = inc[m].sum() / w.values[m].sum()
        sg = inc[m] / inc[m].sum()
        out[g] = Sg * np.sum(sg * np.log(y[m] / Yg))
    return pd.Series(out).sort_values(ascending=False)

wc = within_contrib(2024)
print("\n[국가 내 발산 기여 상위 8국, 2024]")
print((wc.head(8) * 1000).round(2).to_dict(), "(×10^-3)")

# 3) 일드프랑스 vs 프랑스 나머지
fr = P[P.index.str.startswith("FR")]
rest_idx = fr.drop("FR10").index
print("\n[일드프랑스(FR10) / 프랑스 나머지(인구가중 평균)]")
for yr in [2000, 2012, 2024]:
    ratio = fr.loc["FR10", yr] / np.average(fr.drop("FR10")[yr].values,
                                            weights=w.reindex(rest_idx).values)
    print(f"  {yr}: {ratio:.2f}배")

# ── 그림: 국가별 기여 막대 (상위 12, 프랑스 강조) ──
top = wc.head(12)
colors = ["#d62728" if c == "FR" else "#9ecae1" for c in top.index]
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(range(len(top)), top.values * 1000, color=colors, edgecolor="w", linewidth=.5)
ax.set_xticks(range(len(top))); ax.set_xticklabels(top.index)
ax.set_ylabel("Contribution to within-country Theil (×10$^{-3}$)")
ax.set_title("Who drives within-country divergence? (EU, 2024)\nFrance contributes the most",
             fontweight="bold", fontsize=12)
ax.text(0, top.values[0]*1000, "  FR", color="#d62728", va="bottom", fontweight="bold")
fig.text(0.012, -0.02, "Source: Eurostat nama_10r_2gdp + demo_r_pjangrp3 (pop-weighted). Author's calc.",
         fontsize=7, color="grey", style="italic")
fig.tight_layout(); fig.savefig(os.path.join(HERE, "fig5_within_by_country.png"), bbox_inches="tight")
print("\nsaved: fig5_within_by_country.png")
