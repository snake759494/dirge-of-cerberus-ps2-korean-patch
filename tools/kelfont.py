"""fontdata1 (kelfnt0~3) 글리프 셀 접근: SJIS 인덱스 <-> (시트,레이어,행,열), 2bpp 16x16"""
import numpy as np,struct
import fontrfd
def code2idx(c):
    h,l=c>>8,c&255
    h=h-0x81 if h<0xa0 else h-0xc1
    l=l-0x40 if l<0x7f else l-0x41
    return h*188+l
def idx2code(n):
    h=n//188;l=n%188;h=0x81+h
    if h>=0xa0: h+=0x40
    l=0x40+l
    if l>=0x7f: l+=1
    return h<<8|l
BLK={0:(0,1),16:(0,0),32:(1,1),48:(1,0)}  # 오프셋 -> (레이어, 반쪽: 1=오른쪽16칸)
def idx2cell(n):
    s=n//1792;r=(n%1792)//64;o=n%64;b=o//16*16;c=o%16
    L,half=BLK[b];return s,L,r,c+16*half
class Font:
    def __init__(s,data):
        s.d=bytearray(data);s.sheets=fontrfd.parse(data);s.px=[]
        for sh in s.sheets:
            raw=np.frombuffer(bytes(s.d[sh['img']:sh['img']+sh['w']*sh['h']//2]),np.uint8)
            p=np.empty(raw.size*2,np.uint8);p[0::2]=raw&15;p[1::2]=raw>>4
            s.px.append(p.reshape(sh['h'],sh['w']))
    def get(s,n):
        si,L,r,c=idx2cell(n);return (s.px[si][r*16:r*16+16,c*16:c*16+16]>>(2*L))&3
    def put(s,n,g):
        si,L,r,c=idx2cell(n);a=s.px[si][r*16:r*16+16,c*16:c*16+16]
        mask=np.uint8(3<<(2*L));a[:]=(a&~mask)|((g.astype(np.uint8)&3)<<(2*L))
    def tobytes(s):
        for sh,p in zip(s.sheets,s.px):
            f=p.reshape(-1);raw=(f[0::2]|(f[1::2]<<4)).astype(np.uint8)
            s.d[sh['img']:sh['img']+raw.size]=raw.tobytes()
        return bytes(s.d)
