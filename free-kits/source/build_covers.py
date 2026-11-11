import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
F="/usr/share/fonts/opentype/inter/"
def font(n,s): return ImageFont.truetype(F+n,s)
def cover(p1,p2,kicker,title,sub,out,size=(1280,720)):
    W,H=size; im=Image.new("RGB",size,"#FBF7EF"); d=ImageDraw.Draw(im)
    d.ellipse((W-520,-200,W+180,420),fill="#F7E3C4"); d.ellipse((-160,H-260,300,H+200),fill="#F6D5CB")
    for x in range(30,W,34):
        for y in range(30,H,34): d.ellipse((x,y,x+3,y+3),fill="#EFE6D6")
    pages=[Image.open(p) for p in (p2,p1)]
    ph=int(H*0.80) if W>H else int(H*0.48)
    for i,pg in enumerate(pages):
        pg=pg.convert("RGB"); pg=pg.resize((int(pg.width*ph/pg.height),ph))
        ang=8 if i==0 else -4
        sh=Image.new("RGBA",(pg.width+60,pg.height+60),(0,0,0,0)); ImageDraw.Draw(sh).rectangle((30,30,pg.width+30,pg.height+30),fill=(0,0,0,70)); sh=sh.filter(ImageFilter.GaussianBlur(14)).rotate(ang,expand=True)
        r=pg.convert("RGBA").rotate(ang,expand=True)
        if W>H: x=W-r.width-60-(0 if i==0 else 170); y=(H-r.height)//2+(10 if i==0 else 20)
        else: x=W//2-r.width//2+(110 if i==0 else -60); y=H-r.height-50
        im.paste(sh,(x-10,y+8),sh); im.paste(r,(x,y),r)
    d=ImageDraw.Draw(im)
    tx=70; ty=110 if W>H else 80; maxw=560 if W>H else W-140
    d.rounded_rectangle((tx,ty,tx+250,ty+46),23,fill="#E07A5F"); d.text((tx+125,ty+23),kicker,font=font("Inter-ExtraBold.otf",20),fill="white",anchor="mm")
    ty+=80; tf=font("InterDisplay-Bold.otf",66 if W>H else 76)
    words=title.split(); line=""; lines=[]
    for w in words:
        t=(line+" "+w).strip()
        if d.textlength(t,font=tf)>maxw: lines.append(line); line=w
        else: line=t
    lines.append(line)
    for l in lines: d.text((tx,ty),l,font=tf,fill="#0F4C4A"); ty+=tf.size+6
    ty+=18; sf=font("Inter-Medium.otf",26)
    for l in sub: d.text((tx,ty),"✓  "+l if False else "•  "+l,font=sf,fill="#1F2A2A"); ty+=40
    d.text((tx,H-60) if W>H else (tx,ty+14),"REDRAFT STUDIO",font=font("Inter-Bold.otf",18),fill="#6b7878")
    im.save(out)
for kit,kick,title,sub in [("FREE-IEP-Meeting-Prep-Kit","FREE PRINTABLE","IEP Meeting Prep Kit",["2-week countdown checklist","24 questions to ask","One-page meeting script"]),
 ("FREE-Label-Cheat-Sheet-and-Spice-Blends","FREE PRINTABLE","Diabetes Label-Reading Cheat Sheet",["Spot hidden sugars fast","5 no-sugar spice blends","Budget pantry checklist"])]:
    cover(kit+"-p-1.png",kit+"-p-2.png",kick,title,sub,kit+"-cover.png")
    cover(kit+"-p-1.png",kit+"-p-2.png",kick,title,sub,kit+"-thumb.png",(1000,1000))
