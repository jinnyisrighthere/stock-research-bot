"""Auditable NVDA research calculations. USD millions except per-share data.
Run from project root with the bundled Python. No network or invented actuals.
Reported inputs transcribed from sources listed in sources.json; all derived
numbers, score aggregation and forecast calculations are written to fact_sheet.json.
"""
import json, math, shutil
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output' / 'nvda_20261122'
OUT.mkdir(parents=True, exist_ok=True)
legacy = json.loads((ROOT/'output/NVDA_fact_sheet.json').read_text(encoding='utf-8'))

sources = {
'S01': ['FY2026 SEC 10-K', '2026-02-25', 'https://www.sec.gov/Archives/edgar/data/1045810/000104581026000021/nvda-20260125.htm'],
'S02': ['FY2024 SEC 10-K', '2024-02-21', 'https://www.sec.gov/Archives/edgar/data/1045810/000104581024000029/nvda-20240128.htm'],
'S03': ['FY2023 SEC 10-K', '2023-02-24', 'https://www.sec.gov/Archives/edgar/data/1045810/000104581023000017/nvda-20230129.htm'],
'S04': ['FY2027 Q3 earnings release and GAAP reconciliation', '2026-11-17', 'https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-third-quarter-fiscal-2027'],
'S05': ['FY2027 Q3 supplemental unaudited statements', '2026-11-17', 'https://s201.q4cdn.com/141608511/files/doc_financials/2027/Q327/Supplemental-Financial-Information-NVDA-2027-Q3.pdf'],
'S06': ['FY2027 Q3 earnings call transcript', '2026-11-17', 'https://s201.q4cdn.com/141608511/files/content_files/NVDA-3Q27-Earnings-Transcript.pdf'],
'S07': ['FY2027 Q2 SEC 10-Q', '2026-08-27', 'https://www.sec.gov/Archives/edgar/data/1045810/000104581026000075/nvda-20260726.htm'],
'S08': ['FY2027 Q2 earnings release', '2026-08-26', 'https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-second-quarter-fiscal-2027'],
'S09': ['FY2026 Q1 earnings release', '2025-05-28', 'https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-first-quarter-fiscal-2026'],
'S10': ['FY2025 Q4 earnings release', '2025-02-26', 'https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-fourth-quarter-and-fiscal-2025'],
'S11': ['CEO resignation SEC 8-K effective November 11', '2026-11-12', 'https://www.sec.gov/Archives/edgar/data/1045810/000104581026000082/nvda-20261111.htm'],
'S12': ['CEO transition company announcement', '2026-11-12', 'https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-CEO-Transition/default.aspx'],
'S13': ['Reuters accounting inquiry report reproduced by StreetInsider', '2026-11-20', 'https://www.streetinsider.com/General%2BNews/Exclusive-Nvidias%2Baccounting%2Bis%2Ba%2Bfocus%2Bof%2BUS%2BSEC%2Binvestigation%2C%2Bsources%2Bsay/27381042.html'],
'S14': ['California DOJ investigative subpoena announcement', '2026-11-19', 'https://oag.ca.gov/news/press-releases/attorney-general-bonta-serves-investigative-subpoena-nvidia'],
'S15': ['2026 proxy and annual report', '2026-05', 'https://s201.q4cdn.com/141608511/files/doc_financials/2026/ar/2026-annual-report-web-Hyperlinks.pdf'],
'S16': ['Gartner AI infrastructure spending forecast', '2026-11-12', 'https://www.gartner.com/en/newsroom/press-releases/2026-11-12-gartner-forecasts-artificial-intelligence-infrastructure-spending-to-represent-59-percent-of-total-global-artificial-intelligence-spending-in-2027'],
'S17': ['AMD Q3 2026 earnings', '2026-11-03', 'https://ir.amd.com/news-events/press-releases/detail/1303/amd-reports-third-quarter-2026-financial-results'],
'S18': ['Broadcom Q3 FY2026 earnings', '2026-09-02', 'https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announces-third-quarter-fiscal-year-2026-financial'],
'S19': ['Stock Analysis NVDA ratios and regular close', '2026-11-20', 'https://stockanalysis.com/stocks/nvda/financials/ratios/'],
'S20': ['Stock Analysis AMD statistics', '2026-11-20', 'https://stockanalysis.com/stocks/amd/statistics/'],
'S21': ['Stock Analysis Broadcom statistics', '2026-11-20', 'https://stockanalysis.com/stocks/avgo/statistics/'],
'S22': ['MoneyWeek LSEG consensus recap', '2026-11-18', 'https://moneyweek.com/investments/tech-stocks/nvidia-q3-results'],
'S23': ['Kiplinger earnings expectations recap', '2026-11-19', 'https://www.kiplinger.com/news/live/nvidia-earnings-live-updates-and-commentary-november-2026'],
'S24': ['Microsoft FY2027 Q1 earnings call', '2026-10-28', 'https://www.microsoft.com/en-us/investor/events/fy-2027/earnings-fy-2027-q1'],
'S25': ['Alphabet Q3 2026 earnings call', '2026-10', 'https://abc.xyz/investor/events/event-details/2026/2026-Q3-Earnings-Call-2026-Ujou16CTw9/default.aspx'],
'L01': ['Existing Python engine technical output; raw daily series not retained', '2026-11-22', 'output/NVDA_fact_sheet.json'],
'S26': ['Stock Analysis NVDA daily OHLCV', '2026-11-20', 'https://stockanalysis.com/stocks/nvda/history/'],
}

