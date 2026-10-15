"""밝은 채움 이름표(노란 박스) 안 글자 교체. 좌우 끝에서 이어지는(타일 반복) 이름표 지원"""
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILL=np.array([255,254,191])
def spans(rgb,y0,y1):
    lit=(rgb[y0:y1].astype(int).sum(2)>550).any(0)
    out=[];x=0;W=len(lit)
    while x<W:
        if not lit[x]: x+=1;continue
        s=x
        while x<W and lit[x]: x+=1
        out.append([s,x])
    return out
def patch(rgb,y0,y1,labels,color=(30,24,16),fontfile='NanumSquareNeo-cBd.ttf',size=11):
    """labels: [(span_index_or_wrap, text)] ; span 순서는 왼쪽부터. 'wrap'은 오른쪽 끝+왼쪽 끝 이어붙임"""
    W=rgb.shape[1];out=rgb.copy()
    sp=spans(rgb,y0,y1)
    # 내부 정리: 테두리(바깥 2px) 제외하고 어두운 글자 픽셀을 채움색으로
    def clean(x0,x1):
        for x in range(x0,x1):
            for y in range(y0+1,y1-1):
                if out[y,x].astype(int).sum()<600: out[y,x]=FILL
    for s in sp: clean(s[0]+1 if s[0]>0 else 0, s[1]-1 if s[1]<W else W)
    f=ImageFont.truetype(os.path.join(ROOT,fontfile),size*4)
    def draw(cx0,cx1,text):
        width=cx1-cx0;tw=f.getlength(text)/4
        big=Image.new('L',(width*4,(y1-y0)*4),0);dr=ImageDraw.Draw(big)
        asc,desc=f.getmetrics();dr.text(((width*4-tw*4)/2,((y1-y0)*4-(asc+desc))/2),text,font=f,fill=255)
        a=np.asarray(big.resize((width,y1-y0),Image.LANCZOS),np.float32)/255
        return a
    for key,text in labels:
        if key=='wrap':
            L=[s for s in sp if s[0]==0][0];R=[s for s in sp if s[1]==W][0]
            width=(W-R[0])+L[1];a=draw(0,width,text)
            for xx in range(width):
                X=(R[0]+xx)%W
                for yy in range(y1-y0):
                    v=a[yy,xx]
                    if v>0.03: out[y0+yy,X]=(out[y0+yy,X]*(1-v)+np.array(color)*v).astype(np.uint8)
        else:
            s=sp[key];a=draw(s[0],s[1],text)
            for xx in range(s[1]-s[0]):
                for yy in range(y1-y0):
                    v=a[yy,xx]
                    if v>0.03: out[y0+yy,s[0]+xx]=(out[y0+yy,s[0]+xx]*(1-v)+np.array(color)*v).astype(np.uint8)
    return out,sp
