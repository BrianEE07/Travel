# Travel 網域遷移

本次範圍：`travel.weiweifan.com` → `travel.yungwei.com`。其他網站另案處理，不變更整個網域的 nameservers。

## 決策與目前進度

- 新網域留在 Namecheap DNS；網站繼續使用 `BrianEE07/Travel` 的 GitHub Pages / Actions。
- Wei 已完成 GitHub 帳號的 `yungwei.com` 所有權驗證；驗證 TXT 保留。
- 2026-10-26：新 `travel` CNAME 已生效，版本已推送並成功部署；GitHub Pages 已改綁 `travel.yungwei.com`，新憑證已核發且強制 HTTPS 已開啟。Wei 後續決定不設舊站轉址，並已自行刪除 Cloudflare 的舊 `travel` CNAME；權威 DNS 驗證已停止解析。
- 不搬移 localStorage 清單狀態，不重製既有 PDF；只更新未來手冊使用的網站連結。
- Wei 表示舊網域 12/19 到期且不續費；到期後不要求舊網址繼續導向。不要讓新網站依賴舊網域。

## 可重用的流程

1. **盤點**：確認註冊商、權威 DNS、實際主機平台、repo／分支、目前 custom domain、HTTPS、快取、分享與素材網址。記下回復所需的舊設定；不把登入資料放進 Git。
2. **驗證所有權**：先完成 GitHub 帳號的根網域驗證。這保護同帳號的直接子網域，不是網站的 CNAME 設定；不要使用 wildcard DNS。
3. **準備版本**：更新 Astro `site`、`public/CNAME`、未來手冊連結與 SW 版本。現有根目錄相對路徑可保留。檢查 canonical、OG、manifest、內部／分享連結、圖片、字型與離線資源；以封鎖舊網域的瀏覽器驗證不依賴它。不要順便重同步無關行程。
4. **協調切換**：GitHub 一個 Pages 站不能同時綁兩個任意 custom domains。官方建議先綁 Pages 再加 DNS；這可能造成舊站短暫中斷。本次已驗證根網域，也可先準備新 CNAME、確認 DNS 後再協調改綁，降低中斷；不要把這當成未驗證網域的通用做法。尚未改綁前，新網址不保證可用。
5. **Namecheap**：Domain List → `yungwei.com` Manage → Advanced DNS → Host Records。新增 CNAME：Host `travel`，Value `brianee07.github.io`，TTL Automatic。同 Host 不並存衝突的 A／AAAA／Redirect；不加協定或 `/Travel`，不動 `@`、`www` 或驗證 TXT。
6. **發布與綁定**：逐檔審閱、只提交遷移範圍，確認 Actions 成功；GitHub repo → Settings → Pages → Custom domain 設為 `travel.yungwei.com`。Actions 部署忽略 `CNAME` 檔，不能只改檔案而漏改 Pages 設定。確認憑證成功後啟用 Enforce HTTPS；不承諾立即完成，DNS／HTTPS 可能需要最多 24 小時。
7. **驗收**：首頁、行程、清單、舊 `/trips/<slug>/` 入口、modal、日期跳轉、分享、圖片、canonical／OG、manifest／SW／離線均檢查。用新 origin 的乾淨瀏覽器測試；必要時重新加入主畫面。不能把本機建置稱為已上線。
8. **舊站過渡（按需求選擇）**：本次依 Wei 決定不設轉址，確認新站正常後只刪除舊 `travel` DNS。若未來其他網站另有保留轉址需求，再依當次授權設定 edge redirect 並驗證 path／query；不要把轉址當成所有遷移的必要步驟。不要依賴已解除綁定的 Pages 繼續服務，也不要殘留指向它的 DNS。
9. **退場／回復**：新站穩定後移除不再需要的舊 redirect／DNS。舊域名到期後無法控制其內容，不能保證舊連結安全。若新站失敗，依快照協調恢復舊 Pages domain／DNS／發布版本；只回復本次檔案，不覆蓋其他人的工作。

## 驗收紀錄

