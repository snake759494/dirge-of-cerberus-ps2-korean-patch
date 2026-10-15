"""전수검사 2단계: 널 종료 문자열 단위로 깨끗한 SJIS 일본어만 수집"""
import re,struct,zlib,sys,json,collections
from kel import Kel
import audit,sjis
JP=re.compile('[\u3040-\u30ff]')
def strings_in(d):
    for m in audit.KANA.finditer(d):
        s=d.rfind(b'\0',0,m.start())+1;e=d.find(b'\0',m.end());e=len(d) if e<0 else e
        b=d[s:e]
        if len(b)>400: continue
        t=sjis.dec(b)
        esc=len(re.findall(r'\{[0-9A-F]+\}',t))
        if esc>2: continue
        if len(JP.findall(t))<3: continue
        bad=sum(1 for c in t if ord(c)<0x20)
        if bad: continue
        yield s,t
def main(iso):
    k=Kel(iso);res=collections.OrderedDict()
    for i,e in enumerate(k.ents):
        if e['name'].endswith(('.at3','.wd','.at2','.pss','.fed','.rfd')) or e['size']>30_000_000: continue
        try:
            for kind,d in audit.views(k,i,e):
                for off,t in strings_in(d):
                    res.setdefault((i,kind,off),dict(i=i,id='%08x'%k.ids[i][0],name=e['name'].strip(),kind=kind,off=off,text=t))
        except Exception: pass
    return list(res.values())
if __name__=='__main__':
    r=main(sys.argv[1]);json.dump(r,open(sys.argv[2],'w',encoding='utf-8'),ensure_ascii=False,indent=0)
    c=collections.Counter((x['name'] or x['id'][:6],x['kind'][:3]) for x in r)
    print(len(r));[print(v,kk) for kk,v in c.most_common(80)]