keys='fy end revenue gross_profit operating_income net_income eps shares ocf capex principal sbc da interest cash debt inventory ar ap assets equity tax pretax buybacks dividends acquisitions repay'.split()
values=[
[2022,'2022-01-30',26914,17475,10041,9752,.385,25350,9108,976,83,2004,1174,236,21208,10946,2605,4650,1783,44187,26612,189,9941,0,399,263,1000],
[2023,'2023-01-29',26974,15356,4224,4368,.174,25070,5641,1833,58,2709,1544,262,13296,10953,5159,3827,1193,41182,22101,-187,4181,10039,398,49,0],
[2024,'2024-01-28',60922,44301,32972,29760,1.19,24940,28090,1069,74,3549,1508,257,25984,9709,5282,9999,2699,65728,42978,4058,33818,9533,395,83,1250],
[2025,'2025-01-26',130497,97858,81453,72880,2.94,24804,64089,3236,129,4737,1864,247,43210,8463,10080,23065,6310,111601,79327,11146,84026,33706,834,1007,1250],
[2026,'2026-01-25',215938,153463,130387,120067,4.90,24514,102718,6042,101,6386,2843,259,49670,8468,21403,38466,9812,206803,157293,21383,141450,40086,974,1535,0],
]
annual=[dict(zip(keys,v)) for v in values]
for r in annual:
    r['source']='S03' if r['fy']==2022 else ('S02' if r['fy']==2023 else 'S01')
    r['cash_definition']='Cash plus marketable debt securities; FY2022-25 combined marketable securities disclosed, FY2026 excludes listed equity'
    r['rd']={2022:5268,2023:7339,2024:8675,2025:12914,2026:18497}[r['fy']]

