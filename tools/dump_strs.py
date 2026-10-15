"""모든 문자열 컨테이너를 덤프: work/strs_all.tsv (kel인덱스, 파일ID, 항목번호, ID이름, 본문)"""
import zlib,struct,os,sys
from kel import Kel
from strfile import unpack
HDR=bytes.fromhex('4590aff9b747f694')
def parse(z,n):
    ents=[struct.unpack_from('<III',z,i*12) for i in range(n)]
    def cs(o):
        o-=32;e=z.index(b'\0',o);return z[o:e]
    return [(h,cs(a),cs(b)) for h,a,b in ents]
def load(k,i):
    h,b=unpack(k.read(i));flags=struct.unpack_from('<I',h,8)[0];n=flags&0xffffff
    z=zlib.decompress(b) if flags>>24 else b
    return h,flags,parse(z,n)
if __name__=='__main__':
    k=Kel();ids=[int(x) for x in open(sys.argv[1]).read().split()]
    out=open(sys.argv[2],'w',encoding='utf-8')
    for i in ids:
        try: h,fl,ents=load(k,i)
        except Exception as e: print('ERR',i,e);continue
        for j,(hs,idn,t) in enumerate(ents):
            out.write(f"{i}\t{k.ids[i][0]:08x}\t{j}\t{idn.decode('cp932','replace')}\t{t.decode('cp932','replace')!r}\n")
