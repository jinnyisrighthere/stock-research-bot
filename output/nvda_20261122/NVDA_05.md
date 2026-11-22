# 부록 | 계산 기준과 출처

## 자료와 계산의 추적 가능성

이 보고서의 수치와 평가 모델은 engines/nvda_research_20261122.py가 생성한 fact_sheet.json을 기준으로 작성했다. 공시·IR·가격 원자료를 입력한 뒤 비율, 성장률, 현금흐름, DCF, Reverse DCF, 민감도, 시나리오와 기술 지표를 계산했다. 기존 단순 가치평가 결과는 이번 심층 모델에 그대로 사용하지 않았다.

FCF=영업현금흐름-설비투자-금융리스 등 원금 지급. 영업 EBITDA=GAAP 영업이익+감가상각. NWC=매출채권+재고-매입채무. 순금융부채=금융부채-현금·해당 시장성 증권. ROIC는 정상 세율과 평균 총자본을 사용하는 대용치다. 표별 정의가 일반 데이터 공급업체와 다를 수 있으므로 배수 비교 시 같은 산식을 확인해야 한다.

분기 현금흐름은 공시 누적값의 차감 또는 분기 보충자료를 사용했다. 누적·분기 반올림 차이가 있을 수 있다. 회계연도, 캘린더 연도, 평가 모델의 다음 12개월은 서로 구별했다. 주식분할 조정 EPS와 주식수를 사용하며 원자료의 결측값을 임의 채우지 않았다.

## 남아 있는 검증 공백

최신 10-Q의 상세 계약·고객 지원·채권 및 투자 평가 주석은 후속 확인 대상이다. 출하량·ASP, 최신 Top 3·Top 5 고객 비중, 세대별 수익성·정확한 수주잔고는 공시 범위 내에서 분리할 수 없다. 장기 TAM·SAM, WACC·마진·확률은 분석 가정이다. 역사적 배수는 5개 연말 표본이며 연속 거래 밴드가 아니다.

기술 지표는 최근 20거래일 종가·거래량만 새로 검산했다. 장기 이동평균·RSI·52주 범위와 참고 차트는 기존 엔진 자료이며 전체 가격 원시 계열이 보존되지 않았다. 매물대는 실제 가격별 체결 자료가 아닌 근사치다. 이 한계 때문에 기술 분석을 가치평가보다 우선하지 않는다.

정량 무결성 검사에는 손익 항등식, FCF 산식, 지역·제품 매출 합계, 시나리오 확률 합계, Reverse DCF 역산 오차, 할인율이 영구성장률보다 높은지 확인하는 절차가 포함된다. 이러한 계산 검증은 원공시의 감사나 회사 설명의 진실성 검증을 대체하지 않는다.

## 출처 목록

본문의 S 번호는 아래 문서와 연결된다. 공시·IR은 우선 출처, 시장 데이터와 언론 보도는 보조 출처다. 발행일과 수집 기준일은 다를 수 있다. 링크는 원문 확인용이다.

### S01 | FY2026 SEC 10-K

발행·자료일: 2026-02-25.

https://www.sec.gov/Archives/edgar/data/1045810/000104581026000021/nvda-20260125.htm

### S02 | FY2024 SEC 10-K

발행·자료일: 2024-02-21.

https://www.sec.gov/Archives/edgar/data/1045810/000104581024000029/nvda-20240128.htm

### S03 | FY2023 SEC 10-K

발행·자료일: 2023-02-24.

https://www.sec.gov/Archives/edgar/data/1045810/000104581023000017/nvda-20230129.htm

### S04 | FY2027 Q3 earnings release and GAAP reconciliation

발행·자료일: 2026-11-17.

https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-third-quarter-fiscal-2027

### S05 | FY2027 Q3 supplemental unaudited statements

발행·자료일: 2026-11-17.

https://s201.q4cdn.com/141608511/files/doc_financials/2027/Q327/Supplemental-Financial-Information-NVDA-2027-Q3.pdf

### S06 | FY2027 Q3 earnings call transcript

발행·자료일: 2026-11-17.

