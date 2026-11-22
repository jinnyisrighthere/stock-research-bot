"""Render the sequential NVDA manuscript to a styled DOCX.
The sibling PowerShell exporter produces a matching PDF using Word.
"""
from pathlib import Path
import re,json
from docx import Document
from docx.shared import Mm,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/nvda_20261122'
doc=Document()
sec=doc.sections[0]
sec.page_width=Mm(210);sec.page_height=Mm(297)
sec.top_margin=Mm(19);sec.bottom_margin=Mm(18)
sec.left_margin=Mm(19);sec.right_margin=Mm(19)
sec.header_distance=Mm(8);sec.footer_distance=Mm(8)

def font(style,size,bold=False,color='000000'):
    style.font.name='Malgun Gothic';style.font.size=Pt(size)
    style.font.bold=bold;style.font.color.rgb=RGBColor.from_string(color)
    style.element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'맑은 고딕')

font(doc.styles['Normal'],10)
p=doc.styles['Normal'].paragraph_format
p.line_spacing=1.2;p.space_after=Pt(6);p.widow_control=True
for name,size in [('Title',28),('Heading 1',19),('Heading 2',13),('Heading 3',11)]:
    font(doc.styles[name],size,True)
    f=doc.styles[name].paragraph_format
    f.space_before=Pt(12 if name!='Title' else 0);f.space_after=Pt(7)
    f.keep_with_next=True
font(doc.styles['Caption'],8,False,'505050')
doc.styles['Caption'].paragraph_format.space_after=Pt(8)
doc.styles['Caption'].paragraph_format.line_spacing=1.1
font(doc.styles['Header'],8,False,'666666');font(doc.styles['Footer'],8,False,'666666')
head=sec.header.paragraphs[0]
head.text='NVIDIA  |  PUBLIC EQUITY RESEARCH                                         2026.11.22'
foot=sec.footer.paragraphs[0];foot.alignment=WD_ALIGN_PARAGRAPH.RIGHT
foot.add_run('NVDA  ·  ')
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');foot._p.append(field)

def inline(p,text):
    for j,chunk in enumerate(re.split(r'\*\*(.*?)\*\*',text)):
        run=p.add_run(chunk);run.bold=(j%2==1)

def hyperlink(p,url):
    from urllib.parse import urlparse
    h=OxmlElement('w:hyperlink');h.set(qn('r:id'),p.part.relate_to(url,RT.HYPERLINK,is_external=True))
    r=OxmlElement('w:r');pr=OxmlElement('w:rPr')
    c=OxmlElement('w:color');c.set(qn('w:val'),'245B78');pr.append(c)
    u=OxmlElement('w:u');u.set(qn('w:val'),'single');pr.append(u)
    r.append(pr);t=OxmlElement('w:t');t.text='원문 열기  ·  '+urlparse(url).netloc;r.append(t);h.append(r);p._p.append(h)

table_count=0
def add_table(lines):
    global table_count
    rows=[[x.strip() for x in line.strip().strip('|').split('|')] for line in lines]
    rows=[r for r in rows if not all(re.fullmatch(r'[-: ]+',x) for x in r)]
    table_count+=1
    t=doc.add_table(rows=0,cols=len(rows[0]));t.autofit=False
    cols=len(rows[0]); widths=([39]+[(172-39)/(cols-1)]*(cols-1)) if cols>2 else [83,89]
    if cols==3:widths=[50,55,67]
    if cols==4:widths=[50,40,40,42]
    for col,w in zip(t.columns,widths):col.width=Mm(w)
    for i,values in enumerate(rows):
        cells=t.add_row().cells
        trpr=t.rows[-1]._tr.get_or_add_trPr()
        trpr.append(OxmlElement('w:cantSplit'))
        if i==0:
            repeat=OxmlElement('w:tblHeader');trpr.append(repeat)
        for j,(cell,value) in enumerate(zip(cells,values)):
            cell.width=Mm(widths[j]);cell.vertical_alignment=1
            tcpr=cell._tc.get_or_add_tcPr()
            margins=OxmlElement('w:tcMar')
            for side,val in [('top','75'),('bottom','75'),('left','85'),('right','85')]:
                el=OxmlElement('w:'+side);el.set(qn('w:w'),val);el.set(qn('w:type'),'dxa');margins.append(el)
            tcpr.append(margins)
            shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E8EEF1' if i==0 else ('F6F8F9' if i%2 else 'FFFFFF'));tcpr.append(shade)
            borders=OxmlElement('w:tcBorders')
            for edge in ['top','bottom','left','right']:
                e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'3');e.set(qn('w:color'),'D6DCE0');borders.append(e)
            tcpr.append(borders)
            p=cell.paragraphs[0]
            p.paragraph_format.space_after=Pt(0);p.paragraph_format.line_spacing=1.12
            p.paragraph_format.keep_with_next=(i==0)
            value=value.replace('확인 불가%','확인 불가').replace('확인 불가배','확인 불가')
            run=p.add_run(value);run.font.size=Pt(8.1 if cols>=5 else 8.7);run.bold=(i==0)
    doc.add_paragraph().paragraph_format.space_after=Pt(0)

for section_num in range(6):
    if section_num>0:doc.add_page_break()
    lines=(OUT/f'NVDA_0{section_num}.md').read_text(encoding='utf-8').splitlines()
    i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line.startswith('|'):
            block=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                block.append(lines[i]);i+=1
            add_table(block);continue
        match=re.match(r'^(#{1,3}) (.*)',line)
        if match:
            level=len(match[1]);title=match[2]
            doc.add_paragraph(title,style='Title' if section_num==0 and level==1 else f'Heading {level}')
        elif line.startswith('!['):
            filename=re.search(r'\]\((.*?)\)',line)[1]
            p=doc.add_paragraph();p.paragraph_format.keep_with_next=True
            r=p.add_run();r.add_picture(str(OUT/filename),width=Mm(171))
            for drawing in r._r.xpath('.//wp:docPr'):drawing.set('descr','NVDA 1-year close, moving averages and daily trading volume; legacy engine reference chart.')
        elif line.startswith('http'):
            last=doc.paragraphs[-1]
            if last.text.startswith('발행·자료일:'):
                last.add_run('  |  ');hyperlink(last,line)
            else:hyperlink(doc.add_paragraph(style='Caption'),line)
        elif line.startswith('데이터 기준일:') or line.startswith('발행·자료일:'):
            doc.add_paragraph(line,style='Caption')
        else:
            p=doc.add_paragraph();inline(p,line)
        i+=1

doc.core_properties.title='NVIDIA (NVDA) 심층 기업 분석 보고서'
doc.core_properties.subject='자료 기준 2026-11-22 · 주가 기준 2026-11-20'
doc.core_properties.author='Equity Research'
doc.core_properties.keywords='NVDA, DCF, financial quality, equity research'
doc.core_properties.comments=''
path=OUT/'NVDA_심층분석_20261122.docx'
doc.save(path)
(OUT/'build_manifest.json').write_text(json.dumps({'docx':str(path),'tables':table_count,'sections':6,'font':'Malgun Gothic','page':'A4','manuscript':'NVDA_research_report.md'},ensure_ascii=False,indent=2),encoding='utf-8')
print(str(path));print(f'Tables: {table_count}')