qkeys='period end revenue gross_profit operating_income net_income eps shares ocf capex principal sbc da interest cash debt inventory ar ap assets equity'.split()
qvalues=[
['FY25Q4','2025-01-26',39331,28723,24034,22091,.89,24804,16628,1077,32,1321,543,61,43210,8463,10080,23065,6310,111601,79327],
['FY26Q1','2025-04-27',44062,26668,21638,18775,.76,24611,27414,1227,52,1474,612,63,53691,8464,11333,22132,7331,125254,83843],
['FY26Q2','2025-07-27',46743,33853,28440,26422,1.08,None,15365,1894,21,1624,668,62,53991,None,14962,27808,9064,None,None],
['FY26Q3','2025-10-26',57006,41849,36010,31910,1.30,24483,23750,1637,24,1655,752,61,60608,None,19784,33391,8624,None,None],
['FY26Q4','2026-01-25',68127,51093,44299,42960,1.76,24432,36188,1284,4,1633,811,73,49670,8468,21403,38466,9812,206803,157293],
['FY27Q1','2026-04-26',81615,61157,53536,58321,2.39,24391,50344,1757,33,1928,997,102,None,None,25797,40710,13097,None,None],
['FY27Q2','2026-07-26',96221,72142,63734,59688,2.46,24285,24077,2677,59,2027,1127,227,56586,33366,31575,63059,15059,320272,228984],
['FY27Q3','2026-10-25',115844,86676,77520,65287,2.70,24186,48253,4422,54,2088,1254,None,53512,32371,39724,81033,21074,372188,266666],
]
quarterly=[dict(zip(qkeys,v)) for v in qvalues]
# Q4 FY25 weighted diluted shares are taken from the quarter, not the annual average.
# Exact quarterly share count not verified; leave missing rather than impute annual count.
quarterly[0]['shares']=None
quarterly[0]['interest']=None
quarterly[4]['principal']=annual[-1]['principal']-sum(r['principal'] for r in quarterly[1:4])
quarterly[4]['da']=annual[-1]['da']-sum(r['da'] for r in quarterly[1:4])
for i,r in enumerate(quarterly):
    r['source']=['S10','S09','S08; L01 balance subset','S04; L01 balance subset','S01; L01 quarter subset','S08; L01 balance subset','S08','S05'][i]
    r['days']=91
    r['rev_year_ago']=[22103,26044,30040,35082,39331,44062,46743,57006][i]

def pct(a,b): return None if a is None or b in (None,0) else a/b*100
def growth(a,b): return None if a is None or b in (None,0) else (a/b-1)*100
def derive(rows,annual_mode):
    prev=None
    for r in rows:
        r['cogs']=r['revenue']-r['gross_profit']
        r['gpm']=pct(r['gross_profit'],r['revenue']);r['opm']=pct(r['operating_income'],r['revenue'])
        r['fcf']=r['ocf']-r['capex']-r['principal']
        r['fcf_margin']=pct(r['fcf'],r['revenue']);r['ocf_ni']=r['ocf']/r['net_income']
        r['ebitda_operating']=r['operating_income']+r['da']
        r['nwc']=r['ar']+r['inventory']-r['ap']
        r['net_debt']=None if r['debt'] is None or r['cash'] is None else r['debt']-r['cash']
        r['interest_cover']=None if r['interest'] in (None,0) else r['operating_income']/r['interest']
        r['dso']=r['ar']/r['revenue']*(365 if annual_mode else r['days'])
        r['dio']=r['inventory']/r['cogs']*(365 if annual_mode else r['days'])
        r['dpo']=r['ap']/r['cogs']*(365 if annual_mode else r['days'])
        r['ccc']=r['dso']+r['dio']-r['dpo']
        r['sbc_rev']=pct(r['sbc'],r['revenue'])
        r['yoy']=growth(r['revenue'],prev['revenue'] if annual_mode and prev else (r.get('rev_year_ago')))
        r['qoq']=growth(r['revenue'],prev['revenue']) if prev and not annual_mode else None
        r['share_change']=growth(r['shares'],prev['shares']) if prev else None
        r['accruals']=None
        if r['assets'] and prev and prev['assets']:
            r['accruals']=pct(r['net_income']-r['ocf'],(r['assets']+prev['assets'])/2)
        if annual_mode:
            # Conservative comparable ROIC: fixed normalized 17% tax; gross capitalization.
            # Cash not netted, avoiding unstable net-cash denominators and equity portfolio contamination.
            cap=r['equity']+r['debt'];priorcap=prev['equity']+prev['debt'] if prev else None
            r['roic_gross']=pct(r['operating_income']*.83,(cap+priorcap)/2 if priorcap else cap)
            r['roic_spread_14']=r['roic_gross']-14
        prev=r
