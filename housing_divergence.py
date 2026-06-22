# -*- coding: utf-8 -*-
"""
주거 차원의 공간 발산 — 도시화 정도별 주거비 과부담률 (EU27, 2010-2025)
출처: Eurostat ilc_lvho07d (Housing cost overburden rate by degree of urbanisation).
취득: web_fetch, https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ilc_lvho07d?format=JSON&geo=EU27_2020
값은 위 응답에서 발췌(소수 48개). 누구나 위 URL로 재취득 가능.

핵심: 총량 과부담은 2016년 이후 완화됐지만, 도시는 농촌보다 일관되게 높고
      도시/농촌 비율은 2010년 1.33배 → 2025년 1.71배로 '벌어졌다'(주거 차원의 발산).
"""
import os
import numpy as np
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
years  = list(range(2010, 2026))
cities = [11.6, 12.5, 13.3, 13.3, 13.2, 13.3, 13.4, 12.4, 11.6, 11.8, 9.8, 10.5, 10.6, 10.6, 9.8, 9.6]
towns  = [8.6, 9.3, 11.0, 11.0, 10.9, 10.9, 10.3, 9.7, 9.4, 8.8, 7.0, 7.9, 8.1, 8.2, 7.8, 7.1]
rural  = [8.7, 9.0, 9.6, 10.0, 9.9, 9.1, 8.5, 7.7, 7.1, 7.0, 5.8, 7.0, 6.6, 6.9, 6.3, 5.6]

ratio0 = cities[0] / rural[0]
ratio1 = cities[-1] / rural[-1]
print(f"도시/농촌 과부담 비율: {years[0]} {ratio0:.2f}배 → {years[-1]} {ratio1:.2f}배")
print(f"도시 2025 {cities[-1]}% · 농촌 2025 {rural[-1]}% (격차 {cities[-1]-rural[-1]:.1f}%p)")

plt.rcParams.update({"figure.dpi": 130, "font.size": 11, "axes.grid": True,
                     "grid.alpha": .25, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(figsize=(8, 5))
ax.fill_between(years, cities, rural, color="#d62728", alpha=.07, zorder=0)
ax.plot(years, cities, color="#d62728", lw=2.4, marker="o", ms=3.5, label="Cities (DEG1)")
ax.plot(years, towns,  color="#7f7f7f", lw=1.8, ls="--", label="Towns & suburbs (DEG2)")
ax.plot(years, rural,  color="#1f77b4", lw=2.4, marker="s", ms=3.5, label="Rural areas (DEG3)")
ax.annotate(f"city/rural gap widens:\n{ratio0:.2f}× ({years[0]}) → {ratio1:.2f}× ({years[-1]})",
            xy=(2025, (cities[-1]+rural[-1])/2), xytext=(2018.4, 12.4),
            fontsize=9, color="#444",
            arrowprops=dict(arrowstyle="->", color="#999"))
ax.set_title("Housing stress diverges by place:\ncost-overburden rate, cities vs rural (EU27)",
             fontweight="bold", fontsize=12)
ax.set_xlabel("Year"); ax.set_ylabel("Housing cost overburden rate (%)")
ax.legend(frameon=False)
fig.text(0.012, -0.02, "Source: Eurostat ilc_lvho07d (housing cost overburden by degree of urbanisation).",
         fontsize=7, color="grey", style="italic")
fig.tight_layout(); fig.savefig(os.path.join(HERE, "fig4_housing_overburden.png"), bbox_inches="tight")
print("saved: fig4_housing_overburden.png")
