"""한글 16x16 2bpp 글리프 렌더러"""
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SS=8
def make(fontfile,size=15.0,yoff=0.0,xoff=0.0,th=(0.20,0.42,0.62),bold=0):
    f=ImageFont.truetype(os.path.join(ROOT,fontfile),int(round(size*SS)))
    def render(ch):
        W=16*SS;im=Image.new('L',(W,W),0);dr=ImageDraw.Draw(im)
        bb=dr.textbbox((0,0),ch,font=f)
        # 가로 중앙, 세로는 글꼴 em 기준(전 글자 공통 기준선)
        x=(W-(bb[2]-bb[0]))/2-bb[0]+xoff*SS
        asc,desc=f.getmetrics();y=(W-(asc+desc))/2+yoff*SS
        dr.text((x,y),ch,font=f,fill=255,stroke_width=bold,stroke_fill=255)
        a=np.asarray(im,np.float32)/255
        cov=a.reshape(16,SS,16,SS).mean(axis=(1,3))
        g=np.zeros((16,16),np.uint8)
        g[cov>th[0]]=1;g[cov>th[1]]=2;g[cov>th[2]]=3
        return g
    return render

def make4(fontfile,size=17.0,W=20,H=16,yoff=0.0,gamma=0.8):
    """영상 자막용 4bpp(0~15) 글리프, W x H 칸"""
    f=ImageFont.truetype(os.path.join(ROOT,fontfile),int(round(size*SS)))
    def render(ch):
        im=Image.new('L',(W*SS,H*SS),0);dr=ImageDraw.Draw(im)
        bb=dr.textbbox((0,0),ch,font=f)
        x=(W*SS-(bb[2]-bb[0]))/2-bb[0]
        asc,desc=f.getmetrics();y=(H*SS-(asc+desc))/2+yoff*SS
        dr.text((x,y),ch,font=f,fill=255)
        a=np.asarray(im,np.float32)/255
        cov=a.reshape(H,SS,W,SS).mean(axis=(1,3))
        return np.clip(np.round((cov**gamma)*15),0,15).astype(np.uint8)
    return render