derive(annual,True);derive(quarterly,False)

price=125.53; shares=24186
latest=quarterly[-1]
ttm={k:sum(r[k] for r in quarterly[-4:]) for k in ['revenue','gross_profit','operating_income','net_income','ocf','capex','principal','sbc','da','fcf']}
ttm['eps']=sum(r['eps'] for r in quarterly[-4:])
ttm['fcf_yield']=pct(ttm['fcf'],price*shares)
ttm['pe']=price/ttm['eps'];ttm['p_fcf']=price*shares/ttm['fcf']
ttm['ocf_ni']=ttm['ocf']/ttm['net_income']
ttm['fcf_margin']=pct(ttm['fcf'],ttm['revenue'])
ttm['ebitda_operating']=ttm['operating_income']+ttm['da']
market_cap=price*shares
ev=market_cap+latest['debt']-latest['cash']
ttm['ev_sales']=ev/ttm['revenue'];ttm['ev_ebitda']=ev/ttm['ebitda_operating']

model_assumptions={
'bull':dict(probability=25,revenue=[650000,820000,975000,1100000,1210000],opm=[.63,.62,.60,.58,.56],wacc=.12,g=.035,pe=19,share_change=-.005,investment_recovery=.75,reserve=10000),
'base':dict(probability=45,revenue=[550000,650000,735000,805000,860000],opm=[.60,.58,.56,.54,.52],wacc=.14,g=.03,pe=14,share_change=0,investment_recovery=.50,reserve=25000),
'bear':dict(probability=30,revenue=[390000,370000,390000,420000,450000],opm=[.48,.42,.43,.44,.45],wacc=.17,g=.02,pe=10,share_change=.01,investment_recovery=.25,reserve=50000),
}
investments=44219+65528
def dcf(a,wacc=None,g=None):
    wacc=a['wacc'] if wacc is None else wacc; g=a['g'] if g is None else g
    rows=[];prior_nwc=latest['nwc']
    for t,(rev,margin) in enumerate(zip(a['revenue'],a['opm']),1):
        nopat=rev*margin*.83;da=rev*.012;capex=rev*.03;nwc=rev*.22
        fcf=nopat+da-capex-(nwc-prior_nwc);pv=fcf/(1+wacc)**t
        rows.append(dict(year=t,revenue=rev,opm=margin*100,nopat=nopat,da=da,capex=capex,nwc=nwc,delta_nwc=nwc-prior_nwc,fcff=fcf,pv=pv))
        prior_nwc=nwc
    # Stable terminal cash flow explicitly funds working capital growth.
    terminal_rev=a['revenue'][-1]*(1+g)
    terminal_fcf=terminal_rev*a['opm'][-1]*.83+terminal_rev*.012-terminal_rev*.03-a['revenue'][-1]*.22*g
    terminal_pv=terminal_fcf/(wacc-g)/(1+wacc)**5
    enterprise=sum(x['pv'] for x in rows)+terminal_pv
    bridge=latest['cash']-latest['debt']+investments*a['investment_recovery']-a['reserve']
    equity=enterprise+bridge
    return dict(rows=rows,enterprise_value=enterprise,equity_value=equity,bridge=bridge,terminal_pv=terminal_pv,terminal_weight_pct=terminal_pv/enterprise*100,price=equity/shares,terminal_fcff=terminal_fcf)
