"""Genera le icone dell'app (ingranaggio d'ottone su fondo ferro brunito) per Android, Windows e web."""
from PIL import Image, ImageDraw, ImageFilter
import math, os
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
BR=(201,164,92,255); BR2=(150,112,52,255); DARK=(34,40,48,255)
def sfondo(n):
    im=Image.new('RGBA',(n,n)); px=im.load(); c=n/2
    for y in range(n):
        for x in range(n):
            d=min(1,math.hypot(x-c,y-c)/(n*0.72))
            a=(58,70,82); b=(24,28,34)
            px[x,y]=tuple(int(a[i]*(1-d)+b[i]*d) for i in range(3))+(255,)
    return im
def ingranaggio(dr,cx,cy,r,denti,col,foro,prof=0.16,larg=0.5,rot=0):
    pts=[]; N=denti*4
    for i in range(N):
        a=rot+2*math.pi*i/N; k=i%4
        rr=r if k in (1,2) else r*(1-prof)
        off=(larg*math.pi/denti)/2*(1 if k in (1,3) else -1)*0.35
        pts.append((cx+rr*math.cos(a+off),cy+rr*math.sin(a+off)))
    dr.polygon(pts,fill=col)
    if foro: dr.ellipse([cx-foro,cy-foro,cx+foro,cy+foro],fill=(0,0,0,0))
def primo_piano(n,sf=True):
    S=n*4; im=Image.new('RGBA',(S,S),(0,0,0,0)); dr=ImageDraw.Draw(im)
    s=S/1024
    ingranaggio(dr,470*s,540*s,300*s,12,BR,0)
    dr.ellipse([(470-205)*s,(540-205)*s,(470+205)*s,(540+205)*s],fill=(0,0,0,0))
    dr.ellipse([(470-150)*s,(540-150)*s,(470+150)*s,(540+150)*s],fill=BR)
    for k in range(6):
        a=math.pi/3*k+0.26
        x,y=470*s+95*s*math.cos(a),540*s+95*s*math.sin(a)
        dr.ellipse([x-30*s,y-30*s,x+30*s,y+30*s],fill=(0,0,0,0))
    dr.ellipse([(470-38)*s,(540-38)*s,(470+38)*s,(540+38)*s],fill=(0,0,0,0))
    ingranaggio(dr,735*s,290*s,150*s,9,BR2,52*s,rot=0.2)
    return im.resize((n,n),Image.LANCZOS)
def icona(n,rotonda=False):
    im=sfondo(n); fg=primo_piano(n); im.alpha_composite(fg)
    if rotonda:
        m=Image.new('L',(n*4,n*4),0); ImageDraw.Draw(m).ellipse([0,0,n*4-1,n*4-1],fill=255)
        im.putalpha(m.resize((n,n),Image.LANCZOS))
    return im
def fg_adattivo(n):
    im=Image.new('RGBA',(n,n),(0,0,0,0)); f=primo_piano(int(n*0.62)); o=(n-f.size[0])//2
    im.alpha_composite(f,(o,o)); return im
def splash(w,h,scuro=False):
    im=Image.new('RGBA',(w,h),(24,28,34,255) if scuro else (232,235,238,255))
    f=primo_piano(int(min(w,h)*0.32)); im.alpha_composite(f,((w-f.size[0])//2,(h-f.size[1])//2)); return im
icona(1024).save(f'{R}/assets/icon-only.png'); fg_adattivo(1024).save(f'{R}/assets/icon-foreground.png')
sfondo(1024).save(f'{R}/assets/icon-background.png')
splash(2732,2732).save(f'{R}/assets/splash.png'); splash(2732,2732,True).save(f'{R}/assets/splash-dark.png')
icona(512).save(f'{R}/desktop/icon.png'); icona(192).save(f'{R}/www/icona.png')
res=f'{R}/android/app/src/main/res'
for d in os.listdir(res):
    p=os.path.join(res,d)
    for fn in os.listdir(p):
        fp=os.path.join(p,fn)
        if not fn.endswith('.png'): continue
        w,h=Image.open(fp).size
        if fn=='ic_launcher.png': icona(w).save(fp)
        elif fn=='ic_launcher_round.png': icona(w,True).save(fp)
        elif fn=='ic_launcher_foreground.png': fg_adattivo(w).save(fp)
        elif fn=='ic_launcher_background.png': sfondo(w).save(fp)
        elif fn=='splash.png': splash(w,h,'night' in d).save(fp)
print('ok')
