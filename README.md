# 더지 오브 케르베로스 -파이널 판타지 VII- 인터내셔널 · PS2 한글 패치 v1.1

대상: **Dirge of Cerberus -Final Fantasy VII- International (Undub v1.0), SLPM-66629**
(일본판 인터내셔널 기반 언덥 ISO)

비공식 팬 한글 패치입니다. 적법하게 보유한 원본 ISO에 xdelta 패치를 적용해 사용합니다.
릴리즈 첨부 파일은 xdelta와 PCSX2용 16:9 와이드 패치(pnach)이며 원본·완성 ISO, 게임 파일, 폰트는 배포하지 않습니다.

## 패치 적용

| 파일 | SHA-256 |
|---|---|
| 원본 `Final Fantasy VII International - Dirge of Cerberus (Undub v1.0).iso` (4,005,664,768바이트) | `d7e4146969bea642ddde434da3010a12daf86e6cb948944710b051fa442bbc43` |
| 완성 `Final Fantasy VII International - Dirge of Cerberus (Korean).iso` (4,005,986,304바이트) | `e7fa4dd72b2607ed337be16e6361583277824f1955c71961f283c6d17fba764c` |
| `DoC_FF7_International_KO_v1.1.xdelta` | `08863f2160f57c45b919f48672cadd0df7417a50af3b2834462649011620584c` |

```powershell
xdelta3 -d -s ".\Final Fantasy VII International - Dirge of Cerberus (Undub v1.0).iso" .\DoC_FF7_International_KO_v1.1.xdelta ".\Final Fantasy VII International - Dirge of Cerberus (Korean).iso"
```

## BIOS 언어와 관계없이 한글 표시 (v1.1)

원본 게임은 PS2 본체(BIOS) 언어 설정에 따라 일본어/영어 데이터를 고르기 때문에, v1.0은 영문 BIOS 실기·에뮬레이터에서
영어로만 나왔습니다. v1.1은 실행 파일의 언어 저장 명령 1개(0x242448 `sw a0` → `sw zero`)를 고쳐 BIOS 언어와 관계없이
항상 한글 데이터를 쓰도록 했습니다. 이 때문에 게임 CRC가 **093A5F56**으로 바뀌었고 와이드 패치도 새 CRC용으로 교체했습니다.

## 16:9 와이드 패치

한글 패치는 실행 파일 문구를 수정하므로 게임 CRC가 원본(BC06733B)과 달리 **093A5F56**이 됩니다. 그래서 PCSX2에
내장된 원본용 와이드 패치는 자동으로 적용되지 않습니다. 릴리즈에 한글판 CRC용 `SLPM-66629_093A5F56.pnach`를
함께 첨부합니다(PCSX2 커뮤니티 패치를 그대로 옮기고 파일 이름·CRC만 맞춤). 사용법은 [docs/WIDESCREEN.md](docs/WIDESCREEN.md).

## 번역 범위

- 게임 텍스트: 이벤트·동영상 자막, 무전·필드 대사, 메뉴·설정·상점·세이브 안내, 튜토리얼·도움말, 수집 문서(오메가 리포트 등),
  엑스트라 미션·특전, 지역/미션 이름 등 일본어 문자열 6,991종 + 추가 11종 + 지역 이름 124종.
- 이미지: 튜토리얼 레퍼런스 조작표 8종, 마우스 그림 이름표, 타이틀 로고 위 「더지 오브 케르베로스」.
- 외부 번역기·기계 번역 없이 직접 번역하고 전량 원문 대조 검수했습니다. 용어는 [translation/glossary.md](translation/glossary.md) 기준.

## 한글 표시 방식

1. **인코딩**: 게임은 Shift-JIS. 한글 1,132자를 SJIS 한자 영역(0x889F~)에 배치.
2. **폰트**: 메뉴·자막 폰트 `fontdata1.bin`(512×448 4bpp, 2bpp 2층) 3종과 동영상 자막 폰트(`menu_mv.bin` 안 20×16 셀 4bpp) 3종에
   나눔스퀘어 네오로 글리프를 그려 넣음.
3. **문자열**: KEL.DAT 항목은 64비트 키 8바이트 블록 암호 + zlib. 복호 → 교체 → 재암호화. 헤더의 문자열 복사 버퍼 크기를 원본 규칙대로 기록.
4. **이미지**: `.fed` 이펙트 파일 속 8bpp TIM2를 칸 단위로 지우고 한글로 다시 그림.
5. **ISO**: 커진 항목은 ISO 끝에 붙이고 FILELIST.BIN·PVD·디렉터리 레코드 갱신.

## 검증

- PCSX2 2.2(일본 BIOS 및 유럽판 영문 BIOS SCPH-70004): 부팅, 타이틀 로고, 난이도·메모리 카드 안내, 설정, 오프닝 동영상 자막, 첫 전투, 일시정지·게임 내 메뉴,
  튜토리얼(안내·모드 선택·레퍼런스 조작표), 특전 메뉴, 16:9 와이드 패치 적용.
- 공개 저장소만으로 재빌드한 ISO와 xdelta 복원 ISO의 SHA-256 일치.
- **미검증**: 전체 플레이, 온라인 기능, 저장/불러오기, 실기.

## 남은 일본어

개발용 이벤트·존 목록, 스크립트 내부 라벨, 디버그 기능 문구 등 일반 플레이 화면에 나오지 않는 문자열.
키보드 그림의 자판 글자(일본어 자판 배열 그림)와 로고 그림.

## 저장소 구성

- `translation/ko_units.tsv`: 번호·문자열 ID·한국어(일본어 원문 미포함, `tools/make_src.py`로 원본에서 로컬 생성)
- `translation/*.json`: 추가 문자열(원문은 MD5 키)·장식 문자열·실행 파일 문구·이미지 매핑
- `tools/`: 빌드·분석 도구, 재빌드는 [docs/BUILD.md](docs/BUILD.md)
- `widescreen/`: PCSX2 16:9 와이드 패치
- 권리 고지 [RIGHTS.md](RIGHTS.md), 변경 내역 [CHANGELOG.md](CHANGELOG.md)