scenarios={}
for name,a in model_assumptions.items():
    result=dcf(a);diluted_shares=shares*(1+a['share_change'])
    # Scenario EPS excludes investment fair-value gains, uses normalized GAAP operating earnings after SBC.
    eps=a['revenue'][0]*a['opm'][0]*.83/diluted_shares
    target=eps*a['pe']
    scenarios[name]=dict(**a,dcf=result,eps=eps,normalized_net_income=eps*diluted_shares,target=target,return_pct=growth(target,price),dcf_upside_pct=growth(result['price'],price),shares_12m=diluted_shares)
weighted=sum(a['probability']/100*a['target'] for a in scenarios.values())
rr=(scenarios['base']['target']-price)/(price-scenarios['bear']['target'])
sensitivity=[{'wacc':round(w*100,6),'g':round(g*100,6),'price':dcf(model_assumptions['base'],w,g)['price']} for w in [.12,.14,.16,.18] for g in [.02,.03,.04]]
# Reverse DCF uses normalized FCFF built from TTM operating earnings, not levered OCF-CapEx.
# Historical NWC increase from FY26Q3 to FY27Q3 and actual D&A/CapEx/principal.
base_fcff=ttm['operating_income']*.83+ttm['da']-ttm['capex']-ttm['principal']-(latest['nwc']-quarterly[3]['nwc'])
reverse_target=market_cap-scenarios['base']['dcf']['bridge']
def reverse_value(growth_rate,w=.14,g=.03):
    flows=[base_fcff*(1+growth_rate)**t for t in range(1,6)]
    return sum(f/(1+w)**t for t,f in enumerate(flows,1))+flows[-1]*(1+g)/(w-g)/(1+w)**5
lo,hi=-.8,1.5
assert reverse_value(lo)<reverse_target<reverse_value(hi)
for _ in range(100):
    mid=(lo+hi)/2
    if reverse_value(mid)<reverse_target:lo=mid
    else:hi=mid
implied=(lo+hi)/2

tech=legacy['technical_chart'].copy()
tech['source']='L01';tech['reproducibility']='Existing engines/chart_analyzer.py result, daily OHLCV was not retained; not recomputed in this run.'
tech['as_of']='2026-11-20';tech['gap20']=growth(price,tech['sma_20']);tech['gap50']=growth(price,tech['sma_50'])
tech['drawdown_high']=growth(price,tech['high_52w']);tech['above_low']=growth(price,tech['low_52w'])
tech['last_day_return']=growth(price,145.98)
recent_close=[125.53,145.98,150.96,155.46,156.14,162.85,166.19,173.73,168.89,178.67,186.64,181.60,200.13,206.69,202.06,204.64,213.66,215.38,217.94,216.00]
recent_volume=[633336951,322940099,349791392,406985086,333822062,365796552,747707648,339214801,429273205,462719328,180212285,306127783,149033316,91943391,119272174,168386423,77568070,93030154,84799695,90829293]
tech['recomputed_sma20']=mean(recent_close)
tech['recomputed_volume_ratio20']=recent_volume[0]/mean(recent_volume)
tech['recent_close_desc']=recent_close;tech['recent_volume_desc']=recent_volume
tech['earnings_next_day_return']=growth(150.96,155.46)
tech['earnings_to_friday_return']=growth(price,155.46)
tech['ceo_announcement_return']=growth(166.19,173.73)
hist_pe=[58.55,114.74,50.65,47.93,37.98]
hist_fpe=[45.52,52.57,31.19,36.24,26.73]

scores={'NVIDIA':[9,8,9,9,9,10,8,9,7],'AMD':[8,8,7,6,6,7,7,6,6],'Broadcom':[8,8,9,8,6,8,8,7,7]}
score_totals={k:mean(v) for k,v in scores.items()}
annual_fcf=sum(r['fcf'] for r in annual)
allocation={k:{'amount':sum(r[k] for r in annual),'pct_fcf':sum(r[k] for r in annual)/annual_fcf*100} for k in ['capex','acquisitions','buybacks','dividends','repay']}
mix={}
for label,nums in {'Data Center':[47525,115186,193737],'Gaming':[10447,11350,16042],'ProViz':[1553,1878,3191],'Auto':[1091,1692,2349],'OEM Other':[306,391,619]}.items():
    mix[label]=[dict(fy=fy,amount=val,share=val/annual[fy-2022]['revenue']*100) for fy,val in zip([2024,2025,2026],nums)]
