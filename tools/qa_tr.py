"""번역 검수: 누락/토큰 불일치/가나·한자 잔존/인코딩 불가 문자"""
import json,glob,re,os,sys
W='work'
units=json.load(open(W+'/units.json',encoding='utf-8'))
ko={}
for fn in sorted(glob.glob(W+'/tr/b*_ko.json')): ko.update({int(k):v for k,v in json.load(open(fn,encoding='utf-8')).items()})
TOK=re.compile(r'\$r|\$h[0-9a-z]{2}|\$[oxcwtm]\d+\$?|\$i[a-z0-9]{2,3}\$?|\$[a-z]|\{[0-9A-F]+\}|%[0-9]*[ds]|^\d+:\d+:')
bad=[];kana=[];miss=[]
for u in units:
    if u['n'] not in ko: miss.append(u['n']);continue
    t=ko[u['n']]
    if TOK.findall(u['jp'])!=TOK.findall(t): bad.append(u['n'])
    if re.search('[\u3040-\u30ff\u4e00-\u9fff]',re.sub(r'[ー・]','',t)): kana.append(u['n'])
print('번역됨',len(ko),'누락',len(miss),'토큰불일치',len(bad),'가나한자',len(kana))
if '-v' in sys.argv:
    for n in bad[:15]: print('T',n,repr(units[n]['jp'][:80]),'=>',repr(ko[n][:80]))
    for n in kana[:15]: print('K',n,repr(ko[n][:80]))
json.dump(dict(miss=miss,bad=bad,kana=kana),open(W+'/qa.json','w'))
