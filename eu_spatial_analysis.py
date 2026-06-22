# -*- coding: utf-8 -*-
"""
EU 공간 불평등 분석 — 재현 가능 파이프라인 (canonical)
「슬로다운의 사각지대」 5.4 (EU 결속정책 평가) · 8장 (비판)

입력 (이 폴더에 동봉):
  - eu_nuts2_panel_clean.csv : NUTS-2 1인당 GDP(PPS_EU27_2020_HAB), 2000-2024, 224지역·25국
  - eu_nuts2_pop.csv         : NUTS-2 인구(고정 가중치, 2019-2024 평균). Eurostat demo_r_pjangrp3.
                               (build_pop.py + pop_source.json 으로 재생성 가능)

산출:
  - fig1_theil_popweighted.png  (본문 헤드라인) / fig1_theil_unweighted.png (강건성 각주)
  - fig2_beta.png  fig3_distribution.png
  - 콘솔: 두 가중 방식 검증 표

핵심 결과 (둘 다 본 패널로 100% 재현)
  · 인구가중 : 국가間 -56% / 국가內 +5% / within비중 41%→62% / 교차 2007  ← 본문 헤드라인
  · 동일가중 : 국가間 -47% / 국가內 +12% / within비중 33%→51% / 교차 2023  ← robustness
  · β-수렴   : slope -0.017, R^2 0.46 (가중과 무관)
두 방식 모두 핵심 명제(국가間 수렴·국가內 발산·2024년 within 과반 역전)는 동일.
출처: Eurostat nama_10r_2gdp, demo_r_pjangrp3. 저자 계산.
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

HERE = os.path.dirname(os.path.abspath(__file__))

plt.rcParams.update({"figure.dpi": 130, "font.size": 11, "axes.grid": True,
                     "grid.alpha": .25, "axes.spines.top": False, "axes.spines.right": False})

WEST  = set('AT BE DE DK FI FR IE LU NL SE'.split())
SOUTH = set('EL ES IT PT CY MT'.split())
EAST  = set('BG CZ EE HR HU LV LT PL RO SK SI'.split())
def macro(c): return "West/North" if c in WEST else ("South" if c in SOUTH else "East (CEE)")

# ── 로드 ──────────────────────────────────────────────────────────────────────
d = pd.read_csv(os.path.join(HERE, "eu_nuts2_panel_clean.csv"))
P = d.pivot_table(index="code", columns="year", values="gdp_pc_pps")
ctry = pd.Series(P.index.str[:2], index=P.index)
YEARS = sorted(c for c in P.columns if 2000 <= c <= 2024)

w_unw = pd.Series(1.0, index=P.index)                                  # 동일가중
popfile = os.path.join(HERE, "eu_nuts2_pop.csv")
if os.path.exists(popfile):
    w_pop = pd.read_csv(popfile).set_index("code")["pop"].reindex(P.index)
    w_pop = w_pop.fillna(w_pop.median())
else:
    w_pop = None

# ── Theil-T 분해 (가중 일반형) ────────────────────────────────────────────────
def theil_decompose(y, groups, wt):
    inc = wt * y; Y = inc.sum(); ybar = Y / wt.sum(); s = inc / Y
    T = np.sum(s * np.log(y / ybar)); btw = wth = 0.0
    for g in np.unique(groups):
        m = groups == g
        Sg = inc[m].sum() / Y
        Yg = inc[m].sum() / wt[m].sum()
        sg = inc[m] / inc[m].sum()
        btw += Sg * np.log(Yg / ybar)
        wth += Sg * np.sum(sg * np.log(y[m] / Yg))
    return T, btw, wth

def theil_series(wt):
    rows = [(yr, *theil_decompose(P[yr].values, ctry.values, wt.values)) for yr in YEARS]
    return pd.DataFrame(rows, columns=["year", "total", "between", "within"]).set_index("year")

def report(name, T):
    chg = lambda c: (T[c].iloc[-1] / T[c].iloc[0] - 1) * 100
    sh  = lambda yr: T.within.loc[yr] / T.total.loc[yr] * 100
    cr  = T[T.within > T.between]
    cry = int(cr.index[0]) if len(cr) else None
    print(f"\n[{name}]  total {chg('total'):+.1f}% | between {chg('between'):+.1f}% | "
          f"within {chg('within'):+.1f}% | within비중 {sh(2000):.0f}%→{sh(2024):.0f}% | 교차 {cry}")
    return cry

# ── β-수렴 (가중 무관) ────────────────────────────────────────────────────────
y0, y1 = P[YEARS[0]], P[YEARS[-1]]
g_rate = np.log(y1 / y0) / (YEARS[-1] - YEARS[0]); x = np.log(y0)
b, a = np.polyfit(x, g_rate, 1)
r2 = 1 - np.sum((g_rate - (a + b * x)) ** 2) / np.sum((g_rate - g_rate.mean()) ** 2)

print("=" * 70)
print(f"패널: {P.shape[0]}개 NUTS-2 · {ctry.nunique()}개국 · {YEARS[0]}-{YEARS[-1]}")
T_unw = theil_series(w_unw); cry_unw = report("동일가중 (robustness)", T_unw)
if w_pop is not None:
    T_pop = theil_series(w_pop); cry_pop = report("인구가중 (본문 헤드라인)", T_pop)
print(f"\n[β-수렴]  slope={b:.4f}  R^2={r2:.3f}")
print("=" * 70)

# ── 그림 ──────────────────────────────────────────────────────────────────────
def fig_theil(T, cry, tag, title_w, src_w):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(T.index, T.total,   color="#222",    lw=2.4, label="Total inequality")
    ax.plot(T.index, T.between, color="#1f77b4", lw=2, ls="--", label="Between-country (convergence)")
    ax.plot(T.index, T.within,  color="#d62728", lw=2, ls="-.", label="Within-country (divergence)")
    if cry:
        ax.axvline(cry, color="grey", ls=":", lw=1)
        ax.text(cry + .3, ax.get_ylim()[1] * .5, f"crossover {cry}", color="grey", fontsize=8)
    ax.set_title(f"EU regional inequality, {title_w}\n(Theil decomposition, 224 NUTS-2 regions, 25 countries)",
                 fontweight="bold", fontsize=12)
    ax.set_xlabel("Year"); ax.set_ylabel("Theil T index"); ax.legend(frameon=False)
    fig.text(0.012, -0.02, src_w, fontsize=7, color="grey", style="italic")
    fig.tight_layout(); fig.savefig(os.path.join(HERE, f"fig1_theil_{tag}.png"), bbox_inches="tight")

SRC = "Source: Eurostat nama_10r_2gdp"
fig_theil(T_unw, cry_unw, "unweighted", "unweighted (each region = 1 vote)", SRC + ". Author's calc.")
if w_pop is not None:
    fig_theil(T_pop, cry_pop, "popweighted", "population-weighted", SRC + " + demo_r_pjangrp3 (2019-24 pop weights). Author's calc.")

# Fig 2 — β-수렴
fig, ax = plt.subplots(figsize=(8, 5))
cmap = {"West/North": "#1f77b4", "South": "#ff7f0e", "East (CEE)": "#2ca02c"}
mg = ctry.map(macro).values
for grp, col in cmap.items():
    m = mg == grp
    ax.scatter(x[m], g_rate[m], s=45, color=col, edgecolor="w", lw=.4, label=grp, zorder=3)
ax.plot(np.sort(x), a + b * np.sort(x), color="#d62728", lw=2, label=f"OLS: slope={b:.3f} (R^2={r2:.2f})")
ax.set_title("β-convergence, 2000–2024: poorer regions grew faster", fontweight="bold")
ax.set_xlabel("log GDP per capita (PPS), 2000"); ax.set_ylabel("annualised growth 2000–2024")
ax.legend(frameon=False, fontsize=9)
fig.text(0.012, -0.02, SRC + ". Author's calc.", fontsize=7, color="grey", style="italic")
fig.tight_layout(); fig.savefig(os.path.join(HERE, "fig2_beta.png"), bbox_inches="tight")

# Fig 3 — 분포 동학 (인구가중 EU평균 기준; 없으면 동일가중)
wbase = w_pop if w_pop is not None else w_unw
ybar_year = {yr: np.average(P[yr].values, weights=wbase.values) for yr in YEARS}
R = P.apply(lambda colv: 100 * colv / ybar_year[colv.name])
grid = np.linspace(20, 320, 400)
kde = lambda v: gaussian_kde(v[np.isfinite(v)])(grid)
fig, ax = plt.subplots(figsize=(8, 5))
for yr, color in [(2000, "#9ecae1"), (2012, "#4292c6"), (2024, "#08519c")]:
    if yr in R.columns:
        ax.plot(grid, kde(R[yr].values), color=color, lw=2.2, label=str(yr))
        ax.fill_between(grid, kde(R[yr].values), alpha=.06, color=color)
ax.axvline(100, color="grey", ls=":", lw=1); ax.text(102, ax.get_ylim()[1]*.92, "EU=100", color="grey", fontsize=8)
ax.set_title("Distribution dynamics: regional GDP per capita\nrelative to EU average (kernel density)",
             fontweight="bold", fontsize=12)
ax.set_xlabel("GDP per capita, % of EU average (PPS)"); ax.set_ylabel("density")
ax.legend(frameon=False, title="Year")
fig.text(0.012, -0.02, SRC + ". Author's calc.", fontsize=7, color="grey", style="italic")
fig.tight_layout(); fig.savefig(os.path.join(HERE, "fig3_distribution.png"), bbox_inches="tight")
print("saved: fig1_theil_popweighted.png, fig1_theil_unweighted.png, fig2_beta.png, fig3_distribution.png")
