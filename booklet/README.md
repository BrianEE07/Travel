# 旅行手冊製作

直接讀取 Vault 的 Schema 2 筆記，使用共用 parser 匯出公開資料。**不需要先建立或部署網頁**，也不讀取 `src/data/trips`。來源筆記與敏感值指紋不進 repository。

## 共用工具與各旅程

- `scripts/layout.py`：A6 字體、文字、照片、時間線與外側頁碼。
- `scripts/imposition.py`：任意 4 的倍數頁數，跨頁預覽、A4 雙面拼版及列印說明。若 A5 葉數為奇數，最後一張 A4 下半留白。
- `scripts/context.py`：旅程設定、公開快照與審閱雜湊檢查。
- `trips/<slug>/book-plan.json`：頁面計畫、字體位置、審閱雜湊、必要事實與輸出名稱。
- `trips/<slug>/render.py`、`artwork.py`：該趟旅程經精簡審閱的排版與文案。
- `trips/<slug>/assets/`、`photo-sources.json`：原始圖片與來源紀錄。
- `references/fukuoka-approved-a6.pdf`：核准版風格參考，不隨重建覆寫。
- `tmp/<slug>/`：公開快照、QA、抽出文字及渲染圖，已忽略。
- `../output/pdf/<slug>/`：閱讀版、跨頁預覽、印刷版與 `PRINTING.md`，不在網站 public/dist。

`output/` 不進 Git；手冊來源圖片和核准版 PDF 仍是本機素材，不因放在 project 就自動授權公開。提交 booklet 素材前另確認散布權利。

此公開 repository 不保存 `references/*.pdf` 或 `trips/*/assets/`，它們已加入忽略規則。本機檔案保留；換電腦或重新 clone 時，需要從自己的備份補齊圖片、字體與核准參考，才可重建原福岡手冊。文字工具與測試不依賴這些素材就能執行。

新旅程沿用共用工具，但需要自己的內容計畫與 renderer；不是把福岡的八天、24 頁、文案或行程複製改名字。Checklist 分類由筆記決定，無固定分類清單。清單網站勾選狀態不會帶入紙本。

## 福岡重建

先用 workspace dependencies 找到有 reportlab、pypdf、pdfplumber、Pillow 的 Python（以下 `python3` 指該 runtime）：

```sh
node booklet/export-source.mjs --note "/absolute/path/福岡之旅 20260827~0903.md"
python3 booklet/build-book.py --slug fukuoka-2026
python3 booklet/verify-book.py --slug fukuoka-2026
node booklet/export-source.mjs --note "/absolute/path/福岡之旅 20260827~0903.md" --verify
pdftoppm -scale-to 1500 -png output/pdf/fukuoka-2026/handbook.pdf booklet/tmp/fukuoka-2026/reading
pdftoppm -scale-to 1500 -png output/pdf/fukuoka-2026/print-a4.pdf booklet/tmp/fukuoka-2026/print
```

`export-source` 也接受 `TRAVEL_NOTE_PATH`，但沒有福岡隱式預設。`--verify` 會重新讀來源，檢查最新 `book-privacy.json` 的來源雜湊，掃描 PDF 文字、連結與 metadata；不是重新匯出後假裝舊 PDF 已更新。公開價格／圖片沿用網站 parser 的精確 allowlist。

`reviewedSourceHash` 不符會停止建置，需審閱受影響時間、精簡文案與提醒再更新 hash。機械檢查涵蓋尺寸、溢出、重疊、缺字、外側頁碼、圖片 DPI、來源時間、拼版內容與折冊閱讀順序。仍必須看所有渲染頁面和印刷面；沒有實際試印不能宣稱印表機已驗證。

## 福岡成果與印刷

24 頁 A6（105 × 148 mm）：`handbook.pdf`。13 畫面跨頁預覽：`facing-spreads.pdf`（不是印刷檔）。6 面 A4：`print-a4.pdf`，雙面印在 3 張紙上。

印刷：A4 直式、100%、雙面長邊翻轉，關閉小冊子／多頁拼印／縮放。先試第一張正反面。沿 148.5 mm 水平裁半成六張 A5 橫式，正面右邊奇數 1、3、5、7、9、11 由外到內疊好，整疊沿 x=105 mm 對折成 A6。頁碼為偶數左下、奇數右下。實體高度 148.5 mm，要求精確 A6 時可最後修去合計 0.5 mm。詳細配頁表由工具生成在 `PRINTING.md`。

舊的根目錄 PDF 保留，不再作為重建輸出。最初五頁樣張仍可用 `build-sample.py` / `verify-sample.py` 檢查；它不是完整可印冊。

## 影像與字體

白底、深藍、低飽和海綠；正文約 10 pt、短時間／標籤 8–8.5 pt、照片來源 6.5 pt。字體路徑設定在各旅程 plan；缺字會失敗，不畫方框替代。保留 Noto Sans JP 授權。

照片必須符合實際地點與季節，裁切不改原圖。來源標示不代表商用或公開散布授權；目前福岡圖片供個人旅行使用。要公開上傳 PDF 前須另查權利，不能因網站已有連結就假定可再散布。

共用拼版回歸測試：`python3 booklet/scripts/test_imposition.py`（4–40 頁配頁，含 4、12、24、32 頁實際 PDF 檢查）。
