import sys,struct
def walk(f,lba,size,path=''):
    f.seek(lba*2048);d=f.read(size);i=0;out=[]
    while i<len(d):
        l=d[i]
        if l==0: i=(i//2048+1)*2048; continue
        ext,sz=struct.unpack_from('<I',d,i+2)[0],struct.unpack_from('<I',d,i+10)[0]
        fl=d[i+25];nl=d[i+32];name=d[i+33:i+33+nl]
        if name not in(b'\0',b'\1'):
            n=name.decode('latin1').split(';')[0]
            if fl&2: out+=walk(f,ext,sz,path+'/'+n)
            else: out.append((path+'/'+n,ext,sz))
        i+=l
    return out
def listiso(p):
    f=open(p,'rb');f.seek(16*2048+156);r=f.read(34)
    return walk(f,struct.unpack_from('<I',r,2)[0],struct.unpack_from('<I',r,10)[0])
if __name__=='__main__':
    for n,e,s in listiso(sys.argv[1]): print(e,s,n)
