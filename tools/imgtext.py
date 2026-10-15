"""이미지 내 글자 줄 영역 자동 검출 + 지우기 + 한글 그리기"""
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def text_mask(rgb):
    g=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY).astype(np.int16)
    bg=cv2.medianBlur(g.astype(np.uint8),15).astype(np.int16)
    hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)
    m=((g-bg)>45)&(g>110)
    return m.astype(np.uint8)
def detect_lines(rgb,minh=5,maxh=26):
    m=text_mask(rgb)
    k=cv2.getStructuringElement(cv2.MORPH_RECT,(7,3))
    d=cv2.dilate(m,k)
    n,lab,st,_=cv2.connectedComponentsWithStats(d)
    boxes=[]
    for i in range(1,n):
        x,y,w,h,a=st[i]
        if minh<=h<=maxh and w>=6 and m[y:y+h,x:x+w].sum()>=8: boxes.append([int(x),int(y),int(w),int(h)])
    boxes.sort(key=lambda b:(b[1]//6,b[0]))
    return boxes,m
def annotate(rgb,boxes,path,scale=2):
    im=Image.fromarray(rgb).resize((rgb.shape[1]*scale,rgb.shape[0]*scale),Image.NEAREST);dr=ImageDraw.Draw(im)
    for i,(x,y,w,h) in enumerate(boxes):
        dr.rectangle([x*scale,y*scale,(x+w)*scale,(y+h)*scale],outline=(0,255,0))
        dr.text((x*scale,max(0,y*scale-10)),str(i),fill=(255,255,0))
    im.save(path)
def erase(rgb,box,m,pad=1):
    x,y,w,h=box;H,W=m.shape
    x0,y0,x1,y1=max(0,x-pad),max(0,y-pad),min(W,x+w+pad),min(H,y+h+pad)
    mm=np.zeros_like(m);mm[y0:y1,x0:x1]=cv2.dilate(m,np.ones((3,3),np.uint8))[y0:y1,x0:x1]
    return cv2.inpaint(rgb,mm*255,3,cv2.INPAINT_TELEA)
def draw_text(rgb,box,text,color,fontfile='NanumSquareNeo-bRg.ttf',size=None,align='left'):
    x,y,w,h=box;SS=4
    size=size or max(8,h)
    f=ImageFont.truetype(os.path.join(ROOT,fontfile),size*SS)
    tw=f.getlength(text)/SS
    while tw>w+2 and size>7:
        size-=1;f=ImageFont.truetype(os.path.join(ROOT,fontfile),size*SS);tw=f.getlength(text)/SS
    sx=1.0 if tw<=w+2 else (w+2)/tw
    big=Image.new('L',(int((tw+4)*SS),int((h+6)*SS)),0);dr=ImageDraw.Draw(big)
    asc,desc=f.getmetrics();dr.text((0,(h+6)*SS/2-(asc+desc)/2),text,font=f,fill=255)
    tgt_w=max(1,int(round((tw+4)*sx)));a=np.asarray(big.resize((tgt_w,h+6),Image.LANCZOS),np.float32)/255
    ox=x if align=='left' else x+(w-tgt_w)//2
    oy=y-3;out=rgb.astype(np.float32)
    H,W=rgb.shape[:2]
    for yy in range(a.shape[0]):
        for xx in range(a.shape[1]):
            Y,X=oy+yy,ox+xx
            if 0<=Y<H and 0<=X<W and a[yy,xx]>0: out[Y,X]=out[Y,X]*(1-a[yy,xx])+np.array(color)*a[yy,xx]
    return out.clip(0,255).astype(np.uint8)
