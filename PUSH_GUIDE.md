# GitHub 업로드 가이드 — EU 실증 재현 번들

> 저장소(이미 생성됨): https://github.com/jihoon42/France-Europe-Final-Report
> Claude는 사용자 GitHub 인증이 없어 직접 푸시할 수 없습니다. 아래 명령으로 올리시면 됩니다.

## 업로드 (이 폴더 = 압축 푼 위치에서)
```bash
git init
git add -A
git commit -m "EU 공간 불평등 실증 분석 재현 번들"
git branch -M main
git remote add origin https://github.com/jihoon42/France-Europe-Final-Report.git
git push -u origin main
```
- 인증 창이 뜨면 GitHub 계정 로그인(또는 Personal Access Token) 입력.
- 빈 저장소에 README 등을 미리 만들어 충돌나면: `git pull --rebase origin main` 후 다시 `git push`.

## 포함 파일
- 분석 스크립트: `eu_spatial_analysis.py`(Theil·β·분포 동학) · `eu_within_by_country.py`(σ-수렴·국가별 기여·일드프랑스) · `housing_divergence.py`(주거 발산)
- 데이터: `eu_nuts2_panel_clean.csv` · `eu_nuts2_pop.csv` · `pop_source.json` · `build_pop.py`
- 그림 6개 · `README.md` · `requirements.txt`

## 보고서 본문
5장 **[방법론 주]**에 저장소 주소(https://github.com/jihoon42/France-Europe-Final-Report)를 이미 기입했습니다.
