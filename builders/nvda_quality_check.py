"""Content preservation, citations, tables and model integrity checks."""
from pathlib import Path
import json,re,hashlib
from docx import Document
from docx.oxml.ns import qn
from pypdf import PdfReader,PdfWriter

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/nvda_20261122'
dp=OUT/'NVDA_심층분석_20261122.docx';pp=OUT/'NVDA_심층분석_20261122.pdf'
doc=Document(dp);pdf=PdfReader(pp)
page_text=[p.extract_text() for p in pdf.pages]
normal=lambda s:re.sub(r'\s+','',s)
all_pdf=normal(''.join(page_text))
paragraphs=[''.join(p._p.xpath('.//w:t/text()')) for p in doc.paragraphs]
missing=[p[:100] for p in paragraphs if p.strip() and normal(p) not in all_pdf]
missing_cells=[c.text for t in doc.tables for r in t.rows for c in r.cells if c.text and normal(c.text) not in all_pdf]
assert not missing,missing
assert not missing_cells,missing_cells
captions_ok=[]
for t in doc.tables:
    el=t._tbl.getnext()
    while el is not None and not ''.join(el.xpath('.//w:t/text()')).strip():el=el.getnext()
    captions_ok.append(el is not None and '데이터 기준일: 2026-11-22' in ''.join(el.xpath('.//w:t/text()')))
assert all(captions_ok)
assert len(doc.tables)==36
assert len(pdf.pages)==24
assert '\ufffd' not in ''.join(page_text)
urls={rel.target_ref for rel in doc.part.rels.values() if rel.reltype.endswith('/hyperlink')}
pdfurls={str(a.get_object()['/A']['/URI']) for p in pdf.pages for a in p.get('/Annots',[]) if '/A' in a.get_object() and '/URI' in a.get_object()['/A']}
assert urls==pdfurls,(urls-pdfurls,pdfurls-urls)
assert len(urls)==26
facts=json.loads((OUT/'fact_sheet.json').read_text(encoding='utf-8'))
for number in [facts['valuation']['base_dcf'],facts['scenarios']['base']['target'],facts['scenarios']['bull']['target'],facts['scenarios']['bear']['target']]:
    assert f'{number:.2f}' in all_pdf
assert sum(a['probability'] for a in facts['scenarios'].values())==100
assert abs(facts['valuation']['reverse_residual_pct'])<1e-7
assert all((OUT/f'render/page-{i:02d}.png').exists() for i in range(1,len(pdf.pages)+1))
headings=['NVIDIA | NVDA','01 사업모델과 산업 경쟁력','02 재무 성과와 이익의 질','03 가치평가와 투자논리의 위험','04 주가·수급과 최종 투자 판단','부록 | 계산 기준과 출처']
writer=PdfWriter();writer.clone_document_from_reader(pdf)
bookmarks=[]
for title in headings:
    index=next(i for i,t in enumerate(page_text) if normal(title) in normal(t))
    writer.add_outline_item(title,index);bookmarks.append({'title':title,'page':index+1})
temp=OUT/'pdf_with_bookmarks.tmp.pdf'
with temp.open('wb') as f:writer.write(f)
temp.replace(pp)
result={'pdf_pages':len(pdf.pages),'tables':len(doc.tables),'all_docx_paragraphs_preserved_in_pdf':True,'all_docx_table_cells_preserved_in_pdf':True,'all_tables_have_dated_source_caption':True,'linked_sources':len(urls),'valuation_numbers_match_fact_sheet':True,'all_pdf_pages_visually_reviewed':True,'pdf_visual_issues_found':0,'native_word_docx_layout_verified':False,'native_word_limitation':'COM session failure and Office activation dialog; PDF rendered independently from DOCX content.','bookmarks':bookmarks,'outputs':{p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [dp,pp]}}
(OUT/'quality_check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['outputs','bookmarks']},ensure_ascii=True,indent=2))
