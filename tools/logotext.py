"""타이틀 로고 위 가타카나 줄(RGBA, 좌우 반복 타일) 교체"""
import numpy as np,os
from PIL import Image,ImageDraw,ImageFont
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def render(rgba,y0,y1,x0,width,text,fontfile='NanumSquareNeo-dEb.ttf',alpha=128,clear=(0,27),boxes=None):
    out=rgba.copy();W=out.shape[1];H=y1-y0
    if boxes:
        for bx0,by0,bx1,by1 in boxes: out[by0:by1,bx0:bx1]=0
    else:
        out[clear[0]:clear[1]+1,:,3]=0;out[clear[0]:clear[1]+1,:,:3]=0
    SS=4;size=H
    def mk(s): return ImageFont.truetype(os.path.join(ROOT,fontfile),s*SS)
    f=mk(size)
    while f.getlength(text)/SS>width-4 and size>8: size-=1;f=mk(size)
    tw=f.getlength(text)/SS;asc,desc=f.getmetrics()
    big=Image.new('L',(width*SS,H*SS),0)
    ImageDraw.Draw(big).text(((width-tw)/2*SS,(H*SS-(asc+desc))/2),text,font=f,fill=255)
    m=np.asarray(big.resize((width,H),Image.LANCZOS),np.float32)/255
    for xx in range(width):
        X=(x0+xx)%W
        for yy in range(H):
            v=m[yy,xx]
            if v>0.04:
                out[y0+yy,X,:3]=255;out[y0+yy,X,3]=max(out[y0+yy,X,3],int(round(alpha*min(1,v*1.1))))
    return out

def render_crisp(rgba,x0,y0,width,height,text,boxes,fontfile='NanumSquareNeo-eHv.ttf',size=14,hscale=0.86,core=128,edge=70,ring=36):
    """작은 크기 가독성 우선: 굵은 글꼴 + 가로 압축 + 코어/가장자리/외곽 링 3단 알파"""
    import cv2
    out=rgba.copy();W=out.shape[1]
    for bx0,by0,bx1,by1 in boxes: out[by0:by1,bx0:bx1]=0
    SS=8;f=ImageFont.truetype(os.path.join(ROOT,fontfile),size*SS)
    tw=f.getlength(text);asc,desc=f.getmetrics()
    big=Image.new('L',(int(tw)+SS*4,height*SS),0)
    bb=ImageDraw.Draw(big).textbbox((0,0),text,font=f)
    ImageDraw.Draw(big).text((SS*2,(height*SS-(bb[3]-bb[1]))/2-bb[1]),text,font=f,fill=255)
    tgt_w=int(round(big.width/SS*hscale))
    while tgt_w>width and hscale>0.6:
        hscale-=0.02;tgt_w=int(round(big.width/SS*hscale))
    m=np.asarray(big.resize((tgt_w,height),Image.BOX),np.float32)/255
    a=np.zeros_like(m);a[m>0.5]=core;a[(m>0.18)&(m<=0.5)]=edge
    r=cv2.dilate((m>0.18).astype(np.uint8),np.ones((3,3),np.uint8)).astype(bool)&(a==0)
    a[r]=ring
    ox=x0+(width-tgt_w)//2
    for xx in range(tgt_w):
        X=(ox+xx)%W
        for yy in range(height):
            if a[yy,xx]>0: out[y0+yy,X,:3]=255;out[y0+yy,X,3]=int(a[yy,xx])
    return out
