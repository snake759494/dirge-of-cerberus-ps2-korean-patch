"""FILELIST.BIN 재생성"""
import struct,zlib
def build(raw_orig,ents):
    """ents: kel.Kel().ents (sec,size,csize,name) 수정본. 원본 id/flags/압축레벨 유지"""
    t1end,t2end,cnt=struct.unpack_from('<III',raw_orig)
    ids=[struct.unpack_from('<I',raw_orig,12+i*8)[0] for i in range(cnt)]
    recs=[('%x:%x:%x:%s'%(e['sec'],e['size'],e['csize'],e['name'])).encode('latin1')+b'\0' for e in ents]
    recs.append(b'end\0')
    chunks=[];cur=b'';tab=[]
    for r in recs[:-1]:
        if cur and len(cur)+len(r)>8192: chunks.append(cur);cur=b''
        tab.append((len(cur)<<16)|len(chunks));cur+=r
    cur+=recs[-1];chunks.append(cur)
    comp=[zlib.compress(c,9) for c in chunks]
    out=bytearray(struct.pack('<III',0,0,cnt))
    for i in range(cnt): out+=struct.pack('<II',ids[i],tab[i])
    t1=len(out);off=0
    for c,z in zip(chunks,comp): out+=struct.pack('<III',len(c),len(z),off);off+=len(z)
    t2=len(out)
    for z in comp: out+=z
    struct.pack_into('<II',out,0,t1,t2)
    return bytes(out)
