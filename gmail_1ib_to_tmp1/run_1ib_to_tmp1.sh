#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
elif command -v py >/dev/null 2>&1; then
  PYTHON_BIN="py -3"
else
  echo "找不到 Python。請先安裝 Python 3。" >&2
  exit 1
fi

if [ ! -f "credentials.json" ]; then
  cat >&2 <<'EOF'
找不到 credentials.json。

第一次設定：
1. 前往 Google Cloud Console。
2. 建立 OAuth Client ID，應用程式類型選「Desktop app」。
3. 下載 JSON 憑證檔。
4. 將檔案放在本資料夾，並命名為 credentials.json。
5. 重新執行這個指令。

第一次成功執行時，程式會開啟瀏覽器要求 Gmail 授權，並在本資料夾儲存 token.json。
之後再執行時，通常只需要一行指令即可完成。
EOF
  exit 1
fi

if [ ! -d ".venv-gmail-routing" ]; then
  $PYTHON_BIN -m venv .venv-gmail-routing
fi

if [ -f ".venv-gmail-routing/Scripts/python.exe" ]; then
  VENV_PY=".venv-gmail-routing/Scripts/python.exe"
else
  VENV_PY=".venv-gmail-routing/bin/python"
fi

"$VENV_PY" -m pip install -q -r requirements-gmail-routing.txt
"$VENV_PY" route_1ib_to_tmp1.py "$@"
