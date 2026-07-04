# 健康監控提醒系統設定

## 已建立

- Google Sheet: https://docs.google.com/spreadsheets/d/1gIpLlkLcXMirvUxtlXFp36GeBlCcEMw2Y-AdIY9A3wM/edit
- Spreadsheet ID: `1gIpLlkLcXMirvUxtlXFp36GeBlCcEMw2Y-AdIY9A3wM`
- 喝水時間：`07:40,08:45,10:00,11:00,14:00,15:15,16:30,17:45,20:30,21:45`
- 每杯：250 cc
- 每日目標：2,500 cc

## 你需要手動取得的值

1. Telegram bot token
   - 在 Telegram 搜尋 `@BotFather`
   - 輸入 `/newbot`
   - 建立 bot 後複製 token

2. Telegram chat id
   - 先對你的 bot 傳一則訊息，例如 `開始`
   - 在瀏覽器打開：
     `https://api.telegram.org/bot你的TOKEN/getUpdates`
   - 找到 `chat.id`

## Apps Script 設定

1. 打開 https://script.google.com/
2. 建立新專案，命名為 `健康監控提醒系統`
3. 把本資料夾的 `Code.gs` 全部貼到 Apps Script 的 `Code.gs`
4. 到「專案設定」>「指令碼屬性」，新增：

| 屬性 | 值 |
| --- | --- |
| `SPREADSHEET_ID` | `1gIpLlkLcXMirvUxtlXFp36GeBlCcEMw2Y-AdIY9A3wM` |
| `TELEGRAM_BOT_TOKEN` | 你的 Telegram bot token |
| `TELEGRAM_CHAT_ID` | 你的 chat id |
| `WEBHOOK_SECRET` | 自訂一串密碼，例如 `health-2026-private` |

5. 在 Apps Script 編輯器上方選 `sendTestMessage`，按「執行」
   - 第一次會要求授權
   - Telegram 收到「健康提醒系統測試成功」代表 token/chat id 正確

6. 選 `setupTrigger`，按「執行」
   - 這會建立每分鐘檢查一次的雲端排程

## 部署 Web App 與設定 Webhook

1. Apps Script 右上角「部署」>「新增部署作業」
2. 類型選「網頁應用程式」
3. 執行身分：`我`
4. 誰可以存取：`任何人`
5. 部署後複製 Web App URL
6. 回到「專案設定」>「指令碼屬性」，新增：

| 屬性 | 值 |
| --- | --- |
| `WEB_APP_URL` | 你剛剛複製的 Web App URL |

7. 回 Apps Script 編輯器，選 `setTelegramWebhook`，按「執行」
8. 在 Telegram 對 bot 傳：
   `血壓 128/82 體重 72.4`
9. 到 Google Sheet 的 `Log` 檢查今天那列是否寫入。

## 日常使用

- 喝水提醒出現時，按「已喝 250cc」
- 維他命 C 吃完後，按「已吃維他命 C」
- 血壓體重用文字回覆，例如：
  `血壓 128/82 體重 72.4`

## 備用提醒邏輯

- 17:00 若今天尚未回報維他命 C，才會發備用提醒
- 21:30 若今天尚未完整回報血壓與體重，才會發備用提醒
