# UI Style Guide (Trich xuat tu do an Freecell)

Tai lieu nay tong hop style UI hien tai cua Freecell de ban tai su dung cho do an Futoshiki.

## 1) Bang mau (Color Palette)

### 1.1 Mau nen xanh la (game board)

- Primary Green: `#076D1B` (RGB 7,109,27)
- Emerald Dark: `#046238` (RGB 4,98,56)
- Stripe Green (gradient line): `#056416` -> `#057616` (RGB (5,100..118,22), theo tung dong)

Ghi chu:
- Board co 2 che do nen: dung anh (`board_bg_*.jpg`) hoac ve nen xanh + stripe gradient bang line.

### 1.2 Mau cho o bai/o slot (co the map sang o so Futoshiki)

- Slot base (mac dinh): `#E6D25A` (RGB 230,210,90)
- Slot border (vien sang): `#FAF082` (RGB 250,240,130)
- Free Cell group tint: `#046238` (RGB 4,98,56)
- Foundation group tint: `#D4AF37` (RGB 212,175,55)
- Empty-cell overlay (HowTo): `#FFFFFF1E` (trang alpha ~12%)

### 1.3 Mau highlight / hover / accent

- Gold standard: `#D4AF37` (vien, accent, icon ring)
- Gold light: `#FFDF64`
- Gold bright: `#FFD700`
- Label yellow: `#FFF4AA`
- Hover glow card: `#FFDF64` + alpha layer
- Hint button body (burgundy): `#800020`
- Lose overlay dark blue-black: `#0E141C` + alpha
- Victory dim (burnt coffee): `#34150F` + alpha

### 1.4 Mau font chu

- Main light text (menu/button): `#FFFAD2`, `#F5F8D6`, `#FCF8DA`
- Header gold text: `#FAEC96`, `#FFF5A0`, `#FFD700`
- Neutral white: `#FFFFFF`, `#FFFACD`
- Red card text: `#BE1919`
- Black card text: `#121212`

## 2) Cau truc UI (Layout)

### 2.1 Scene map tong the

UI chia theo scene:
- `menu`
- `easy_select`
- `howto`
- `ai_select`
- `game`
- `intro/outro` (video)

### 2.2 Bo cuc man hinh game

Khung chinh:
- Cua so game: `1366 x 990`
- Vung board chiem phan lon man hinh
- Toolbar tron o day man hinh
- HUD o tren (message, hint), goc phai duoi (timer), giua day (playback khi AI)

Chi tiet layout board:
- Card size: `110 x 154`
- Margin X: `26`
- Top Y (hang FreeCell/Foundation): `95`
- Cascade Y: `top_y + card_h + 72` (voi card_h=154 -> `321`)
- Card overlap Y: `max(26, card_h//4)` -> `38`
- So cot:
  - 4 Free Cells (trai)
  - 4 Foundations (phai)
  - 8 Tableau/Cascade (duoi)
- Co vach ngan decor o giua FreeCell va Foundation

### 2.3 Khu vuc menu va status

- Menu chinh:
  - Cac nut trung tam (Manual, AI Solver)
  - 2 nut goc (HowTo, Exit)
  - Title FREECELL o day
- Easy selector:
  - Panel trung tam (chon deal)
  - Prev/Next/Start/Back
- Game status/HUD:
  - Top-left: solver_message / auto-play status
  - Top-right: Hint capsule button
  - Bottom-right: fancy timer
  - Bottom-center: 5 icon tron (New/Replay/Home/Undo/Redo)

## 3) Assets va Fonts

### 3.1 Font dang dung

- `georgia` (chu dao): title/menu/hint/body/labels
- `arialblack`: tieu de VICTORY/GAME OVER
- `arial`: fallback text tren la bai khi thieu image
- `segoeuisymbol`: ky hieu suit (`♠ ♥ ♣ ♦`) trong foundation placeholder

Khuyen nghi cho Futoshiki:
- Giu `georgia` lam font chinh de giu cam giac classic casino.
- Dung 1 font display dam (tuong tu `arialblack`) cho state win/lose.

### 3.2 Xu ly hinh anh/icon

