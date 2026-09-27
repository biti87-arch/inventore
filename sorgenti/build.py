"""Genera l'app a partire da template.html e dai dati JSON.
Uso: python3 sorgenti/build.py [percorso_versione_web]
- scrive www/index.html (app Android/Windows, font locali, funziona offline)
- se indicato, scrive anche la versione web con i font di Google Fonts."""
import json, sys, os, re
R=os.path.dirname(os.path.abspath(__file__))
t=open(os.path.join(R,'template.html'),encoding='utf8').read()
mini=lambda f: json.dumps(json.load(open(os.path.join(R,f),encoding='utf8')),ensure_ascii=False,separators=(',',':'))
t=t.replace('__DATI__',mini('inventore.json')).replace('__ARMI__',mini('armi.json'))
if len(sys.argv)>1: open(sys.argv[1],'w',encoding='utf8').write(t)
fonts=re.compile(r'<link rel="preconnect"[^>]*>\n<link rel="preconnect"[^>]*>\n<link rel="stylesheet" href="https://fonts.googleapis.com[^>]*>')
assert fonts.search(t)
body=fonts.sub('<link rel="stylesheet" href="vendor/fonts.css">\n<link rel="icon" href="icona.png">',t)
head='''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>
'''
i=body.index('<div class="wrap">')
out=head+body[:i]+'</head>\n<body>\n'+body[i:]+'\n</body>\n</html>\n'
open(os.path.join(R,'..','www','index.html'),'w',encoding='utf8').write(out)
print('ok', len(out))
