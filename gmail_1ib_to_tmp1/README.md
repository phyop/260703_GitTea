# Gmail 1IB 到 tmp1 自動整理工具

這個工具會把 Gmail 中符合條件的券商通知從 `1IB` 搬到 `tmp1`。

「搬到 `tmp1`」代表：

- 加上 `tmp1` 標籤
- 移除 `1IB` 標籤
- 如果信件仍在收件夾，會移除 `INBOX`，讓它不再出現在收件夾

## 規則

以下通知會直接搬移：

- IBKR `Daily Activity Statement`
- IBKR `FYI: Upcoming Exchange Holidays`
- IBKR `FYI: Earnings Notification`

Firstrade 信件會先讀取內容，只搬移登入或帳戶安全確認通知。

IBKR `Message Center Notification` 不會只看標題。程式會讀取信件內容，只有當每一個 numbered item 都是 `Cash Dividend` 相關通知時才搬移。如果包含 `Pending Merger`、投票、稅務、保證金、交易、認購或其他非股息主題，就會保留在 `1IB`。

## 第一次設定

Google 不允許程式在沒有使用者授權的情況下直接存取 Gmail。因此第一次使用前，你需要建立一次 OAuth 憑證。

1. 前往 Google Cloud Console。
2. 建立或選擇一個專案。
3. 啟用 Gmail API。
4. 建立 OAuth Client ID，應用程式類型選擇 `Desktop app`。
5. 如果畫面有提供下載 JSON，請下載 JSON 憑證檔。
6. 將檔案放在本資料夾，並命名為 `credentials.json`。

如果找不到下載 JSON 的按鈕，也可以使用本資料夾內已建立好的
`credentials.json` 範本。請用文字編輯器打開它，找到：

```json
"client_secret": "請把這整段文字替換成你的完整用戶端密碼"
```

把引號內的佔位文字替換成你複製下來的完整用戶端密碼。請保留前後雙引號與逗號，例如：

```json
"client_secret": "你的完整用戶端密碼"
```

不要把用戶端密碼貼到聊天視窗，也不要截圖分享完整密碼。

第一次成功執行時，程式會開啟瀏覽器要求 Gmail 授權，並在本資料夾產生 `token.json`。之後再執行時，通常不需要重新授權。

## PowerShell 執行方式

請使用 PowerShell 執行，不要使用 Git Bash 或 cmd。Git Bash 可能會抓到缺少 SSL 模組的 Python，導致 pip 出現 `ssl module in Python is not available`，無法安裝 Google API 套件。

先預覽，不修改 Gmail：

```powershell
Set-Location "D:\文件\260703_Al_Agent\260703_Gmail_1ib_to_tmp1"
.\run_1ib_to_tmp1.ps1 -DryRun
```

確認規則符合需求後，實際搬移：

```powershell
Set-Location "D:\文件\260703_Al_Agent\260703_Gmail_1ib_to_tmp1"
.\run_1ib_to_tmp1.ps1
```

這個 PowerShell script 會自動建立 `.venv-gmail-routing`，並安裝需要的 Python 套件。

如果 PowerShell 阻擋執行 `.ps1`，請在同一個 PowerShell 視窗先執行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

這只會影響目前這個 PowerShell 視窗。

## 測試

不需要 Gmail 憑證也可以測試分類規則：

```bash
python test_route_rules.py
```

或使用 Windows Python launcher：

```powershell
py -3 test_route_rules.py
```

## 檔案說明

- `route_1ib_to_tmp1.py`：主程式
- `run_1ib_to_tmp1.ps1`：PowerShell 一行執行入口
- `run_1ib_to_tmp1.sh`：Git Bash 備用入口，不建議在你的環境使用
- `requirements-gmail-routing.txt`：Python 依賴清單
- `test_route_rules.py`：本地規則測試
- `credentials.json`：你下載的 Google OAuth 憑證，不應提交到 Git
- `token.json`：第一次授權後自動產生，不應提交到 Git
