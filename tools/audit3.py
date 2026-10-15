"""최종 ISO 재검사: 가나 + '한글 배치표에 없는 한자 코드'까지 탐지 (문자열 컨테이너/kelstr/존/SLPM)"""
import re,struct,zlib,sys,json,collections
from kel import Kel
from dump_strs import load
import kelstr,sjis
from isols import listiso
cm={bytes.fromhex(v) for v in json.load(open('../work/charmap.json',encoding='utf-8')).values()}
def jp_parts(b):
    """문자열 바이트에서 일본어(가나 또는 배치표 밖 한자) 문자 수"""
    n=0;i=0
    while i<len(b):
        c=b[i]
        if (0x81<=c<=0x9f or 0xe0<=c<=0xfc) and i+1<len(b):
            p=b[i:i+2]
            if p not in cm:
                if c==0x82 and p[1]>=0x9f or c==0x83 and p[1]<=0x96: n+=1          # 가나
                elif 0x88<=c<=0x9f or 0xe0<=c<=0xea:                              # 한자
                    if not (c==0x88 and p[1]<0x9f): n+=1
            i+=2
        else: i+=1
    return n
def run(iso):
    k=Kel(iso);out=[]
    ids=[int(x) for x in open(r'C:/Users/Jay/AppData/Local/Temp/claude/D--ps2-----------FF7---------/a07ee5d0-7635-48d3-b7da-1bffe52d30af/scratchpad/strfiles.txt').read().split()]
    for i in ids:
        try: ents=load(k,i)[2]
        except Exception as e: out.append(('ERR',i,str(e)));continue
        for j,(h,idn,t) in enumerate(ents):
            if jp_parts(t): out.append(('str',i,'%08x'%k.ids[i][0],j,sjis.dec(idn),t))
    N={e['name']:i for i,e in enumerate(k.ents)}
    for nm in ('data/etc/locale/jp/kelstr.bin',):
        h,secs=kelstr.parse(k.read(N[nm]))
        for si,s in enumerate(secs):
            if not s: continue
            lst=[x for g in s[1] for x in g[1]] if s[0]=='G' else s[1]
            for j,x in enumerate(lst):
                if x and not x.startswith(b'$&') and jp_parts(x): out.append(('kelstr',si,j,x))
    return out,k
if __name__=='__main__':
    out,k=run(sys.argv[1])
    cmr={bytes.fromhex(v):kk for kk,v in json.load(open('../work/charmap.json',encoding='utf-8')).items()}
    def dec(b):
        o='';i=0
        while i<len(b):
            if b[i]>=0x80 and i+1<len(b):
                p=b[i:i+2];o+=cmr.get(p) or p.decode('cp932','replace');i+=2
            else: o+=chr(b[i]);i+=1
        return o
    c=collections.Counter()
    rows=[]
    for r in out:
        if r[0]=='str': rows.append(dict(kind='str',f=r[1],fid=r[2],e=r[3],id=r[4],text=dec(r[5])))
        elif r[0]=='kelstr': rows.append(dict(kind='kelstr',sec=r[1],idx=r[2],text=dec(r[3])))
        else: rows.append(dict(kind='err',f=r[1],msg=r[2]))
    json.dump(rows,open('../work/audit_final.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
    print(len(rows))
    for x in rows[:80]: print(x.get('kind'),x.get('fid',x.get('sec')),x.get('id',x.get('idx')),repr(x.get('text',x.get('msg',''))[:90]))
