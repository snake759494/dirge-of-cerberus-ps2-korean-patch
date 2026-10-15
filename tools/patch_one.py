"""원본 ISO 복사본에 특정 KEL 파일 하나만 교체(실험용)"""
import sys,os,shutil,zlib
from kel import Kel,ISO
import filelist
from isols import listiso
def make(out,repl,base=None):
    base=base or ISO
    k=Kel(base);N={e['name']:i for i,e in enumerate(k.ents)}
    isof={n:(e,s) for n,e,s in listiso(base)};kel_lba=isof['/D730AA92/KEL.DAT'][0]
    if os.path.exists(out): os.remove(out)
    shutil.copyfile(base,out);ents=[dict(e) for e in k.ents]
    with open(out,'r+b') as f:
        for name,data in repl.items():
            i=N[name] if isinstance(name,str) else name;z=zlib.compress(data,9);e=ents[i]
            order=sorted(range(len(ents)),key=lambda j:ents[j]['sec']);nxt=ents[order[order.index(i)+1]]['sec']
            assert (len(z)+2047)//2048<=nxt-e['sec']
            e['size']=len(data);e['csize']=len(z)
            f.seek((kel_lba+e['sec'])*2048);f.write(z+bytes(-len(z)%2048))
        fl=filelist.build(k.raw,ents);f.seek(isof['/FILELIST.BIN'][0]*2048);f.write(fl+bytes(-len(fl)%2048))
