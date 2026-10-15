"""번역 품질 자동 검사: 잘림 의심(길이비), 용어 불일치, 문장부호/기호 이상"""
import json,glob,re,collections
W='work'
units=json.load(open(W+'/units.json',encoding='utf-8'))
ko={}
for fn in glob.glob(W+'/tr/b*_ko.json'): ko.update({int(k):v for k,v in json.load(open(fn,encoding='utf-8')).items()})
TOK=re.compile(r'^\d+:\d+:|\$h[0-9a-z]{2}|\$[oxwtm]\d+\$?|\$c\d+\$?|\$i[a-z0-9]{2,3}\$?|\$r|\{[0-9A-F]+\}|%[0-9]*[ds]')
def body(s): return TOK.sub('',s)
issues=collections.defaultdict(list)
# 용어: 일본어 → 기대 한국어, 금지 변형
TERMS={'ヴィンセント':['빈센트'],'ユフィ':['유피'],'シェルク':['셸크'],'シャルア':['샬루아'],'リーブ':['리브'],'ケット・シー':['케트 시','케트시'],
'ルクレツィア':['루크레치아'],'ヴァイス':['바이스'],'ネロ':['네로'],'アスール':['아줄'],'ロッソ':['로소'],'ツヴィエート':['츠비에트'],
'ディープグラウンド':['딥그라운드'],'ミッドガル':['미드가르'],'カーム':['칼름'],'魔晄':['마황'],'マテリア':['마테리아'],'ライフストリーム':['라이프스트림'],
'オメガ':['오메가'],'カオス':['카오스'],'宝条':['호조'],'神羅':['신라'],'ソルジャー':['솔저'],'タークス':['터크스'],'シド':['시드'],'バレット':['바렛'],'クラウド':['클라우드'],
'エッジ':['엣지'],'ルーイ':['루이']}
for u in units:
    t=ko.get(u['n'])
    if t is None: continue
    jb=body(u['jp']);kb=body(t)
    jl=len(jb.strip());kl=len(kb.strip())
    if jl>=12 and kl<jl*0.45: issues['잘림의심'].append(u['n'])
    if jl>=4 and kl>jl*2.6: issues['과다길이'].append(u['n'])
    for jp,oks in TERMS.items():
        if jp in u['jp'] and not any(o in t for o in oks): issues['용어:'+jp].append(u['n'])
    if re.search(r'[。、「」]',t) and not re.search(r'[「」]',u['jp']): issues['일본식부호'].append(u['n'])
    if re.search(r'\?\?|!!!!|\.\.\.\.',t): issues['부호반복'].append(u['n'])
    if '  ' in kb.strip() and '　' not in u['jp'] and '  ' not in u['jp']: issues['이중공백'].append(u['n'])
tot=collections.Counter({k:len(v) for k,v in issues.items()})
for k,v in sorted(tot.items(),key=lambda x:-x[1]): print(v,k)
json.dump(issues,open(W+'/qa_quality.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