geo={k:{'amount':v,'share':v/215938*100} for k,v in {'US':149617,'Taiwan':42345,'China HK':19677,'Other':4299}.items()}
dc_increment={str(fy):{'dc_growth':growth(mix['Data Center'][i]['amount'],mix['Data Center'][i-1]['amount']),'contribution':(mix['Data Center'][i]['amount']-mix['Data Center'][i-1]['amount'])/(annual[fy-2022]['revenue']-annual[fy-2023]['revenue'])*100} for i,fy in [(1,2025),(2,2026)]}
diagnostics={
'q3_ocf_growth':growth(48253,23750),'q3_fcf_growth':growth(latest['fcf'],quarterly[3]['fcf']),
'q3_inventory_yoy':growth(39724,19784),'q3_ar_yoy':growth(81033,33391),
'q3_ar_qoq':growth(81033,63059),'q3_inventory_qoq':growth(39724,31575),
'q3_eps_non_gaap':2.68,'q2_eps_non_gaap':2.22,'q3_prior_eps_non_gaap_recast':1.27,
'q3_eps_surprise':growth(2.68,2.47),'q3_revenue_surprise_lseg':growth(115844,109110),
'q3_revenue_surprise_alternative':growth(115844,108800),'q3_revenue_beat_company':growth(115844,108000),
'q3_gpm_beat_company_pp':latest['gpm']-74,'q4_guidance_growth':growth(130000,115844),
'fy27_revenue_guidance_bridge':293681+130000,'fy28_revenue_guidance_bridge':(293681+130000)*1.75,
'q3_dc_share':107600/115844*100,'q3_edge_share':8200/115844*100,
'buyback_avg_fy26':40388/282,'buyback_vs_current':growth(125.53,40388/282),
'9m_equity_purchase_vs_fcf':58100/(122675-8856-147)*100,
'9m_equity_gain_vs_pretax':25474/220427*100,
'q3_accruals':pct(65287-48253,(372188+320272)/2),
'q3_cash_conversion':48253/65287,
'9m_cash_conversion':122675/183297,
'moat_margin_gap_amd':latest['gpm']-7210/13377*100,
'amd_gpm':7210/13377*100,'amd_opm':2832/13377*100,
'illustrative_capex_payback_years':8000/2000,
'q3_opm_non_gaap':77900/115844*100,
'q3_gaap_nongaap_eps_gap':growth(2.68,2.70),
'market_cap_spot_shares':125.53*24147,
'equity_quality_score':5.0,
'tam_2026_infra':1563000,'tam_2027_infra':2397000,'server_2026':527600,'server_2027':957200,
'tam_2031_scenario':1563000*1.20**5,'sam_2026_scenario':527600*.65,'sam_2031_scenario':527600*.65*1.20**5,
'tam_cagr_assumption':20,'sam_capture_assumption':65,
'supply_commitments_q2':279000,'supply_commitments_q3':390000,
'msft_capex_q1':45200,'alphabet_capex_low':195000,'alphabet_capex_high':205000,
'founder_proxy_ownership':3.58,
'base_revenue_growth':growth(550000,ttm['revenue']),
'base_five_year_revenue_cagr':((860000/ttm['revenue'])**.2-1)*100,
'base_dcf_discount':growth(scenarios['base']['dcf']['price'],price),
'base_sbc_deducted_ttm_fcf':ttm['fcf']-ttm['sbc'],
'fy26_investment_gain':8918,
'fy25_investment_gain':1030,
'fy24_investment_gain':238,
}
facts=dict(summary={'ticker':'NVDA','company_name':'NVIDIA Corporation','as_of_date':'2026-11-22','price_as_of':'2026-11-20 16:00 America/New_York','currency':'USD','current_price':price,'valuation_diluted_shares_m':shares,'market_cap_diluted_m':market_cap,'enterprise_value_cash_debt_only_m':ev},annual=annual,quarterly=quarterly,ttm=ttm,scenarios=scenarios,valuation={'weighted_target':weighted,'weighted_return_pct':growth(weighted,price),'base_reward_bear_risk':rr,'base_dcf':scenarios['base']['dcf']['price'],'reverse_normalized_fcff':base_fcff,'reverse_five_year_cagr_pct':implied*100,'reverse_residual_pct':growth(reverse_value(implied),reverse_target),'sensitivity':sensitivity,'cash_plus_debt_securities':53512,'financial_debt':32371,'listed_equity':44219,'nonmarketable_investments':65528,'total_investments':investments,'entry_low':100,'entry_high':110},technical=tech,mix=mix,geography=geo,dc_growth_contribution=dc_increment,moat_scores=scores,moat_totals=score_totals,capital_allocation_5y=allocation,capital_allocation_fcf_total=annual_fcf,diagnostics=diagnostics,history={'years':[2022,2023,2024,2025,2026],'pe':hist_pe,'forward_pe':hist_fpe,'pe_low':min(hist_pe),'pe_high':max(hist_pe),'pe_mean':mean(hist_pe),'fpe_low':min(hist_fpe),'fpe_high':max(hist_fpe),'fpe_mean':mean(hist_fpe),'scope':'Five fiscal year-end snapshots; not daily 5-year trading range; uses subsequently known fiscal earnings, not point-in-time trading multiples'},peers={'NVDA':{'trailing_pe':13.48,'forward_pe':8.65,'ev_ebitda':12.21},'AMD':{'trailing_pe':91.99,'forward_pe':28.19,'ev_ebitda':62.45,'revenue':13377,'gross_profit':7210,'operating_income':2832},'AVGO':{'trailing_pe':38.86,'forward_pe':17.52,'ev_ebitda':28.48,'revenue_q3_rounded':29600,'ai_revenue_q3_rounded':16700,'revenue_yoy_rounded':86}},sources=sources,limitations=['Latest Q3 10-Q not retrieved; latest statements are unaudited supplemental results, not audited 10-Q notes.','No raw daily price series; legacy technical indicators are retained and clearly marked.','No granular ASP/units, exact top3/top5 latest customer shares, or same-definition five-year TAM forecast available.','Q2/Q3 FY26 and Q1 FY27 balance subsets retain vendor inputs; missing debt/assets not invented.','Historical multiples are five year-end snapshots, not a full trading band.','Forecasts, probabilities, valuation rates, investment recovery and reserve are analyst assumptions, not consensus.'])
assert len(annual)==5 and len(quarterly)==8
assert sum(a['probability'] for a in scenarios.values())==100
assert all(abs(r['revenue']-r['cogs']-r['gross_profit'])<1e-6 for r in annual+quarterly)
assert all(r['fcf']==r['ocf']-r['capex']-r['principal'] for r in annual+quarterly)
assert abs(facts['valuation']['reverse_residual_pct'])<1e-7
assert sum(v['amount'] for v in geo.values())==215938
assert sum(x[2]['amount'] for x in mix.values())==215938
for a in scenarios.values(): assert a['wacc']>a['g']
(OUT/'fact_sheet.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copyfile(ROOT/'output/NVDA_chart.png',OUT/'NVDA_chart_legacy.png')
print(json.dumps({'valuation':facts['valuation'],'scenarios':{k:{x:v[x] for x in ['eps','target','return_pct']} for k,v in scenarios.items()},'ttm':ttm,'diagnostics':diagnostics},indent=2))
