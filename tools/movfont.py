"""menu_mv.bin 내 영상 자막 폰트(청크1~10, 512x512 4bpp, 20x16 셀, 25열x32행) 패치"""
import numpy as np,struct
import menumv,kelfont
def patch(raw,glyphs):
    """glyphs: {sjis코드: 16x20 uint8(0~15)}"""
    items=menumv.unpack(raw);sheets={}
    def px(s):
        if s not in sheets:
            t=items[1+s][1];hs=struct.unpack_from('<H',t,0x10+0xc)[0];img=0x10+hs
            r=np.frombuffer(t[img:img+512*512//2],np.uint8);p=np.empty(r.size*2,np.uint8);p[0::2]=r&15;p[1::2]=r>>4
            sheets[s]=(p.reshape(512,512),img)
        return sheets[s][0]
    for code,g in glyphs.items():
        idx=kelfont.code2idx(code);s=idx//800;r=(idx%800)//25;c=idx%25
        px(s)[r*16:r*16+16,c*20:c*20+20]=g
    for s,(p,img) in sheets.items():
        f=p.reshape(-1);rawb=(f[0::2]|(f[1::2]<<4)).astype(np.uint8).tobytes()
        t=bytearray(items[1+s][1]);t[img:img+len(rawb)]=rawb;items[1+s]=('z',bytes(t))
    return menumv.pack(items)
