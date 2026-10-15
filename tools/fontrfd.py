"""fontdata*.bin/rfd (rfd 컨테이너 + TIM2 4bpp 시트) 파서"""
import struct
from PIL import Image
def parse(d):
    assert d[:11]==b'fontdatarfd'
    n=struct.unpack_from('<H',d,0x10)[0]
    offs=[struct.unpack_from('<I',d,0x14+4*i)[0] for i in range(n)]
    sheets=[]
    for o in offs:
        name=d[o:o+16].split(b'\0')[0];t=o+0x10
        assert d[t:t+3]==b'TIM'
        p=t+0x10
        tot,clsz,imsz,hsz,ncol,fmt,mip,clt,imt,w,h=struct.unpack_from('<IIIHHBBBBHH',d,p)
        img_off=p+hsz;clut_off=img_off+imsz
        sheets.append(dict(name=name,img=img_off,clut=clut_off,w=w,h=h,imsz=imsz,ncol=ncol,imt=imt))
    return sheets
def to_png(d,s,path):
    w,h=s['w'],s['h'];raw=d[s['img']:s['img']+w*h//2]
    px=bytearray()
    for b in raw: px+=bytes(((b&15)*17,(b>>4)*17))
    Image.frombytes('L',(w,h),bytes(px)).save(path)
