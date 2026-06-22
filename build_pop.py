# -*- coding: utf-8 -*-
"""
Eurostat demo_r_pjangrp3 (NUTS-2 총인구, sex=T, age=TOTAL) → eu_nuts2_pop.csv
데이터 취득: mcp web_fetch (공식 Eurostat dissemination API). 아래 RAW는 그 응답에서
필요한 두 객체(value, geo index)만 발췌. flat index = geo_pos*7 + time_pos (time 2019..2025).
고정 가중치 = 2019–2024 평균 인구.
"""
import json, os, pandas as pd, numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = json.load(open(os.path.join(HERE, "pop_source.json"), encoding="utf-8"))
value = {int(k): v for k, v in RAW["value"].items()}
gidx = RAW["geo_index"]              # code -> geo position
NT = 7                               # 2019..2025
TPOS = [0, 1, 2, 3, 4, 5]            # 2019..2024 평균

# 패널 코드만
panel = pd.read_csv(os.path.join(HERE, "eu_nuts2_panel_clean.csv"))
codes = sorted(panel["code"].unique())

rows, missing = [], []
for c in codes:
    if c not in gidx:
        missing.append(c); continue
    p = gidx[c]
    vals = [value.get(p*NT + t) for t in TPOS]
    vals = [v for v in vals if v]            # 0/None 제외
    if not vals:
        missing.append(c); continue
    rows.append((c, int(np.mean(vals))))

pop = pd.DataFrame(rows, columns=["code", "pop"])
pop.to_csv(os.path.join(HERE, "eu_nuts2_pop.csv"), index=False)

# ── 검증 체크섬 ──
tot = pop["pop"].sum()
print(f"매칭 지역: {len(pop)} / 패널 {len(codes)}   (미매칭 {len(missing)}: {missing[:8]})")
print(f"EU 합계 인구(매칭분): {tot:,}  (EU27 ≈ 4.4–4.5억 기대)")
for c in ["FR10", "DE21", "EL30", "RO32", "PL91", "ES30"]:
    v = pop.loc[pop.code == c, "pop"]
    if len(v): print(f"  {c}: {int(v.iloc[0]):,}")
