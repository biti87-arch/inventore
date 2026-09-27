"""Estrae il testo paragrafo per paragrafo dai .docx in docx/ -> txt/ (una riga per paragrafo)."""
import zipfile,re,html,os
R=os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(R,'txt'),exist_ok=True)
for f in os.listdir(os.path.join(R,'docx')):
    if not f.endswith('.docx'): continue
    x=zipfile.ZipFile(os.path.join(R,'docx',f)).read('word/document.xml').decode()
    ps=[html.unescape(''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>',p))) for p in re.findall(r'<w:p[ >].*?</w:p>',x,re.S)]
    open(os.path.join(R,'txt',f[:-5]+'.txt'),'w',encoding='utf8').write('\n'.join(ps))
    print(f,len(ps))
