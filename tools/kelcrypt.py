"""DoC 파일 암호(헤더 8바이트 키, 8바이트 블록) 복호/암호화 - kel.pex 0x41bd38~0x41c3d8 재구현"""
import struct
from kelcrypt_tables import E,D
M64=(1<<64)-1
def rotl32(x,n): x&=0xffffffff;return ((x<<n)|(x>>(32-n)))&0xffffffff
class Ctx:
    def __init__(s,key8):
        K=int.from_bytes(key8,'big')            # 0x3a84c0: 헤더를 빅엔디언 64비트로
        hi=K>>32;lo=K&0xffffffff
        k0=(rotl32(lo,8)<<32)|rotl32(hi,16)
        b=bytearray(k0.to_bytes(8,'little'))
        b[0]=(b[0]+69)&0xff
        for i in range(1,8):
            b[i]=(((b[i]+212)+b[i-1])^(b[i-1]<<2)^0x45)&0xff
        sk=[int.from_bytes(b,'little')]
        for i in range(1,32): sk.append((sk[-1]*5)&M64)
        s.sk=sk;s.pos=0;s.chk=0
    def _t(s): t=s.pos;return ((t|(t<<10)|(t<<20)|(t<<30))+0xa1652347)&M64
    def dec_block(s,c):
        K=s.sk[(s.pos&0xff)>>3];kb=K.to_bytes(8,'little')
        t3=((s.pos>>3)^0x45)&0xff;o=bytearray(8)
        for j in range(8):
            a=c[j];x=t3^a;t3=a
            for k in range(8): x=(D[x]-kb[k])&0xff
            o[j]=x
        v=int.from_bytes(o,'little')
        v=((v-K)&M64)^s._t()^K
        v=((v>>32)|(v<<32))&M64
        o=v.to_bytes(8,'little')
        s.pos+=8;s.chk=(s.chk+o[0]+o[4])&0xffffffff
        return o
    def enc_block(s,p):
        s.chk=(s.chk+p[0]+p[4])&0xffffffff
        K=s.sk[(s.pos&0xff)>>3];kb=K.to_bytes(8,'little')
        v=int.from_bytes(p,'little');v=((v>>32)|(v<<32))&M64
        v=(((v^K)^s._t())+K)&M64
        o=bytearray(v.to_bytes(8,'little'))
        t4=((s.pos>>3)^0x45)&0xff
        for j in range(8):
            x=o[j]
            for k in range(7,-1,-1): x=E[(x+kb[k])&0xff]
            x^=t4;o[j]=x;t4=x
        s.pos+=8
        return bytes(o)
def decrypt(data):
    """파일 전체(헤더 포함) -> (헤더, 평문)."""
    hdr=data[:8];body=data[8:];c=Ctx(hdr)
    out=bytearray()
    for i in range(0,len(body)-8,8): out+=c.dec_block(body[i:i+8])
    chk=c.chk;last=c.dec_block(body[len(body)-8:])
    n,ck=struct.unpack('<II',last)
    if ck!=chk: raise ValueError('checksum mismatch %x %x'%(ck,chk))
    return hdr,bytes(out[:n])
def encrypt(hdr,plain):
    c=Ctx(hdr);p=plain+bytes(-len(plain)%8);out=bytearray(hdr)
    for i in range(0,len(p),8): out+=c.enc_block(p[i:i+8])
    out+=c.enc_block(struct.pack('<II',len(plain),c.chk))
    return bytes(out)
