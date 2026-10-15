# 재빌드

검증 환경: Windows 11, Python 3.13, `pip install -r requirements.txt`. xdelta3 실행 파일을 저장소 루트에 `xdelta.exe` 로 둡니다.

저장소 루트에 다음을 둡니다.

- 원본 ISO: `Final Fantasy VII International - Dirge of Cerberus (Undub v1.0).iso`
  (SHA-256 `d7e4146969bea642ddde434da3010a12daf86e6cb948944710b051fa442bbc43`)
- 폰트: `NanumSquareNeo-bRg.ttf`, `NanumSquareNeo-cBd.ttf`, `NanumSquareNeo-dEb.ttf`, `NanumSquareNeo-eHv.ttf`

```powershell
python tools/make_src.py      # 원본 ISO → work/ 원문 데이터 생성, translation/ → work/ 복사
python tools/qa_tr.py         # 누락·제어코드·가나 잔존 검사 (모두 0이어야 함)
python tools/build.py         # → Final Fantasy VII International - Dirge of Cerberus (Korean).iso
.\xdelta.exe -e -f -s "Final Fantasy VII International - Dirge of Cerberus (Undub v1.0).iso" "Final Fantasy VII International - Dirge of Cerberus (Korean).iso" DoC_FF7_International_KO_v1.0.xdelta
```

출력 ISO SHA-256이 README 의 완성 ISO 값과 같아야 합니다.

## 구조 요약

| 대상 | 형식 | 도구 |
|---|---|---|
| `D730AA92/KEL.DAT` + `FILELIST.BIN` | 항목별 zlib, 목록은 zlib 청크 텍스트 | `kel.py`, `filelist.py` |
| 대사·자막·메뉴 문자열 컨테이너 | 64비트 키 8바이트 블록 암호(헤더 키 0x5789A3F195315688 → 본문 키) + zlib | `kelcrypt.py`, `strfile.py`, `dump_strs.py` |
| `kelstr.bin` | 16바이트 XOR + 섹션 표 | `kelstr.py` |
| 메뉴 폰트 `fontdata1.bin` | 512×448 4bpp TIM, 2bpp 2층, SJIS 순 16×16 | `kelfont.py`, `hanglyph.py` |
| 동영상 자막 폰트 `menu_mv.bin` | kelcrypt(키 7)+zlib 청크, 20×16 셀 4bpp | `menumv.py`, `movfont.py` |
| 조작표·로고 이미지 | `.fed` 내 8bpp TIM2 | `imgpatch.py`, `tabletext.py`, `labeltext.py`, `logotext.py` |
| 지역 이름 | 존 설정 파일 오프셋 4, 28바이트 | `build.py` |
| 실행 파일 문구 | `SLPM_666.29` 제자리 치환 | `build.py` |

한글은 SJIS 한자 영역(0x889F~)에 배치하고, 각 폰트의 해당 칸에 글리프를 그립니다. 커진 KEL 항목은 ISO 끝에 덧붙이고 FILELIST·PVD·디렉터리 레코드 크기를 갱신합니다.

`tools/emu.py` 는 PCSX2 백그라운드 확인용(PostMessage 입력, PINE 메모리 읽기)이며 빌드에는 쓰이지 않습니다.