- 本機準備：28 項測試通過、35 個 Astro 檔案檢查無錯誤／警告，6 個頁面建置完成；使用現有來源筆記的私人指紋掃描 11 份公開檔案通過，未重同步行程 JSON。輸出檔無舊網域字串，canonical／OG 指向新 origin。手冊 renderer 僅驗語法，未產生 PDF。
- 本機瀏覽器：封鎖舊網域後，首頁／行程／清單／舊路由入口皆通過；390px 手機寬度無橫向溢出，無舊網域請求或 JavaScript 執行錯誤。既有 meta CSP 的 `frame-ancestors` 提示仍存在，未宣稱等同 HTTP header 防護。本機預覽與測試瀏覽器已關閉。
- 網站 revision：`c96dcabf07eec6b74adad54ea147c6a90cb236da`；[Actions 40284868787](https://github.com/BrianEE07/Travel/actions/runs/40284868787) 成功。僅發布網域設定、SW 版本、未來手冊連結和回歸測試，行程 JSON 未變更。
- 新 DNS：兩台 Namecheap 權威 DNS 與公共 DNS 均確認 `travel.yungwei.com CNAME brianee07.github.io`。GitHub Pages custom domain 與 protected domain state 分別為新 hostname／verified。
- HTTPS：新憑證 approved（到期 2027-01-24），Enforce HTTPS 已開啟；正常 TLS 驗證下首頁 HTTP 200，HTTP 清單路徑以 301 保留路徑導向 HTTPS。
- 新站瀏覽器：封鎖舊網域後，首頁／福岡／清單／舊 `/trips/fukuoka-2026/` 入口皆正常；canonical／OG 與站內程式／樣式使用新 origin，舊網域請求 0、JavaScript 執行錯誤 0。分享按鈕輸出新福岡網址（用測試替身接收，未覆寫使用者剪貼簿）；390px 寬度無橫向溢出。新 origin 的 SW 已 activated，快取為 `wei-travel-v28-assets`／`wei-travel-v28-pages`；本次未認證完整離線情境。
- 舊 travel：改綁初期為 HTTP 404；Wei 決定不轉址並刪除殘留 CNAME 後，`serena.ns.cloudflare.com` 與 `clyde.ns.cloudflare.com` 權威查詢均回 NXDOMAIN。舊入口已停用，不是兩個網址同時服務。
- 刪除後回歸檢查：新首頁／福岡／清單均 HTTP 200；舊 `weiweifan.com` 主站與 `portfolio.weiweifan.com` 也均 HTTP 200，這兩站尚未遷移。已補充通知 Brian 以此現況更新大腦入口；Jason 僅完成舊 styles 依賴的唯讀查核，沒有代為移除其他服務。

## 舊網址退場結案

本次只刪除 `weiweifan.com` 的 `CNAME travel → brianee07.github.io`，由 Wei 在 Cloudflare 操作、Adrian 核對公開 DNS。沒有新增 redirect 或佔位 A 紀錄，也沒有刪除整個 zone。

- `@`、`www`、`portfolio`、`styles` 與共用驗證／登入設定不在本次刪除範圍，不能照此筆紀錄一併清除。
- 公共解析器或裝置可能暫留舊 DNS 快取；是否刪除成功以權威 DNS 回應確認，新站使用自己的新域名，不依賴快取消退。
- 若誤刪需要回復，可依原值重建該單筆 CNAME；但目前 Pages 已綁新網域，單純恢復舊 DNS 不會恢復舊站服務。沒有新的授權，不應重新加回舊綁定或轉址。
- 12/19 到期後不承諾舊連結可用。歷史筆記、既有 PDF、備份與部署證據保留原狀；只更新仍作現行入口的連結與描述。

## 官方參考

- [GitHub custom domain 設定](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)
- [GitHub domain verification](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages)
- [Namecheap Host Records](https://www.namecheap.com/support/knowledgebase/article.aspx/434/2237/how-do-i-set-up-host-records-for-a-domain/)
- [Cloudflare redirect domain](https://developers.cloudflare.com/fundamentals/manage-domains/redirect-domain/)
