"""이펙트(.fed/.fez) 내 8bpp TIM2 이미지 한글화: 원본 이미지 해시로 찾아 교체"""
import re,struct,hashlib,json,os
import numpy as np
import tabletext,labeltext,logotext
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def _swz(): i=np.arange(256);return (i&0xe7)|((i&0x10)>>1)|((i&0x08)<<1)
SWZ=_swz()
def tims(d):
    for m in re.finditer(rb'TIM2',d):
        p=m.start()+0x10
        try: tot,clsz,imsz,hs,ncol,fmt,mip,clt,imt,w,h=struct.unpack_from('<IIIHHBBBBHH',d,p)
        except Exception: continue
        if imt!=5 or imsz!=w*h or not(16<=w<=1024 and 16<=h<=1024): continue
        img=p+hs;clut=img+imsz
        if clut+1024>len(d): continue
        yield m.start(),w,h,img,clut
def key(d,img,clut,w,h): return hashlib.md5(d[img:img+w*h]+d[clut:clut+1024]).hexdigest()[:10]+'_%dx%d.png'%(w,h)
def decode(d,img,clut,w,h):
    pal=np.frombuffer(d[clut:clut+1024],np.uint8).reshape(256,4)[SWZ]
    idx=np.frombuffer(d[img:img+w*h],np.uint8).reshape(h,w)
    return idx,pal
def quantize(rgb,pal,orig_idx):
    """바뀐 픽셀만 팔레트 최근접 색으로(알파는 원본 인덱스 기준 유지 위해 알파 같은 색 우선)"""
    P=pal[:,:3].astype(np.int32)
    out=orig_idx.copy()
    cur=pal[orig_idx][...,:3]
    ch=np.any(cur!=rgb,axis=2)
    ys,xs=np.nonzero(ch)
    if len(ys)==0: return out
    px=rgb[ys,xs].astype(np.int32)
    alpha=pal[orig_idx[ys,xs],3]
    d=((px[:,None,:]-P[None])**2).sum(2)
    best=d.argmin(1)        # 팔레트 인덱스(스위즐 후 순서)
    out[ys,xs]=best         # decode의 pal은 이미 저장 인덱스 순서로 정렬됨
    return out
def quantize_rgba(rgba,pal,orig_idx):
    P=pal.astype(np.int32);out=orig_idx.copy()
    ch=np.any(pal[orig_idx]!=rgba,axis=2);ys,xs=np.nonzero(ch)
    if len(ys)==0: return out
    px=rgba[ys,xs].astype(np.int32)
    w=np.array([1,1,1,3],np.int32)
    d=(((px[:,None,:]-P[None])**2)*w).sum(2)
    out[ys,xs]=d.argmin(1);return out
def load_jobs():
    jobs={k:('table',v) for k,v in json.load(open(os.path.join(ROOT,'work','img','table_ko.json'),encoding='utf-8')).items()}
    gf=os.path.join(ROOT,'work','img','logo_ko.json')
    if os.path.exists(gf): jobs.update({k:('logo',v) for k,v in json.load(open(gf,encoding='utf-8')).items()})
    lf=os.path.join(ROOT,'work','img','label_ko.json')
    if os.path.exists(lf): jobs.update({k:('label',v) for k,v in json.load(open(lf,encoding='utf-8')).items()})
    return jobs
def patch_file(d,jobs,cache):
    d=bytearray(d);n=0
    for off,w,h,img,clut in list(tims(bytes(d))):
        k=key(d,img,clut,w,h)
        if k not in jobs: continue
        if k not in cache:
            idx,pal=decode(d,img,clut,w,h)
            rgb=pal[idx][...,:3].copy()
            kind,job=jobs[k]
            if kind=='logo' and job.get('crisp'):
                new=logotext.render_crisp(pal[idx].copy(),job['x0'],job['y0'],job['width'],job['height'],job['text'],job['boxes'],fontfile=job['font'],size=job['size'],edge=job.get('edge',70),ring=job.get('ring',36))
                cache[k]=quantize_rgba(new,pal,idx).tobytes();d[img:img+w*h]=cache[k];n+=1;continue
            if kind=='logo':
                new=logotext.render(pal[idx].copy(),job['y0'],job['y1'],job['x0'],job['width'],job['text'],clear=tuple(job.get('clear',(0,0))),boxes=job.get('boxes'),alpha=job.get('alpha',128))
                cache[k]=quantize_rgba(new,pal,idx).tobytes();d[img:img+w*h]=cache[k];n+=1;continue
            if kind=='table':
                new,miss=tabletext.apply_table(rgb,job)
                if miss: raise ValueError('표 칸 누락 %s %s'%(k,miss))
            else:
                new,_=labeltext.patch(rgb,job['y0'],job['y1'],[tuple(x) for x in job['labels']],size=job.get('size',11))
            cache[k]=quantize(new,pal,idx).tobytes()
        d[img:img+w*h]=cache[k];n+=1
    return bytes(d),n
