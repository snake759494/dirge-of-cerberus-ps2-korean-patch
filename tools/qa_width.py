"""줄 폭 검수: 원문 줄 대비 번역 줄 표시폭 초과 보고 (전각/한글=2, 반각=1, 제어토큰=0)"""
import json,glob,re,sys,unicodedata
W='work'
units=json.load(open(W+'/units.json',encoding='utf-8'))
ko={}
for fn in glob.glob(W+'/tr/b*_ko.json'): ko.update({int(k):v for k,v in json.load(open(fn,encoding='utf-8')).items()})
TOK=re.compile(r'^\d+:\d+:|\$h[0-9a-z]{2}|\$[oxwtm]\d+\$?|\$c\d+\$?|\$i[a-z0-9]{2,3}\$?|\{[0-9A-F]+\}')
def width(s):
    s=TOK.sub('',s);w=0
    for c in s:
        if ord(c)<0x80 or 0xff61<=ord(c)<=0xff9f: w+=1
        else: w+=2
    return w
over=[]
for u in units:
    t=ko.get(u['n'])
    if t is None: continue
    jl=u['jp'].split('$r');kl=t.split('$r')
    mj=max(width(x) for x in jl)
    for x in kl:
        if width(x)>mj+4: over.append((u['n'],width(x),mj,x));break
print('폭 초과 항목',len(over))
for o in over[:int(sys.argv[1]) if len(sys.argv)>1 else 10]: print(o)
json.dump([o[0] for o in over],open(W+'/qa_width.json','w'))
