#!/usr/bin/env python3
"""將指定的 1IB 券商通知搬移到 tmp1。

使用方式：
  ./run_1ib_to_tmp1.sh --dry-run
  ./run_1ib_to_tmp1.sh

第一次執行前，請先依照 README.md 建立 Google OAuth Desktop 憑證，
並將下載的 JSON 檔放在本資料夾，命名為 credentials.json。
"""

from __future__ import annotations

import argparse
import base64
import re
from dataclasses import dataclass
from email.header import decode_header
from pathlib import Path
from typing import Iterable


SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
TMP_LABEL = "tmp1"
SOURCE_LABEL = "1IB"
BASE_DIR = Path(__file__).resolve().parent
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"

DIRECT_QUERIES = [
    '{in:inbox label:1IB} from:donotreply@interactivebrokers.com '
    'subject:"Daily Activity Statement" newer_than:30d',
    '{in:inbox label:1IB} from:donotreply@interactivebrokers.com '
    'subject:"FYI: Upcoming Exchange Holidays" newer_than:30d',
    '{in:inbox label:1IB} from:donotreply@interactivebrokers.com '
    'subject:"FYI: Earnings Notification" newer_than:30d',
]

FIRSTRADE_QUERY = '{in:inbox label:1IB} from:sender@firstrade.com newer_than:30d'
MESSAGE_CENTER_QUERY = (
    '{in:inbox label:1IB} from:donotreply@interactivebrokers.com '
    'subject:"Message Center Notification" newer_than:30d'
)

NON_DIVIDEND_TOPICS = [
    "pending merger",
    "merger",
    "voluntary",
    "mandatory",
    "tender",
    "subscription",
    "voting",
    "margin",
    "tax",
    "trade",
]


@dataclass
class Message:
    message_id: str
    subject: str
    text: str


def build_service():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    f"找不到 {CREDENTIALS_FILE}。請先建立 Google OAuth Desktop "
                    "憑證，下載 JSON 後存成 credentials.json。"
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w", encoding="utf-8") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def decode_mime_header(value: str) -> str:
    chunks = []
    for chunk, encoding in decode_header(value or ""):
        if isinstance(chunk, bytes):
            chunks.append(chunk.decode(encoding or "utf-8", errors="replace"))
        else:
            chunks.append(chunk)
    return "".join(chunks)


def get_header(payload: dict, name: str) -> str:
    for header in payload.get("headers", []):
        if header.get("name", "").lower() == name.lower():
            return decode_mime_header(header.get("value", ""))
    return ""


def decode_body(data: str | None) -> str:
    if not data:
        return ""
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding).decode("utf-8", errors="replace")


def payload_text(payload: dict) -> str:
    mime_type = payload.get("mimeType", "")
    body_text = decode_body(payload.get("body", {}).get("data"))
    parts = payload.get("parts", [])
    if mime_type == "text/plain" and body_text:
        return body_text
    if not parts:
        return body_text
    texts = [payload_text(part) for part in parts]
    return "\n".join(text for text in texts if text)


def list_label_ids(service) -> dict[str, str]:
    response = service.users().labels().list(userId="me").execute()
    return {label["name"]: label["id"] for label in response.get("labels", [])}


def ensure_label(service, name: str) -> str:
    labels = list_label_ids(service)
    if name in labels:
        return labels[name]
    created = (
        service.users()
        .labels()
        .create(
            userId="me",
            body={
                "name": name,
                "labelListVisibility": "labelShow",
                "messageListVisibility": "show",
            },
        )
        .execute()
    )
    return created["id"]


def search_ids(service, query: str, max_results: int = 100) -> list[str]:
    ids: list[str] = []
    token = None
    while True:
        request = service.users().messages().list(
            userId="me",
            q=query,
            maxResults=min(100, max_results),
            pageToken=token,
        )
        response = request.execute()
        ids.extend(message["id"] for message in response.get("messages", []))
        token = response.get("nextPageToken")
        if not token or len(ids) >= max_results:
            return ids[:max_results]


def read_message(service, message_id: str) -> Message:
    raw = service.users().messages().get(userId="me", id=message_id, format="full").execute()
    payload = raw.get("payload", {})
    return Message(
        message_id=message_id,
        subject=get_header(payload, "Subject"),
        text=payload_text(payload),
    )


def move_to_tmp1(service, message_ids: Iterable[str], dry_run: bool) -> int:
    ids = list(dict.fromkeys(message_ids))
    if not ids:
        return 0
    labels = list_label_ids(service)
    tmp_id = ensure_label(service, TMP_LABEL)
    remove_ids = ["INBOX"]
    if SOURCE_LABEL in labels:
        remove_ids.append(labels[SOURCE_LABEL])
    if dry_run:
        print(f"[預覽] 會搬移 {len(ids)} 封信：{ids}")
        return len(ids)
    service.users().messages().batchModify(
        userId="me",
        body={"ids": ids, "addLabelIds": [tmp_id], "removeLabelIds": remove_ids},
    ).execute()
    return len(ids)


def is_firstrade_login_notice(message: Message) -> bool:
    text = f"{message.subject}\n{message.text}".lower()
    brand_markers = ["firstrade", "第一證券", "第一证券"]
    login_markers = ["login", "log in", "sign in", "登入", "登錄", "登录"]
    security_markers = ["security", "account", "帳戶", "賬戶", "账户", "安全"]
    return (
        any(marker in text for marker in brand_markers)
        and any(marker in text for marker in login_markers)
        and any(marker in text for marker in security_markers)
    )


def is_cash_dividend_only(message: Message) -> bool:
    text = message.text
    lower = text.lower()
    if any(topic in lower for topic in NON_DIVIDEND_TOPICS):
        return False

    item_headers = re.findall(r"(?m)^\s*\d+\s+([A-Za-z][^\n:]*:[^\n]+)", text)
    if not item_headers:
        return "cash dividend" in lower and "message notification(s)" in lower
    return all("cash dividend" in header.lower() for header in item_headers)


def main() -> int:
    parser = argparse.ArgumentParser(description="將符合規則的 1IB 信件搬到 tmp1。")
    parser.add_argument("--dry-run", action="store_true", help="只預覽，不修改 Gmail。")
    args = parser.parse_args()

    service = build_service()
    moved_direct = 0
    for query in DIRECT_QUERIES:
        ids = search_ids(service, query)
        moved_direct += move_to_tmp1(service, ids, args.dry_run)

    firstrade = [read_message(service, mid) for mid in search_ids(service, FIRSTRADE_QUERY)]
    moved_firstrade = move_to_tmp1(
        service,
        [message.message_id for message in firstrade if is_firstrade_login_notice(message)],
        args.dry_run,
    )

    center = [read_message(service, mid) for mid in search_ids(service, MESSAGE_CENTER_QUERY)]
    cash_dividend_ids = [
        message.message_id for message in center if is_cash_dividend_only(message)
    ]
    moved_center = move_to_tmp1(service, cash_dividend_ids, args.dry_run)

    print(f"直接通知搬移數：{moved_direct}")
    print(f"Firstrade 候選檢查數：{len(firstrade)}，搬移數：{moved_firstrade}")
    print(f"Message Center 候選檢查數：{len(center)}，搬移數：{moved_center}")
    print(f"Message Center 保留不動數：{len(center) - moved_center}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
