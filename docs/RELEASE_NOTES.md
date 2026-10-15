# 더지 오브 케르베로스 -FF VII- 인터내셔널 PS2 한글 패치 v1.0

SLPM-66629(인터내셔널, Undub v1.0) 원본용 정식 한글 패치입니다. 첨부 파일은 한글 패치 xdelta와 PCSX2 16:9 와이드 패치 pnach이며, 원본 ISO·게임 파일·폰트는 제공하지 않습니다.

- 이벤트·동영상 자막, 대사, 메뉴·설정·상점, 튜토리얼·도움말, 수집 문서, 엑스트라 미션·특전, 지역 이름 등 일본어 문자열 7,100여 항목 한글화(외부 기계 번역 미사용, 전량 원문 대조 검수).
- 튜토리얼 레퍼런스 조작표 8종·마우스 그림 이름표·타이틀 로고 위 「더지 오브 케르베로스」 이미지 한글화.
- 메뉴·자막 폰트와 동영상 자막 폰트에 한글 1,132자(나눔스퀘어 네오) 추가.
- PCSX2에서 부팅·타이틀·설정·오프닝 자막·첫 전투·메뉴·튜토리얼·특전·와이드 패치 확인, 공개 소스 재빌드 및 xdelta 복원 해시 일치. 전체 플레이, 온라인, 저장/불러오기, 실기는 미검증입니다.

## 첨부 파일

- `DoC_FF7_International_KO_v1.0.xdelta`: 한글 패치(원본 Undub v1.0 ISO용)
- `SLPM-66629_093E5F56.pnach`: PCSX2 16:9 와이드 패치(한글판 CRC 093E5F56용, PCSX2 커뮤니티 패치를 그대로 옮김)

## 한글 패치 적용

1. xdelta3(또는 xdeltaUI)를 준비합니다.
2. 원본 `Final Fantasy VII International - Dirge of Cerberus (Undub v1.0).iso`의 SHA-256이 아래 값과 같은지 확인합니다.
3. 명령: `xdelta3 -d -s "Final Fantasy VII International - Dirge of Cerberus (Undub v1.0).iso" DoC_FF7_International_KO_v1.0.xdelta "Final Fantasy VII International - Dirge of Cerberus (Korean).iso"`
   - xdeltaUI: Patch에 xdelta, Source File에 원본 ISO, Output File에 만들 ISO 이름을 넣고 Patch를 누릅니다.
4. 완성 ISO의 SHA-256이 아래 값과 같으면 정상입니다.

## 16:9 와이드 패치 사용법

한글 패치는 실행 파일을 수정해 게임 CRC가 원본 BC06733B에서 **093E5F56**으로 바뀝니다. PCSX2 내장 와이드 패치는 CRC로 찾으므로 한글판에는 자동 적용되지 않아, 한글판 CRC용 파일을 첨부했습니다.

**PCSX2 2.x(권장)**
1. 첨부한 `SLPM-66629_093E5F56.pnach`를 `문서\PCSX2\patches\`(포터블은 `PCSX2 폴더\patches\`)에 넣습니다.
2. 게임 목록에서 한글판 ISO를 오른쪽 클릭 → 속성 → **패치** 탭 → **Widescreen 16:9** 체크. (항목이 안 보이면 게임을 한 번 실행했다 끈 뒤 다시 엽니다.)
3. 속성 → 그래픽 → 디스플레이에서 화면 비율 **16:9**, FMV 화면 비율 전환 **4:3**(동영상은 원래 4:3).
4. 게임 시작 시 “1개의 게임 패치가 활성화되었습니다” 표시 확인.

설정 파일로 켜려면 `문서\PCSX2\gamesettings\SLPM-66629_093E5F56.ini`에 다음을 저장합니다.

```ini
[EmuCore]
EnableWideScreenPatches = true

[Patches]
Enable = Widescreen 16:9

[EmuCore/GS]
AspectRatio = 16:9
FMVAspectRatioSwitch = 4:3
```

**PCSX2 1.6** — 파일 이름을 `093E5F56.pnach`로 바꿔 `cheats_ws` 폴더에 넣고, 시스템 → 와이드스크린 패치 사용을 켠 뒤 비디오 → 창 설정에서 16:9를 고릅니다.

메뉴·HUD 등 2D 화면은 4:3 기준이라 일부 늘어나 보일 수 있습니다. 끄려면 패치 탭 체크를 해제합니다. 원본(일본어) ISO에는 PCSX2 내장 패치를 쓰면 됩니다. 자세한 내용은 저장소의 docs/WIDESCREEN.md를 보세요.

원본 SHA-256: `d7e4146969bea642ddde434da3010a12daf86e6cb948944710b051fa442bbc43`

완성 ISO SHA-256: `eaa74fef24c7cf9d05e1b5715927d43b7ab5f62c5456bf0fb67cac54cd8ee052`

xdelta SHA-256: `375ce9c13fe7d0f32e76fefcf2510f09f19f333a03cf7fe96fcda3605c74e61c`

와이드 패치 SHA-256: `578141ce409361a8f3550c4566bb89f3685d5319c20e562e86985289aff431ef`
