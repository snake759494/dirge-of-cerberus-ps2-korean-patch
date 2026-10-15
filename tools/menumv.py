"""menu_mv.bin: u32 n, (u32 off,u32 size)*n
청크 = [u32 zlib크기][u32 원래크기][kelcrypt(key=7)(zlib, 8정렬) + 꼬리(u32 정렬길이,u32 체크섬)]
TIM2가 아닌 항목(마지막 표)은 원본 그대로 보존"""
import struct,zlib,kelcrypt
KEY=(7).to_bytes(8,'big')
def _dec(data,pl):
    c=kelcrypt.Ctx(KEY);out=bytearray()
    for i in range(0,pl,8): out+=c.dec_block(data[i:i+8])
    chk=c.chk;L,ck=struct.unpack('<II',c.dec_block(data[pl:pl+8]))
    if ck!=chk or L!=pl: raise ValueError('chk')
    return bytes(out)
def _enc(z):
    p=z+bytes(-len(z)%8);c=kelcrypt.Ctx(KEY);out=bytearray()
    for i in range(0,len(p),8): out+=c.enc_block(p[i:i+8])
    out+=c.enc_block(struct.pack('<II',len(p),c.chk));return bytes(out)
def unpack(d):
    n=struct.unpack_from('<I',d,0)[0];tab=[struct.unpack_from('<II',d,4+8*i) for i in range(n)]
    out=[]
    for o,s in tab:
        cs,us=struct.unpack_from('<II',d,o);pl=((cs+7)//8)*8
        try:
            z=_dec(d[o+8:o+8+pl+8],pl);t=zlib.decompress(z[:cs]);assert len(t)==us
            out.append(('z',t))
        except Exception:
            out.append(('raw',d[o:o+s]))
    return out
def pack(items,hdr_align=0x80,align=0x40):
    n=len(items);out=bytearray(b'\0'*hdr_align);struct.pack_into('<I',out,0,n)
    for i,(kind,t) in enumerate(items):
        while len(out)%align: out.append(0)
        o=len(out)
        if kind=='z':
            z=zlib.compress(t,9);blk=struct.pack('<II',len(z),len(t))+_enc(z)
        else: blk=t
        out+=blk;struct.pack_into('<II',out,4+8*i,o,len(blk))
    while len(out)%align: out.append(0)
    return bytes(out)
