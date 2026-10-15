"""KEL.DAT / FILELIST.BIN 파서"""
import struct,zlib,os,sys
sys.path.insert(0,os.path.dirname(__file__))
from isols import listiso
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ISO=os.path.join(ROOT,'Final Fantasy VII International - Dirge of Cerberus (Undub v1.0).iso')
def filelist_raw(f):
    files={n:(e,s) for n,e,s in listiso(ISO)}
    e,s=files['/FILELIST.BIN'];f.seek(e*2048);return f.read(s),files
def parse_filelist(d):
    t1end,t2end,cnt=struct.unpack_from('<III',d)
    ids=[struct.unpack_from('<II',d,12+i*8) for i in range(cnt)]
    nch=(t2end-t1end)//12
    ch=[struct.unpack_from('<III',d,t1end+i*12) for i in range(nch)]
    txt=b''.join(zlib.decompress(d[t2end+o:t2end+o+s]) for a,s,o in ch)
    ents=[]
    for x in txt.split(b'\0'):
        if not x or x==b'end': continue
        p=x.decode('latin1').split(':',3)
        ents.append(dict(sec=int(p[0],16),size=int(p[1],16),csize=int(p[2],16),name=p[3]))
    return ids,ch,ents
class Kel:
    def __init__(s,iso=ISO):
        s.f=open(iso,'rb');s.raw,s.isof=filelist_raw(s.f)
        s.ids,s.ch,s.ents=parse_filelist(s.raw)
        s.kelbase=s.isof['/D730AA92/KEL.DAT'][0]
    def read(s,i):
        e=s.ents[i];s.f.seek((s.kelbase+e['sec'])*2048);c=s.f.read(e['csize'])
        if e['csize']==e['size']:
            try:
                z=zlib.decompress(c)
                if len(z)==e['size']: return z
            except Exception: pass
            return c
        return zlib.decompress(c)
