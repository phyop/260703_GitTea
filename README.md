# Weekly Report AI Agent

這個專案用來管理與查詢每週報告資料。你可以匯入 Markdown 週報，建立本地索引，之後用命令列或網頁介面查詢內容。

## 基本用法

初始化週報索引：

```powershell
python weekly_agent.py init --source "D:\文件\220825_OVT\220825_ABK\220818_weekly\Weekly_All\___Weekly.md"
```

查詢問題：

```powershell
python weekly_agent.py ask "OX03G10 最近有哪些進展？"
```

啟動互動式聊天：

```powershell
python weekly_agent.py chat
```

啟動網頁介面：

```powershell
python weekly_agent.py web
```

預設網址：

```text
http://127.0.0.1:8765
```

如果 8765 連接埠已被使用，可以改用其他連接埠：

```powershell
python weekly_agent.py web --port 8766
```

對應網址：

```text
http://127.0.0.1:8766
```

## OpenAI API 金鑰

如果要使用需要語言模型或網路搜尋的功能，請先設定 `OPENAI_API_KEY`：

```powershell
$env:OPENAI_API_KEY="你的 API key"
python weekly_agent.py web
```

如果沒有設定 `OPENAI_API_KEY`，仍可使用本地索引查詢，但需要模型或網路搜尋的功能會受限。

## 更新週報

匯入新的週報：

```powershell
python weekly_agent.py update --new-week "D:\...\Y26W27.md"
```

如果要同時追加到主週報檔：

```powershell
python weekly_agent.py update --new-week "D:\...\Y26W27.md" --append-to-master
```

## HTML 匯入

如果來源同時有 Markdown 與 HTML，可以一起匯入，讓系統保留更完整的段落與連結資訊：

```powershell
python weekly_agent.py init --source "D:\...\___Weekly.md" --html "D:\...\___Weekly.html"
```

## 專案資料

- 索引資料：`.weekly_agent/index.jsonl`
- 設定檔：`.weekly_agent/config.json`
- 匯入紀錄：`.weekly_agent/imports.json`

## Windows 使用提醒

如果 `python` 指令不可用，可以改用：

```powershell
py weekly_agent.py status
```

如果 PowerShell 顯示中文亂碼，可以先切換成 UTF-8：

```powershell
chcp 65001
```
