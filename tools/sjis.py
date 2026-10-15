"""가역 SJIS 코덱: 표준 SJIS 외 2바이트/제어바이트는 {XXXX}/{XX}로 보존"""
import re
def dec(b):
    out=[];i=0
    while i<len(b):
        c=b[i]
        if (0x81<=c<=0x9f or 0xe0<=c<=0xfc) and i+1<len(b):
            pair=b[i:i+2]
            try:
                ch=pair.decode('cp932')
                if ch.encode('cp932')==pair: out.append(ch);i+=2;continue
            except UnicodeDecodeError: pass
            out.append('{%02X%02X}'%(pair[0],pair[1]));i+=2;continue
        if 0x20<=c<0x7f and c not in (0x7b,0x7d): out.append(chr(c))
        elif 0xa1<=c<=0xdf: out.append(bytes([c]).decode('cp932'))
        else: out.append('{%02X}'%c)
        i+=1
    return ''.join(out)
_tok=re.compile(r'\{([0-9A-F]{2}|[0-9A-F]{4})\}')
def enc(s,charmap=None):
    """charmap: dict 문자->bytes (한글 등 사용자 매핑)"""
    out=bytearray();i=0
    while i<len(s):
        m=_tok.match(s,i)
        if m: out+=bytes.fromhex(m.group(1));i=m.end();continue
        ch=s[i]
        if charmap and ch in charmap: out+=charmap[ch]
        else: out+=ch.encode('cp932')
        i+=1
    return bytes(out)
