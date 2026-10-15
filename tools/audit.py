"""패치 ISO 전수검사: 모든 KEL 항목을 (복호/해제 후) 훑어 연속 가나(일본어) 문자열 탐지"""
import re,struct,zlib,sys,json
from kel import Kel
import kelcrypt,strfile,kelstr,sjis
KANA=re.compile(rb'(?:(?:\x81[\x40-\xac]|\x82[\x9f-\xf1]|\x83[\x40-\x96])*(?:\x82[\x9f-\xf1]|\x83[\x40-\x96])){3,}')
HDR=bytes.fromhex('4590aff9b747f694')
def views(k,i,e):
    d=k.read(i);yield 'raw',d
    if d[:4]==b'TTTT':
        try: yield 'tttt',kelcrypt.decrypt(d)[1]
        except Exception: pass
    if d[:8]==HDR:
        try:
            h,b=strfile.unpack(d);fl=struct.unpack_from('<I',h,8)[0]
            yield 'str',(zlib.decompress(b) if fl>>24 else b)
        except Exception: pass
    if e['name'].endswith('kelstr.bin'): yield 'kelstr',kelstr.xor(d)
    # 내부 zlib 스트림
    for m in re.finditer(rb'\x78[\x9c\xda]',d[:2_000_000]):
        try:
            z=zlib.decompressobj();o=z.decompress(d[m.start():m.start()+1_000_000],4_000_000)
            if len(o)>64: yield 'z@%x'%m.start(),o
        except Exception: pass
def main(iso):
    k=Kel(iso);out=[]
    for i,e in enumerate(k.ents):
        if e['name'].endswith(('.at3','.wd','.at2','.pss')) or e['size']>30_000_000: continue
        try:
            for kind,d in views(k,i,e):
                for m in KANA.finditer(d):
                    out.append(dict(i=i,id='%08x'%k.ids[i][0],name=e['name'].strip(),kind=kind,off=m.start(),text=sjis.dec(d[max(0,m.start()-40):m.end()+40])))
        except Exception as ex: pass
    return out
if __name__=='__main__':
    r=main(sys.argv[1]);json.dump(r,open(sys.argv[2],'w',encoding='utf-8'),ensure_ascii=False,indent=0)
    import collections
    c=collections.Counter((x['name'] or x['id'][:5],x['kind'][:3]) for x in r)
    print(len(r));[print(v,kk) for kk,v in c.most_common(60)]
