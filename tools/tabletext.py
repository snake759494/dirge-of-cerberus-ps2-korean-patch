"""조작표 이미지: 행(band)별 열 최빈값 배경 복원 → 글자 묶음 검출/지우기/한글 그리기"""
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def bands(rgb):
    lum=rgb.mean(2)
    dark=(lum<30).mean(1)>0.6
    out=[];y=0;H=len(dark)
    while y<H:
        if dark[y]: y+=1;continue
        s=y
        while y<H and not dark[y]: y+=1
        if y-s>=7: out.append((s,y))
    return out
def refrow(blk):
    # 띠 안에서 글자 없는 기준 행 선택: 열 최빈값과 가장 가까운 행
    m=colmode(blk).astype(int)
    d=[np.abs(blk[r].astype(int)-m).max(1).mean() for r in range(blk.shape[0])]
    return blk[int(np.argmin(d))].copy()
def colmode(blk):
    # 각 열의 최빈 색
    h,w,_=blk.shape;bg=np.zeros((w,3),np.uint8)
    for x in range(w):
        col=[tuple(c) for c in blk[:,x]]
        vals,cnt=np.unique(np.array(col),axis=0,return_counts=True)
        bg[x]=vals[cnt.argmax()]
    return bg
def band_bgs(rgb):
    """같은 줄무늬 패턴의 띠들을 묶어 열별 최빈값으로 깨끗한 배경 행 생성"""
    B=bands(rgb);refs=[refrow(rgb[y0:y1]).astype(int) for y0,y1 in B]
    groups=[]
    for i,r in enumerate(refs):
        for g in groups:
            if (np.abs(refs[g[0]]-r).max(1)<12).mean()>0.6: g.append(i);break
        else: groups.append([i])
    bg={}
    for g in groups:
        rows=[]
        for i in g:
            y0,y1=B[i];blk=rgb[y0:y1].astype(int)
            d=np.abs(blk-refs[g[0]][None]).max(2)>28
            for r in (1,2,blk.shape[0]-2):
                rows.append(blk[r])
        stack=np.array(rows)
        m=np.zeros_like(refs[g[0]])
        for x in range(stack.shape[1]):
            vals,cnt=np.unique(stack[:,x],axis=0,return_counts=True);m[x]=vals[cnt.argmax()]
        for i in g: bg[i]=m.astype(np.uint8)
    return B,bg
def segments(rgb,gap=7):
    res=[];B,BG=band_bgs(rgb)
    for bi,(y0,y1) in enumerate(B):
        blk=rgb[y0:y1].astype(int);bg=BG[bi]
        diff=np.abs(blk-bg[None]).max(2)>28
        border=diff.mean(1)>0.5;border[2:-2]=False
        diff[border]=False
        sep=(blk.mean(2)<45).mean(0)>0.85      # 칸 구분선: 행 전체가 어두운 열
        W=len(sep);x=0
        while x<W:
            if sep[x]: x+=1;continue
            c0=x
            while x<W and not sep[x]: x+=1
            c1=x
            cols=np.nonzero(diff[:,c0:c1].any(0))[0]
            if len(cols)>=3 and diff[:,c0:c1].sum()>=10:
                res.append(dict(box=[int(c0+cols[0]),int(y0),int(cols[-1]-cols[0]+1),int(y1-y0)],cell=[int(c0),int(c1)],bg=bg.tolist()))
    return res
def annotate(rgb,segs,path,scale=3):
    im=Image.fromarray(rgb).resize((rgb.shape[1]*scale,rgb.shape[0]*scale),Image.NEAREST);dr=ImageDraw.Draw(im)
    for i,s in enumerate(segs):
        x,y,w,h=s['box'];dr.rectangle([x*scale,y*scale,(x+w)*scale-1,(y+h)*scale-1],outline=(0,255,0))
        dr.text((x*scale+1,y*scale-1),str(i),fill=(255,255,0))
    im.save(path)
def render(rgb,seg,text,color=(10,10,10),fontfile='NanumSquareNeo-bRg.ttf',xpad=0,outline=(205,200,200)):
    x,y,w,h=seg['box'];out=rgb.copy()
    bgall=np.array(seg['bg'],np.uint8);c0,c1=seg['cell']
    blk=out[y:y+h,c0:c1].astype(int)
    diff=np.abs(blk-bgall[None,c0:c1].astype(int)).max(2)>28
    border=diff.mean(1)>0.5;border[2:-2]=False
    ex0=max(c0,x-2);ex1=c1
    for r in range(h):
        if not border[r]: out[y+r,ex0:ex1]=bgall[ex0:ex1]
    w=c1-x-1
    SS=4;size=h-1
    def mk(sz): return ImageFont.truetype(os.path.join(ROOT,fontfile),sz*SS)
    f=mk(size);tw=f.getlength(text)/SS
    maxw=w+xpad
    while tw>maxw and size>8: size-=1;f=mk(size);tw=f.getlength(text)/SS
    sx=min(1.0,maxw/tw) if tw>0 else 1
    asc,desc=f.getmetrics()
    big=Image.new('L',(int(tw*SS)+8,h*SS),0);ImageDraw.Draw(big).text((0,(h*SS-(asc+desc))/2),text,font=f,fill=255)
    tw2=max(1,int(round(tw*sx)));a=np.asarray(big.resize((tw2+2,h),Image.LANCZOS),np.float32)/255
    a=np.clip(a*1.2,0,1)
    import cv2
    ol=cv2.dilate((a>0.25).astype(np.uint8),np.ones((3,3),np.uint8)).astype(np.float32)*0.85
    W=out.shape[1];oc=np.array(outline,np.float32) if outline is not None else None
    for yy in range(h):
        for xx in range(a.shape[1]):
            X=x+xx
            if X>=W: continue
            px=out[y+yy,X].astype(np.float32)
            if oc is not None and ol[yy,xx]>0: px=px*(1-ol[yy,xx])+oc*ol[yy,xx]
            if a[yy,xx]>0.02: px=px*(1-a[yy,xx])+np.array(color,np.float32)*a[yy,xx]
            out[y+yy,X]=px.clip(0,255).astype(np.uint8)
    return out

def apply_table(rgb,mapping):
    """mapping: {'x,y': 한글} 좌표 근사(±3px) 매칭으로 칸마다 한글 렌더링. 반환 (이미지, 누락키)"""
    segs=segments(rgb);out=rgb.copy();miss=[]
    for k,t in mapping.items():
        kx,ky=map(int,k.split(','))
        c=[s for s in segs if abs(s['box'][0]-kx)<=3 and abs(s['box'][1]-ky)<=3]
        if not c: miss.append(k);continue
        out=render(out,c[0],t)
    return out,miss
