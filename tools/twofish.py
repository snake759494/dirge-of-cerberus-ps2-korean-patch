"""Twofish (128-bit key) + CBC, 순수 파이썬 구현"""
Q0=[[0x8,0x1,0x7,0xD,0x6,0xF,0x3,0x2,0x0,0xB,0x5,0x9,0xE,0xC,0xA,0x4],[0xE,0xC,0xB,0x8,0x1,0x2,0x3,0x5,0xF,0x4,0xA,0x6,0x7,0x0,0x9,0xD],[0xB,0xA,0x5,0xE,0x6,0xD,0x9,0x0,0xC,0x8,0xF,0x3,0x2,0x4,0x7,0x1],[0xD,0x7,0xF,0x4,0x1,0x2,0x6,0xE,0x9,0xB,0x3,0x0,0x8,0x5,0xC,0xA]]
Q1=[[0x2,0x8,0xB,0xD,0xF,0x7,0x6,0xE,0x3,0x1,0x9,0x4,0x0,0xA,0xC,0x5],[0x1,0xE,0x2,0xB,0x4,0xC,0x3,0x7,0x6,0xD,0xA,0x5,0xF,0x9,0x0,0x8],[0x4,0xC,0x7,0x5,0x1,0x6,0x9,0xA,0x0,0xE,0xD,0x8,0x2,0xB,0x3,0xF],[0xB,0x9,0x5,0x1,0xC,0x3,0xD,0xE,0x6,0x4,0x7,0xF,0x2,0x0,0x8,0xA]]
def ror4(x,n): return ((x>>n)|(x<<(4-n)))&0xF
def mkq(t):
    q=[]
    for x in range(256):
        a0,b0=x>>4,x&15;a1=a0^b0;b1=a0^ror4(b0,1)^((8*a0)&15)
        a2,b2=t[0][a1],t[1][b1];a3=a2^b2;b3=a2^ror4(b2,1)^((8*a2)&15)
        a4,b4=t[2][a3],t[3][b3];q.append((b4<<4)|a4)
    return q
q0=mkq(Q0);q1=mkq(Q1)
def gfm(a,b,p):
    r=0
    while b:
        if b&1: r^=a
        a<<=1
        if a&0x100: a^=p
        b>>=1
    return r
MDS=[[0x01,0xEF,0x5B,0x5B],[0x5B,0xEF,0xEF,0x01],[0xEF,0x5B,0x01,0xEF],[0xEF,0x01,0xEF,0x5B]]
RS=[[0x01,0xA4,0x55,0x87,0x5A,0x58,0xDB,0x9E],[0xA4,0x56,0x82,0xF3,0x1E,0xC6,0x68,0xE5],[0x02,0xA1,0xFC,0xC1,0x47,0xAE,0x3D,0x19],[0xA4,0x55,0x87,0x5A,0x58,0xDB,0x9E,0x03]]
def rol(x,n): return ((x<<n)|(x>>(32-n)))&0xffffffff
def ror(x,n): return ((x>>n)|(x<<(32-n)))&0xffffffff
def h(X,L):
    y=[(X>>(8*i))&255 for i in range(4)]
    l=[[(w>>(8*i))&255 for i in range(4)] for w in L]
    if len(L)==2:
        y=[q1[q0[q0[y[0]]^l[1][0]]^l[0][0]],q0[q0[q1[y[1]]^l[1][1]]^l[0][1]],q1[q1[q0[y[2]]^l[1][2]]^l[0][2]],q0[q1[q1[y[3]]^l[1][3]]^l[0][3]]]
    z=0
    for i in range(4):
        v=0
        for j in range(4): v^=gfm(MDS[i][j],y[j],0x169)
        z|=v<<(8*i)
    return z
