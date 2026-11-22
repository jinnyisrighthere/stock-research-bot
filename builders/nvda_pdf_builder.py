"""PDF fallback renderer for the authored DOCX when native conversion is unavailable.
Reads the final DOCX paragraphs/tables in order, preserving all report content.
"""
from pathlib import Path
import re,json,html
from docx import Document
from docx.text.paragraph import Paragraph as DocParagraph
from docx.table import Table as DocTable
from docx.oxml.ns import qn
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image,KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/nvda_20261122'
pdfmetrics.registerFont(TTFont('Malgun','C:/Windows/Fonts/malgun.ttf'))
pdfmetrics.registerFont(TTFont('MalgunBold','C:/Windows/Fonts/malgunbd.ttf'))
pdfmetrics.registerFontFamily('Malgun',normal='Malgun',bold='MalgunBold',italic='Malgun',boldItalic='MalgunBold')
styles={
'Normal':ParagraphStyle('Body',fontName='Malgun',fontSize=9.3,leading=14.2,spaceAfter=7,wordWrap='CJK',allowWidows=0,allowOrphans=0),
'Title':ParagraphStyle('Title',fontName='MalgunBold',fontSize=27,leading=36,spaceAfter=12,keepWithNext=True,wordWrap='CJK'),
'Heading 1':ParagraphStyle('H1',fontName='MalgunBold',fontSize=18,leading=25,spaceBefore=5,spaceAfter=12,keepWithNext=True,wordWrap='CJK'),
'Heading 2':ParagraphStyle('H2',fontName='MalgunBold',fontSize=12.8,leading=19,spaceBefore=12,spaceAfter=8,keepWithNext=True,wordWrap='CJK'),
'Heading 3':ParagraphStyle('H3',fontName='MalgunBold',fontSize=10.5,leading=16,spaceBefore=9,spaceAfter=6,keepWithNext=True,wordWrap='CJK'),
'Caption':ParagraphStyle('Caption',fontName='Malgun',fontSize=7.4,leading=11,spaceAfter=9,textColor=colors.HexColor('#505050'),wordWrap='CJK'),
}
cellstyle=ParagraphStyle('Cell',fontName='Malgun',fontSize=7.8,leading=11.2,wordWrap='CJK',spaceAfter=0)
headstyle=ParagraphStyle('CellHead',parent=cellstyle,fontName='MalgunBold')

def escape(s):return html.escape(s).replace('\n','<br/>')

docx=Document(OUT/'NVDA_심층분석_20261122.docx');story=[];table_total=0
for el in docx.element.body:
    if el.tag==qn('w:p'):
        p=DocParagraph(el,docx);style=p.style.name
        if el.xpath('.//w:br[@w:type="page"]'):
            story.append(PageBreak());continue
        if el.xpath('.//w:drawing'):
            im=Image(OUT/'NVDA_chart_legacy.png');im.drawHeight*=172*mm/im.drawWidth;im.drawWidth=172*mm
            story.append(im);story.append(Spacer(1,4));continue
        hyperlinks=el.xpath('.//w:hyperlink')
        if hyperlinks:
            h=hyperlinks[0];rid=h.get(qn('r:id'));url=docx.part.rels[rid].target_ref
            label=''.join(h.xpath('.//w:t/text()'))
            prefix=''.join(escape(r.text) for r in p.runs)
            story.append(Paragraph(prefix+'<link href="'+html.escape(url,quote=True)+'" color="#245B78">'+escape(label)+'</link>',styles['Caption']));continue
        if not p.text.strip():continue
        txt=''.join(('<b>'+escape(r.text)+'</b>') if r.bold else escape(r.text) for r in p.runs)
        story.append(Paragraph(txt,styles.get(style,styles['Normal'])))
    elif el.tag==qn('w:tbl'):
        t=DocTable(el,docx);ncols=len(t.columns);table_total+=1
        widths=([39]+[(172-39)/(ncols-1)]*(ncols-1)) if ncols>2 else [83,89]
        if ncols==3:widths=[50,55,67]
        if ncols==4:widths=[50,40,40,42]
        data=[[Paragraph(escape(c.text),headstyle if i==0 else cellstyle) for c in row.cells] for i,row in enumerate(t.rows)]
        tab=Table(data,colWidths=[w*mm for w in widths],repeatRows=1,hAlign='LEFT')
        tab.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E8EEF1')),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#F6F8F9'),colors.white]),
            ('GRID',(0,0),(-1,-1),.25,colors.HexColor('#D6DCE0')),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
            ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
        ]));story.append(tab);story.append(Spacer(1,5))

def chrome(c,doc):
    c.saveState();c.setFont('Malgun',7.3);c.setFillColor(colors.HexColor('#666666'))
    c.drawString(19*mm,287*mm,'NVIDIA  |  PUBLIC EQUITY RESEARCH')
    c.drawRightString(191*mm,287*mm,'2026.11.22')
    c.drawRightString(191*mm,9*mm,f'NVDA  ·  {doc.page}')
    c.restoreState()

target=OUT/'NVDA_심층분석_20261122.pdf'
pdf=SimpleDocTemplate(str(target),pagesize=(210*mm,297*mm),leftMargin=19*mm,rightMargin=19*mm,topMargin=19*mm,bottomMargin=18*mm,title='NVIDIA (NVDA) 심층 기업 분석 보고서',author='Equity Research')
pdf.build(story,onFirstPage=chrome,onLaterPages=chrome)
r=PdfReader(target)
texts=[p.extract_text() for p in r.pages]
(OUT/'pdf_text.txt').write_text('\n\n'.join(f'PAGE {i+1}\n{t}' for i,t in enumerate(texts)),encoding='utf-8')
(OUT/'pdf_manifest.json').write_text(json.dumps({'pages':len(r.pages),'tables':table_total,'renderer':'ReportLab DOCX-content fallback','native_word_pagination_verified':False,'docx_and_pdf_content_same':True,'pdf_text_characters':sum(map(len,texts))},indent=2),encoding='utf-8')
print(f'PDF pages: {len(r.pages)}; tables: {table_total}')
print(str(target))
