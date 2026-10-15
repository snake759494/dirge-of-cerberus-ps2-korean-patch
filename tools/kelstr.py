"""kelstr.bin 파서/빌더 (XOR 복호 + 섹션 구조)"""
import struct
K=bytes.fromhex('6c70b4c3d30d4fb578596724bd817e43')
NSEC=63
def xor(d): return d[:0x20]+bytes(d[i]^K[i%16] for i in range(0x20,len(d)))
def cstr(d,o): e=d.index(b'\0',o);return d[o:e]
def parse(raw):
    d=xor(raw);base=0x24
    secp=[struct.unpack_from('<I',d,0x24+4*i)[0] for i in range(NSEC)]
    secs=[]
    for si,p in enumerate(secp):
        if not p: secs.append(None);continue
        s=base+p
        if si==0:
            n=struct.unpack_from('<I',d,s)[0];groups=[]
            for g in range(n):
                cnt,tag,off=struct.unpack_from('<H2sI',d,s+4+8*g)
                t=s+off;strs=[]
                for j in range(cnt):
                    o=struct.unpack_from('<H',d,t+2*j)[0]
                    strs.append(cstr(d,s+o) if o else None)
                groups.append((tag,strs))
            secs.append(('G',groups))
        else:
            n=struct.unpack_from('<H',d,s)[0];strs=[]
            for j in range(n):
                o=struct.unpack_from('<H',d,s+2+2*j)[0]
                strs.append(cstr(d,s+o) if o else None)
            secs.append(('S',strs))
    return d[:0x24],secs
def build(head,secs):
    body=bytearray(b'\0'*(4*NSEC))
    def align():
        while len(body)%4: body.append(0)
    for si,sec in enumerate(secs):
        if sec is None: continue
        align();s=len(body);struct.pack_into('<I',body,4*si,s)
        if sec[0]=='G':
            groups=sec[1];hdr=bytearray(struct.pack('<I',len(groups))+b'\0'*(8*len(groups)))
            tables=bytearray();pool=bytearray()
            # 레이아웃: hdr | 각 그룹 테이블 | 문자열
            tsz=sum(2*len(st) for _,st in groups)
            strbase=len(hdr)+tsz;toff=len(hdr)
            for g,(tag,st) in enumerate(groups):
                struct.pack_into('<H2sI',hdr,4+8*g,len(st),tag,toff)
                for x in st:
                    if x is None: tables+=b'\0\0'
                    else:
                        o=strbase+len(pool);assert o<0x10000;tables+=struct.pack('<H',o);pool+=x+b'\0'
                toff+=2*len(st)
            body+=hdr+tables+pool
        else:
            st=sec[1];tab=bytearray(struct.pack('<H',len(st)));pool=bytearray();strbase=2+2*len(st)
            for x in st:
                if x is None: tab+=b'\0\0'
                else:
                    o=strbase+len(pool);assert o<0x10000;tab+=struct.pack('<H',o);pool+=x+b'\0'
            body+=tab+pool
    align()
    while len(body)%16: body.append(0)
    h=bytearray(head);struct.pack_into('<I',h,0x1c,len(body)+4)
    d=bytes(h)+bytes(body)
    return xor(d)
