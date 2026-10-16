"""더지 오브 케르베로스 한글패치 빌드

사용: python tools/build.py [출력ISO]

- work/units.json + work/tr/bNN_ko.json 번역 적용

- 문자열 컨테이너(jp) / kelstr(jp) 재작성, fontdata1(jp, etc) 한글 글리프 주입

- KEL.DAT 항목 제자리 기록(넘치면 ISO 끝에 추가), FILELIST.BIN 재생성

"""

import sys,os,json,glob,re,struct,zlib,shutil,hashlib

sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))

from kel import Kel,ISO,ROOT

import kelstr,kelfont,hanglyph,filelist,strfile,sjis,movfont,imgpatch

from dump_strs import load as load_strfile

from isols import listiso



WORK=os.path.join(ROOT,'work')
class HDict(dict):
    """원문 키 또는 원문 md5 키(배포용) 모두로 찾는 사전"""
    def _h(self,k): return hashlib.md5(k.encode('utf-8')).hexdigest()
    def get(self,k,d=None):
        if dict.__contains__(self,k): return dict.__getitem__(self,k)
        return dict.get(self,self._h(k),d)
    def __contains__(self,k): return dict.__contains__(self,k) or dict.__contains__(self,self._h(k))
    def __getitem__(self,k):
        v=self.get(k)
        if v is None: raise KeyError(k)
        return v

FONT_FILE='NanumSquareNeo-bRg.ttf'

HANGUL_START=0x889F      # 한자 제1수준 시작부터 한글 배치



# 번역문에 쓰일 수 있는 cp932 외 문자 대체

REPL={'·':'・','‧':'・','—':'―','–':'－','~':'～','“':'"','”':'"','‘':"'",'’':"'",'…':'…','‥':'‥',' ':' ','─':'―','♪':'♪'}



def load_translations():

    units=json.load(open(os.path.join(WORK,'units.json'),encoding='utf-8'))

    ko={}

    for fn in glob.glob(os.path.join(WORK,'tr','b*_ko.json')):

        ko.update({int(k):v for k,v in json.load(open(fn,encoding='utf-8')).items()})

    tr=HDict();missing=[]

    ex=os.path.join(WORK,'extra_ko.json')

    if os.path.exists(ex): tr.update(json.load(open(ex,encoding='utf-8')))

    for u in units:

        if u['n'] in ko: tr[u['jp']]=ko[u['n']]

        else: missing.append(u['n'])

    return units,tr,missing



def norm(s):

    return ''.join(REPL.get(c,c) for c in s)



def build_charmap(texts):

    texts=list(texts)+list(json.load(open(os.path.join(WORK,'deco_ko.json'),encoding='utf-8')).values())

    zf=os.path.join(WORK,'zone_ko.json')

    if os.path.exists(zf): texts+=list(json.load(open(zf,encoding='utf-8')).values())
    xf=os.path.join(WORK,'exe_ko.json')
    if os.path.exists(xf): texts+=[v['ko'] for v in json.load(open(xf,encoding='utf-8')).values()]

    chars=sorted({c for t in texts for c in t if '가'<=c<='힣' or 'ㄱ'<=c<='ㆎ'})

    start=kelfont.code2idx(HANGUL_START)

    cmap={c:kelfont.idx2code(start+i).to_bytes(2,'big') for i,c in enumerate(chars)}

    return cmap



def encode(s,cmap):

    s=norm(s);out=bytearray();i=0

    while i<len(s):

        m=sjis._tok.match(s,i)

        if m: out+=bytes.fromhex(m.group(1));i=m.end();continue

        c=s[i]

        if c in cmap: out+=cmap[c]

        else:

            try: out+=c.encode('cp932')

            except UnicodeEncodeError: raise ValueError('인코딩 불가 문자 %r in %r'%(c,s))

        i+=1

    return bytes(out)



