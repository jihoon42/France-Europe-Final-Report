*다음은 2026학년도 1학기 김예경 교수님의 '프랑스와 유럽' 기말 과제에 대해 작성하고 실습한 데이터 분석 내용입니다.*
*추후에, 내용을 추가하거나 보강할 계획이 있습니다. 다만, 공정성을 위하여 당분간 큰 골자는 변경하지 않도록 하겠습니다.*

# EU 공간 불평등 — 실증 분석 (재현 가능)

「슬로다운의 사각지대」 5.4(EU 결속정책 평가) · 8장(비판)의 실증 근거.
**동봉한 데이터 한 벌로 본문의 모든 수치·그림이 재생성됩니다.**

## 실행
```bash
pip install -r requirements.txt
python eu_spatial_analysis.py     # 그림 1~3·6 + Theil/β 검증 표
python eu_within_by_country.py    # 그림 5 + σ-수렴·국가별 기여·일드프랑스
```

## 파일
| 파일 | 설명 |
|---|---|
| `eu_spatial_analysis.py` | 메인 분석 (Theil·β·분포). 인구가중·동일가중 둘 다 산출 |
| `eu_nuts2_panel_clean.csv` | NUTS-2 1인당 GDP(PPS), 224지역·25국·2000–2024 (`nama_10r_2gdp`) |
| `eu_nuts2_pop.csv` | NUTS-2 인구 가중치 (2019–2024 평균, `demo_r_pjangrp3`) |
| `build_pop.py` + `pop_source.json` | 위 인구 가중치를 Eurostat 응답에서 재생성하는 스크립트·원자료 |
| `fig1_theil_popweighted.png` | **본문 헤드라인** (인구가중) |
| `fig1_theil_unweighted.png` | **강건성 각주** (동일가중) |
| `fig2_beta.png`, `fig3_distribution.png` | β-수렴, 분포 동학 |
| `housing_divergence.py` → `fig4_housing_overburden.png` | **주거 차원 발산** (Eurostat `ilc_lvho07d`, 도시 vs 농촌 주거비 과부담, 도시/농촌 비율 1.33→1.71배) |
| `eu_within_by_country.py` → `fig5_within_by_country.png` | **국가 내 발산 심화** (σ-수렴 −28%; 국가별 기여 분해 — 프랑스 EU 1위; 일드프랑스/프랑스나머지 1.81→1.89배) |
| `requirements.txt` | 의존 패키지 |

## 결과 (둘 다 본 패널로 100% 재현됨 · 검증 완료)
| 지표 | 인구가중 (본문) | 동일가중 (강건성) |
|---|---|---|
| Theil total 변화 2000→2024 | −31% | −28% |
| between (국가 間) | **−56%** | −47% |
| within (국가 內) | **+5%** | +12% |
| within 비중 | **41% → 62%** | 33% → 51% |
| 교차 연도 | **2007** (글로벌 금융위기) | 2023 |
| β-수렴 slope / R² | −0.017 / 0.46 | −0.017 / 0.46 |

**두 방식 모두 핵심 명제는 동일하게 성립한다**: 국가 間 수렴 · 국가 內 발산 · 2024년 within 비중이 과반으로 역전. 본문은 인구가중(사람 1단위)을 헤드라인으로, 동일가중(지역 1단위)을 robustness로 함께 싣습니다.

## 방법
1. **Theil-T 분해** — 전체 불평등 = 국가 間(between) + 국가 內(within). 인구가중/동일가중.
2. **β-수렴** — 초기(2000) 소득 대비 연평균 성장률 회귀. 가중과 무관.
3. **분포 동학** — EU평균=100 상대 1인당GDP의 커널밀도(2000/2012/2024).
4. **심화** — σ-수렴(인구가중 log GDP 표준편차), 국가 내 발산의 국가별 기여 분해(프랑스 1위), 일드프랑스 상대비 추이.

## 데이터 출처 (재취득 가능)
- 1인당 GDP: Eurostat **`nama_10r_2gdp`** (단위 `PPS_EU27_2020_HAB`, NUTS-2).
- 인구: Eurostat **`demo_r_pjangrp3`** (sex=T, age=TOTAL, NUTS-2). API:
  `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/demo_r_pjangrp3?format=JSON&sex=T&age=TOTAL&unit=NR&geoLevel=nuts2`
- 균형패널: 2000–2024 내내 관측된 224개 NUTS-2(벨기에·루마니아 등 결측 과다 지역 제외), 내부 결측은 선형보간.
- 1인당 GDP는 거주지가 아닌 근무지 기준이라 통근 유입이 대도시를 과대계상 → 본고 논지를 강화하는 방향.

출처: Eurostat. 저자 계산.
