"""원본 ISO에서 원문 데이터(work/strfile_jp.json, kelstr_jp.json, units.json)를 로컬 생성하고
translation/ko_units.tsv(번호·ID·한국어)를 work/tr/b_all_ko.json으로 변환한다.
사용: python tools/make_src.py"""
import sys,os,json,re,csv
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from kel import Kel,ROOT
from dump_strs import load
import kelstr,sjis
HDR=bytes.fromhex('4590aff9b747f694')
JP=re.compile('[\u3040-\u30ff\u4e00-\u9fff]')
def main():
    W=os.path.join(ROOT,'work');os.makedirs(os.path.join(W,'tr'),exist_ok=True)
    k=Kel();N={e['name']:i for i,e in enumerate(k.ents)}
    ids=[]
    for i,e in enumerate(k.ents):
        if e['name'].endswith(('.at3','.wd','.pss','.at2')): continue
        try: d=k.read(i)
        except Exception: continue
        if d[:8]==HDR: ids.append(i)
    byid={k.ids[i][0]:i for i in ids}
    data={i:load(k,i)[2] for i in ids}
    jpf=[i for i in ids if sum(1 for e in data[i] if JP.search(sjis.dec(e[2])))>len(data[i])*0.3]
    sf=[]
    for i in jpf:
        fid=k.ids[i][0];uk=byid.get(fid+2)
        ukmap={e[1]:sjis.dec(e[2]) for e in data[uk]} if uk is not None else {}
        for j,(hs,idn,t) in enumerate(data[i]):
            sf.append(dict(f=i,fid='%08x'%fid,e=j,id=sjis.dec(idn),jp=sjis.dec(t),en=ukmap.get(idn,'')))
    json.dump(sf,open(os.path.join(W,'strfile_jp.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=0)
    hj,sj=kelstr.parse(k.read(N['data/etc/locale/jp/kelstr.bin']));hu,su=kelstr.parse(k.read(N['data/etc/locale/uk/kelstr.bin']))
    def flat(secs):
        out=[]
        for si,s in enumerate(secs):
            if not s: continue
            if s[0]=='G':
                for g,(tag,st) in enumerate(s[1]):
                    for j,x in enumerate(st): out.append((f'K{si}.{g}.{j}',x))
            else:
                for j,x in enumerate(s[1]): out.append((f'K{si}.{j}',x))
        return out
    fu=dict(flat(su));ks=[]
    for key,x in flat(sj):
        if not x or x.startswith(b'$&'): continue
        t=sjis.dec(x)
        if not JP.search(t): continue
        ks.append(dict(src='kelstr',key=key,jp=t,en=sjis.dec(fu[key]) if fu.get(key) else ''))
    json.dump(ks,open(os.path.join(W,'kelstr_jp.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=0)
    units=[];seen=set()
    for x in sf:
        if x['jp'] in seen or not x['jp'].strip(): continue
        seen.add(x['jp']);units.append(dict(id=x['id'],jp=x['jp'],en=x['en']))
    for x in ks:
        if x['jp'] in seen: continue
        seen.add(x['jp']);units.append(dict(id=x['key'],jp=x['jp'],en=x['en']))
    for n,u in enumerate(units): u['n']=n
    json.dump(units,open(os.path.join(W,'units.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=0)
    json.dump([i for i in ids if i not in jpf and any(JP.search(sjis.dec(e[2])) for e in data[i])],
              open(os.path.join(W,'extra_files.json'),'w'))
    import shutil,glob
    T=os.path.join(ROOT,'translation')
    for nm in ('extra_ko.json','zone_ko.json','deco_ko.json','exe_ko.json','exe_code.json','glossary.md'):
        if os.path.exists(os.path.join(T,nm)): shutil.copy(os.path.join(T,nm),os.path.join(W,nm))
    os.makedirs(os.path.join(W,'img'),exist_ok=True)
    for f in glob.glob(os.path.join(T,'img','*.json')): shutil.copy(f,os.path.join(W,'img'))
    tsv=os.path.join(T,'ko_units.tsv')
    if os.path.exists(tsv):
        ko={}
        for r in csv.reader(open(tsv,encoding='utf-8'),delimiter='\t',quoting=csv.QUOTE_NONE):
            if not r or r[0]=='n': continue
            n=int(r[0]);assert units[n]['id']==r[1],('ID 불일치',n,r[1])
            ko[str(n)]=r[2].replace('\t','\t').replace('\n','\n')
        json.dump(ko,open(os.path.join(W,'tr','b_all_ko.json'),'w',encoding='utf-8'),ensure_ascii=False)
    print('문자열 파일',len(ids),'일본어',len(jpf),'번역 단위',len(units))
if __name__=='__main__': main()
