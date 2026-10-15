"""evstr/scenestr/movie string 등 'ID 문자열 컨테이너' 복호화/재암호화"""
import struct,zlib,kelcrypt
K1=((((0xaf13<<17)|0x8fc6)<<17|0xa98a)<<13|0x1688)&((1<<64)-1)
def _dec(data,key):
    c=kelcrypt.Ctx(key.to_bytes(8,'big'));out=bytearray()
    for i in range(0,len(data)-8,8): out+=c.dec_block(data[i:i+8])
    chk=c.chk;n,ck=struct.unpack('<II',c.dec_block(data[-8:]))
    if ck!=chk: raise ValueError('chk')
    return bytes(out[:n])
def _enc(plain,key):
    c=kelcrypt.Ctx(key.to_bytes(8,'big'));p=plain+bytes(-len(plain)%8);out=bytearray()
    for i in range(0,len(p),8): out+=c.enc_block(p[i:i+8])
    out+=c.enc_block(struct.pack('<II',len(plain),c.chk));return bytes(out)
def unpack(d):
    h=_dec(d[:32],K1);key2=struct.unpack_from('<Q',h,0)[0];pad=struct.unpack_from('<I',h,12)[0]
    b=_dec(d[32:len(d)-pad],key2)
    return h,b