def build_strfile(k,i,tr,cmap,stats):

    h,flags,ents=load_strfile(k,i)

    n=len(ents);table=bytearray();pool=bytearray()

    texts=[]

    for hs,idn,t in ents:

        jp=sjis.dec(t);ko=tr.get(jp)

        if ko is None: stats['untr']+=1;b=t

        else: b=encode(ko,cmap)

        texts.append((hs,idn,b))

    base=32+12*n

    for hs,idn,b in texts:

        o_id=base+len(pool);pool+=idn+b'\0'

        o_tx=base+len(pool);pool+=b+b'\0'

        table+=struct.pack('<III',hs,o_id,o_tx)

    plain=bytes(table+pool)

    while len(plain)%4: plain+=b'\0'

    comp=flags>>24

    body=zlib.compress(plain,9) if comp else plain

    benc=strfile._enc(body,1)

    # 헤더 u32[3] = 문자열 복사 버퍼 크기(최장 문자열+1, 8정렬). 파일 끝에 같은 크기의 영역이 붙음
    pad=max(8,(max(len(b) for _,_,b in texts)+1+7)//8*8);total=32+len(benc)+pad

    hdr=strfile._enc(struct.pack('<6I',1,0,(flags&0xff000000)|n,pad,len(plain),total),strfile.K1)

    assert len(hdr)==32

    out=hdr+benc+bytes(pad)

    # 검증

    h2,b2=strfile.unpack(out)

    assert (zlib.decompress(b2) if comp else b2)[:len(plain)]==plain

    return out



def flat_kelstr(secs):

    for si,s in enumerate(secs):

        if not s: continue

        if s[0]=='G':

            for g,(tag,st) in enumerate(s[1]):

                for j,x in enumerate(st): yield si,(g,j),x

        else:

            for j,x in enumerate(s[1]): yield si,(None,j),x



def build_kelstr(raw,tr,cmap,stats):

    head,secs=kelstr.parse(raw)

    secs=[None if s is None else (s[0],[(t,list(st)) for t,st in s[1]] if s[0]=='G' else list(s[1])) for s in secs]

    deco=json.load(open(os.path.join(WORK,'deco_ko.json'),encoding='utf-8'))

    for si,(g,j),x in list(flat_kelstr(secs)):

        key=f'K{si}.{g}.{j}' if g is not None else f'K{si}.{j}'

        if x and x.startswith(b'$&') and key in deco:

            b=encode(deco[key],cmap)

            if secs[si][0]=='G': secs[si][1][g][1][j]=b

            else: secs[si][1][j]=b

            continue

        if not x or x.startswith(b'$&'): continue

        jp=sjis.dec(x);ko=tr.get(jp)

        if ko is None: continue

        b=encode(ko,cmap)

        if secs[si][0]=='G': secs[si][1][g][1][j]=b

        else: secs[si][1][j]=b

    out=kelstr.build(head,secs)

    assert len(out)<=0x1c800, 'kelstr 크기 초과 %d'%len(out)

    return out



def build_font(raw,cmap):

    F=kelfont.Font(raw);r=hanglyph.make(FONT_FILE,15)

    for c,code in cmap.items():

        F.put(kelfont.code2idx(int.from_bytes(code,'big')),r(c))

    return F.tobytes()



def kel_pack(data):

    z=zlib.compress(data,9)

    if len(z)>=len(data): return data,len(data)   # 무압축 저장(크기==압축크기)

    return z,len(z)



def main():

    out_iso=sys.argv[1] if len(sys.argv)>1 else os.path.join(ROOT,'Final Fantasy VII International - Dirge of Cerberus (Korean).iso')

    k=Kel();N={e['name']:i for i,e in enumerate(k.ents)}

    units,tr,missing=load_translations()

    print('번역',len(tr),'누락',len(missing))

    cmap=build_charmap(tr.values())

    print('한글 글자 수',len(cmap),'마지막 코드',cmap[max(cmap)].hex() if cmap else None)

    json.dump({c:b.hex() for c,b in cmap.items()},open(os.path.join(WORK,'charmap.json'),'w',encoding='utf-8'),ensure_ascii=False)

    stats={'untr':0}

    newfiles={}

    jpfiles={x['f'] for x in json.load(open(os.path.join(WORK,'strfile_jp.json'),encoding='utf-8'))}

    ef=os.path.join(WORK,'extra_files.json')

    if os.path.exists(ef): jpfiles|=set(json.load(open(ef)))

    jpfiles=sorted(jpfiles)

    for i in jpfiles: newfiles[i]=build_strfile(k,i,tr,cmap,stats)

    newfiles[N['data/etc/locale/jp/kelstr.bin']]=build_kelstr(k.read(N['data/etc/locale/jp/kelstr.bin']),tr,cmap,stats)

    for fn in ('data/etc/locale/jp/fontdata1.bin','data/etc/fontdata1.bin','data/etc/locale/uk/fontdata1.bin'):

        newfiles[N[fn]]=build_font(k.read(N[fn]),cmap)

    # 존 설정 파일(오프셋4, 28바이트 이름 필드)

    zf=os.path.join(WORK,'zone_ko.json')

    if os.path.exists(zf):

        Z=HDict(json.load(open(zf,encoding='utf-8')));nz=0

        for i,e in enumerate(k.ents):

            if (k.ids[i][0]>>24)!=6 or e['size']>4096 or e['csize']>=e['size']+64: continue

            try: d=k.read(i)

            except Exception: continue

            if len(d)<32 or d[:4]!=bytes([13,0,0,0]): continue

            try: nm=d[4:32].decode('cp932').rstrip(' ')

            except Exception: continue

            if nm in Z:

                b=encode(Z[nm],cmap);assert len(b)<=28,(nm,Z[nm])

                newfiles[i]=d[:4]+b+b' '*(28-len(b))+d[32:];nz+=1

        print('존 이름 패치',nz)

    # 이펙트 파일 내 일본어 조작표 이미지 교체
    jobs=imgpatch.load_jobs();cache={};ni=0;nf=0
    for i,e in enumerate(k.ents):
        if not e['name'].endswith(('.fed','.fez')): continue
        src=newfiles.get(i) or k.read(i)
        out,n=imgpatch.patch_file(src,jobs,cache)
        if n: newfiles[i]=out;ni+=n;nf+=1
    print('이미지 패치',ni,'개 /',nf,'파일 / 고유',len(cache))
    R4=hanglyph.make4(FONT_FILE,17)

    g4={int.from_bytes(b,'big'):R4(c) for c,b in cmap.items()}

    for fn in ('data/etc/locale/jp/menu_mv.bin','data/etc/locale/uk/menu_mv.bin','data/etc/menu_mv.bin'):

        newfiles[N[fn]]=movfont.patch(k.read(N[fn]),g4)

    print('미번역 문자열(컨테이너 내)',stats['untr'],'수정 파일',len(newfiles))

    # 배치

    order=sorted(range(len(k.ents)),key=lambda i:k.ents[i]['sec'])

    nxt={}

    for a,b in zip(order,order[1:]): nxt[a]=k.ents[b]['sec']

    isof={n:(e,s) for n,e,s in listiso(ISO)}

    kel_lba,kel_size=isof['/D730AA92/KEL.DAT']

    nxt[order[-1]]=(kel_size+2047)//2048

    iso_end=os.path.getsize(ISO)//2048

    append_sec=iso_end-kel_lba   # KEL 기준 섹터

    ents=[dict(e) for e in k.ents];writes=[];appended=0

    for i,data in sorted(newfiles.items()):

        blob,cs=kel_pack(data);e=ents[i]

        need=(len(blob)+2047)//2048;have=nxt[i]-e['sec']

        e['size']=len(data);e['csize']=cs

        if need<=have: sec=e['sec']

        else:

            sec=append_sec;append_sec+=need;appended+=need;e['sec']=sec

        writes.append((kel_lba+sec,blob+bytes(need*2048-len(blob))))

    print('ISO 끝에 추가된 섹터',appended)

    fl=filelist.build(k.raw,ents)

    fl_lba,fl_size=isof['/FILELIST.BIN'];fl_have=(isof['/D730AA92/HASH.INF'][0]-fl_lba)*2048

    assert len(fl)<=fl_have,'FILELIST 공간 부족'

    writes.append((fl_lba,fl+bytes(-len(fl)%2048)))

    # ISO 출력

    if os.path.exists(out_iso): os.remove(out_iso)

    shutil.copyfile(ISO,out_iso)

    with open(out_iso,'r+b') as f:

        for lba,blob in writes: f.seek(lba*2048);f.write(blob)

        new_end=max(iso_end,kel_lba+append_sec)

        f.truncate(new_end*2048)

        # PVD 볼륨 크기

        f.seek(16*2048+80);f.write(struct.pack('<I',new_end)+struct.pack('>I',new_end))

        # FILELIST.BIN 디렉터리 레코드 크기 갱신

        patch_dirrec(f,'FILELIST.BIN;1',len(fl))
        # 실행 파일(SLPM_666.29) 내 문구 제자리 치환
        cf=os.path.join(WORK,'exe_code.json')
        if os.path.exists(cf):
            elba=isof['/SLPM_666.29'][0]
            for va,v in json.load(open(cf,encoding='utf-8')).items():
                if va.startswith('_'): continue
                off=elba*2048+int(va,16)-0x100000+0x100   # 세그먼트0: 파일 0x100 = VA 0x100000
                f.seek(off);cur=f.read(4)
                assert cur==struct.pack('<I',int(v['old'],16)),('코드 불일치',va,cur.hex())
                f.seek(off);f.write(struct.pack('<I',int(v['new'],16)))
        xf=os.path.join(WORK,'exe_ko.json')
        if os.path.exists(xf):
            elba=isof['/SLPM_666.29'][0]
            for off,v in json.load(open(xf,encoding='utf-8')).items():
                b=encode(v['ko'],cmap);assert len(b)<v['len'],(len(b),v['len'])
                f.seek(elba*2048+int(off,16));f.write(b+bytes(v['len']-len(b)))

        if appended: patch_dirrec(f,'KEL.DAT;1',(append_sec)*2048,sub='D730AA92')

    print('완료',out_iso,new_end)



def patch_dirrec(f,name,size,sub=None):

    f.seek(16*2048+156);r=f.read(34);lba=struct.unpack_from('<I',r,2)[0];ln=struct.unpack_from('<I',r,10)[0]

    def find(lba,ln,target):

        f.seek(lba*2048);d=f.read(ln);i=0

        while i<len(d):

            l=d[i]

            if l==0: i=(i//2048+1)*2048;continue

            nl=d[i+32];nm=d[i+33:i+33+nl].decode('latin1')

            if nm==target: return lba*2048+i,d[i:i+l]

            i+=l

        raise KeyError(target)

    if sub:

        pos,rec=find(lba,ln,sub);lba=struct.unpack_from('<I',rec,2)[0];ln=struct.unpack_from('<I',rec,10)[0]

    pos,rec=find(lba,ln,name)

    f.seek(pos+10);f.write(struct.pack('<I',size)+struct.pack('>I',size))



if __name__=='__main__': main()