https://s201.q4cdn.com/141608511/files/content_files/NVDA-3Q27-Earnings-Transcript.pdf

### S07 | FY2027 Q2 SEC 10-Q

발행·자료일: 2026-08-27.

https://www.sec.gov/Archives/edgar/data/1045810/000104581026000075/nvda-20260726.htm

### S08 | FY2027 Q2 earnings release

발행·자료일: 2026-08-26.

https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-second-quarter-fiscal-2027

### S09 | FY2026 Q1 earnings release

발행·자료일: 2025-05-28.

https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-first-quarter-fiscal-2026

### S10 | FY2025 Q4 earnings release

발행·자료일: 2025-02-26.

https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-fourth-quarter-and-fiscal-2025

### S11 | CEO resignation SEC 8-K effective November 11

발행·자료일: 2026-11-12.

https://www.sec.gov/Archives/edgar/data/1045810/000104581026000082/nvda-20261111.htm

### S12 | CEO transition company announcement

발행·자료일: 2026-11-12.

https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-CEO-Transition/default.aspx

### S13 | Reuters accounting inquiry report reproduced by StreetInsider

발행·자료일: 2026-11-20.

https://www.streetinsider.com/General%2BNews/Exclusive-Nvidias%2Baccounting%2Bis%2Ba%2Bfocus%2Bof%2BUS%2BSEC%2Binvestigation%2C%2Bsources%2Bsay/27381042.html

### S14 | California DOJ investigative subpoena announcement

발행·자료일: 2026-11-19.

https://oag.ca.gov/news/press-releases/attorney-general-bonta-serves-investigative-subpoena-nvidia

### S15 | 2026 proxy and annual report

발행·자료일: 2026-05.

https://s201.q4cdn.com/141608511/files/doc_financials/2026/ar/2026-annual-report-web-Hyperlinks.pdf

### S16 | Gartner AI infrastructure spending forecast

발행·자료일: 2026-11-12.

https://www.gartner.com/en/newsroom/press-releases/2026-11-12-gartner-forecasts-artificial-intelligence-infrastructure-spending-to-represent-59-percent-of-total-global-artificial-intelligence-spending-in-2027

### S17 | AMD Q3 2026 earnings

발행·자료일: 2026-11-03.

https://ir.amd.com/news-events/press-releases/detail/1303/amd-reports-third-quarter-2026-financial-results

### S18 | Broadcom Q3 FY2026 earnings

발행·자료일: 2026-09-02.

https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announces-third-quarter-fiscal-year-2026-financial

### S19 | Stock Analysis NVDA ratios and regular close

발행·자료일: 2026-11-20.

https://stockanalysis.com/stocks/nvda/financials/ratios/

### S20 | Stock Analysis AMD statistics

발행·자료일: 2026-11-20.

https://stockanalysis.com/stocks/amd/statistics/

### S21 | Stock Analysis Broadcom statistics

발행·자료일: 2026-11-20.

https://stockanalysis.com/stocks/avgo/statistics/

### S22 | MoneyWeek LSEG consensus recap

발행·자료일: 2026-11-18.

https://moneyweek.com/investments/tech-stocks/nvidia-q3-results

### S23 | Kiplinger earnings expectations recap

발행·자료일: 2026-11-19.

https://www.kiplinger.com/news/live/nvidia-earnings-live-updates-and-commentary-november-2026

### S24 | Microsoft FY2027 Q1 earnings call

발행·자료일: 2026-10-28.

https://www.microsoft.com/en-us/investor/events/fy-2027/earnings-fy-2027-q1

### S25 | Alphabet Q3 2026 earnings call

발행·자료일: 2026-10.

https://abc.xyz/investor/events/event-details/2026/2026-Q3-Earnings-Call-2026-Ujou16CTw9/default.aspx

### L01 | Existing Python engine technical output; raw daily series not retained

발행·자료일: 2026-11-22.

output/NVDA_fact_sheet.json

### S26 | Stock Analysis NVDA daily OHLCV

발행·자료일: 2026-11-20.

https://stockanalysis.com/stocks/nvda/history/