Cach xu ly trong code:
- `pygame.image.load(...).convert()` cho anh nen/JPG
- `convert_alpha()` cho PNG/icon/the bai
- `pygame.transform.smoothscale(...)` de scale card/icon/background
- Card image loader co cache theo key `(rank, suit)` de tranh load lap
- Co fallback renderer neu thieu anh card (ve card bang primitive)

Nhom assets chinh:
- Backgrounds: `background.jpg`, `board_bg_*.jpg`, `selector_bg.jpg`, `howto_bg.png`, `ai_bg.jpg`, `video_bg.jpg`
- Icons: `icon_new.png`, `icon_replay.png`, `icon_home.png`, `icon_undo.png`, `icon_redo.png`, `icon_prev.png`, `icon_play.png`, `icon_next.png`, `icon_stop.png`
- Card sprites: `Source/assets/images/cards/*`
- Audio: `bg_jazz.mp3`, `btn_click.mp3`, `chip_hover.mp3`, `deal.mp3`, `jackpot.wav`, `lose_bgm.mp3`
- Video: `intro.mp4`, `outro.mp4`

## 4) Hanh vi (Interactions)

### 4.1 Hover

- Button hover: doi `base_color` -> `hover_color`
- Vien gold va shadow giup noi khoi nen
- Bottom circular toolbar: hover theo khoang cach tron (distance < radius), vien vang sang hon
- AI selector chips: hover lam sang chip + phat hover sound
- Card hover: neu card nam trong tap nuoc di hop le thi ve glow vang

### 4.2 Click / drag

- Menu:
  - Click Manual mo dropdown do kho
  - Click AI Solver vao scene chon thuat toan
  - Click cac option de chuyen scene
- Board:
  - Mouse down: pick card/sequence hop le
  - Mouse motion: cap nhat drag anchor
  - Mouse up: drop vao target (`freecell/foundation/cascade`) neu hop le
  - Neu khong hop le: snap-back ve vi tri cu
- Toolbar:
  - 5 nut truyen len cac action New/Replay/Home/Undo/Redo
- Hint button: click de request goi y (A*)

### 4.3 Transition va animation

- Scene transition: fade-out/fade-in bang surface den alpha (step 25)
- Deal animation: bai bay tu tren xuong, moi la delay `i*2` frame
- Solver animator:
  - `step_delay_ms = 500`
  - `transition_frames = 10`
  - Noi suy vi tri la bai theo frame
- Victory/Lose:
  - Overlay + particle effects + text animation
  - Co nhac nen va SFX theo state

## 5) Hang so UI (Constants) de giu cam giac classic

### 5.1 Kich thuoc/chia khoi chinh

- Window game: `1366 x 990`
- Card size: `110 x 154`
- Slot corner radius: `8` (inner 7)
- Button corner radius:
  - Nut thuong: `10..14`
  - Capsule hint: radius `26`
  - Nut tron toolbar: radius `30`

### 5.2 Spacing/Padding

- Board margin X: `26`
- Top row Y: `95`
- Khoang cach top row -> cascades: `+72`
- Overlap card theo cot: `38` (voi card_h=154)
- Slot gap ngang: tu dong theo width, min `14`
- Timer anchor: cach le phai/day `20px`
- Hint button: top-right, offset `40px` tu phai, `20px` tu tren
- Bottom toolbar: center_y `h - 60`, gap nut `35`

### 5.3 Animation tuning (co the copy sang Futoshiki)

- Dropdown speed: `0.18`
- Fade alpha step: `25`
- Deal move step: `dx,dy * 0.1` + anti-stuck 1px
- Playback control radius:
  - prev/next: `40`
  - play/pause: `50`
  - stop: `30`

## 6) Goi y map sang Futoshiki

- Nen board: dung cap `#076D1B` + gold accent `#D4AF37` de giu DNA Freecell.
- O so Futoshiki:
  - Normal: ton `#E6D25A` + vien `#FAF082`
  - Selected: burgundy/gold (`#800020` + `#FFD700`)
  - Candidate/hover: glow `#FFDF64` alpha
- HUD:
  - Top-left: status/giai thuat
  - Top-right: hint toggle
  - Bottom-center: action buttons dang tron vien vang

---
Nguon trich: Source/gui/interface.py, Source/gui/menu.py, Source/gui/app.py, Source/gui/hud.py, Source/gui/howto.py, Source/gui/animation.py va Source/assets/.