class Twofish:
    def __init__(s,key):
        assert len(key)==16
        M=[int.from_bytes(key[4*i:4*i+4],'little') for i in range(4)]
        Me=[M[0],M[2]];Mo=[M[1],M[3]]
        S=[]
        for i in range(2):
            v=[0]*4
            for r in range(4):
                for c in range(8): v[r]^=gfm(RS[r][c],key[8*i+c],0x14D)
            S.append(v[0]|(v[1]<<8)|(v[2]<<16)|(v[3]<<24))
        S=S[::-1]
        s.K=[]
        rho=0x01010101
        for i in range(20):
            A=h(2*i*rho,Me);B=rol(h((2*i+1)*rho,Mo),8)
            s.K.append((A+B)&0xffffffff);s.K.append(rol((A+2*B)&0xffffffff,9))
        # 키 의존 S-box 테이블 (속도용)
        sb=[[(S[1]>>(8*i))&255,(S[0]>>(8*i))&255] for i in range(4)]
        s.T=[]
        for i in range(4):
            t=[]
            for x in range(256):
                if i==0: y=q1[q0[q0[x]^sb[0][0]]^sb[0][1]]
                elif i==1: y=q0[q0[q1[x]^sb[1][0]]^sb[1][1]]
                elif i==2: y=q1[q1[q0[x]^sb[2][0]]^sb[2][1]]
                else: y=q0[q1[q1[x]^sb[3][0]]^sb[3][1]]
                t.append(gfm(MDS[0][i],y,0x169)|(gfm(MDS[1][i],y,0x169)<<8)|(gfm(MDS[2][i],y,0x169)<<16)|(gfm(MDS[3][i],y,0x169)<<24))
            s.T.append(t)
    def g(s,X):
        T=s.T;return T[0][X&255]^T[1][(X>>8)&255]^T[2][(X>>16)&255]^T[3][X>>24]
    def enc(s,b):
        K=s.K;R=[int.from_bytes(b[4*i:4*i+4],'little')^K[i] for i in range(4)]
        for r in range(16):
            t0=s.g(R[0]);t1=s.g(rol(R[1],8))
            f0=(t0+t1+K[2*r+8])&0xffffffff;f1=(t0+2*t1+K[2*r+9])&0xffffffff
            R2=ror(R[2]^f0,1);R3=rol(R[3],1)^f1
            R=[R2,R3,R[0],R[1]]
        R=[R[2],R[3],R[0],R[1]]
        return b''.join((R[i]^K[4+i]).to_bytes(4,'little') for i in range(4))
    def dec(s,b):
        K=s.K;R=[int.from_bytes(b[4*i:4*i+4],'little')^K[4+i] for i in range(4)]
        R=[R[2],R[3],R[0],R[1]]
        for r in range(15,-1,-1):
            R0,R1=R[2],R[3]
            t0=s.g(R0);t1=s.g(rol(R1,8))
            f0=(t0+t1+K[2*r+8])&0xffffffff;f1=(t0+2*t1+K[2*r+9])&0xffffffff
            R2=rol(R[0],1)^f0;R3=ror(R[1]^f1,1)
            R=[R0,R1,R2,R3]
        return b''.join((R[i]^K[i]).to_bytes(4,'little') for i in range(4))
    def cbc_dec(s,data,iv):
        out=bytearray();prev=iv
        for i in range(0,len(data)-len(data)%16,16):
            c=data[i:i+16];p=s.dec(c);out+=bytes(a^b for a,b in zip(p,prev));prev=c
        return bytes(out)+data[len(data)-len(data)%16:]
    def cbc_enc(s,data,iv):
        out=bytearray();prev=iv
        for i in range(0,len(data)-len(data)%16,16):
            c=s.enc(bytes(a^b for a,b in zip(data[i:i+16],prev)));out+=c;prev=c
        return bytes(out)+data[len(data)-len(data)%16:]
if __name__=='__main__':
    # 공식 테스트 벡터: key=0, pt=0 -> 9F589F5CF6122C32B6BFEC2F2AE8C35A
    t=Twofish(bytes(16));c=t.enc(bytes(16));print(c.hex().upper(),t.dec(c)==bytes(16))
