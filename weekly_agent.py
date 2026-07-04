#!/usr/bin/env python3
import argparse
import hashlib
import mimetypes
import json
import math
import os
import re
import sys
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

APP_DIR = Path(".weekly_agent")
CONFIG_PATH = APP_DIR / "config.json"
INDEX_PATH = APP_DIR / "index.jsonl"
IMPORTS_PATH = APP_DIR / "imports.json"
SECRETS_PATH = APP_DIR / "secrets.json"
WEB_DIR = Path("web")

WEEK_RE = re.compile(r"^#\s+Weekly Report\s*-\s*(Y(?P<year>\d{2})W(?P<week>\d{2}))\s*$", re.I)
DATE_RE = re.compile(r"^>\s*(\d{4}/\d{2}/\d{2})\s*$")
TOKEN_RE = re.compile(r"[A-Za-z0-9_./+-]{2,}|[\u4e00-\u9fff]")


def read_text(path):
    for encoding in ("utf-8-sig", "utf-8", "cp950", "big5"):
        try:
            return Path(path).read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return Path(path).read_text(encoding="utf-8", errors="replace")


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def get_openai_key():
    env_key = os.environ.get("OPENAI_API_KEY")
    if env_key:
        return env_key
    secrets = read_json(SECRETS_PATH, {})
    return secrets.get("OPENAI_API_KEY") or ""


def mask_secret(value):
    if not value:
        return ""
    if len(value) <= 8:
        return "*" * len(value)
    return value[:3] + "..." + value[-4:]


def set_openai_key(api_key):
    api_key = (api_key or "").strip()
    if not api_key:
        raise ValueError("API key 不可為空。")
    if not api_key.startswith("sk-"):
        raise ValueError("API key 格式看起來不正確，通常會以 sk- 開頭。")
    data = read_json(SECRETS_PATH, {})
    data["OPENAI_API_KEY"] = api_key
    write_json(SECRETS_PATH, data)


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def normalize_week(yw):
    match = re.match(r"Y(\d{2})W(\d{2})", yw, re.I)
    if not match:
        return yw
    return f"W{match.group(2)}Y{match.group(1)}"


def html_anchor(title):
    anchor = title.strip().lower()
    anchor = re.sub(r"[^\w\u4e00-\u9fff\s-]", "", anchor)
    anchor = re.sub(r"\s+", "-", anchor)
    return "#" + anchor


def split_week_sections(text, source_path):
    lines = text.splitlines()
    starts = []
    for idx, line in enumerate(lines):
        match = WEEK_RE.match(line.strip())
        if match:
            starts.append((idx, match.group(0), match.group(1).upper()))

    sections = []
    for pos, (start_idx, title, raw_week) in enumerate(starts):
        end_idx = starts[pos + 1][0] if pos + 1 < len(starts) else len(lines)
        section_lines = lines[start_idx:end_idx]
        date = ""
        if len(section_lines) > 1:
            date_match = DATE_RE.match(section_lines[1].strip())
            if date_match:
                date = date_match.group(1)
        sections.append(
            {
                "source_path": str(source_path),
                "raw_week": raw_week,
                "week": normalize_week(raw_week),
                "title": title.lstrip("#").strip(),
                "date": date,
                "start_line": start_idx + 1,
                "end_line": end_idx,
                "text": "\n".join(section_lines).strip(),
            }
        )
    return sections


def chunk_section(section, max_chars=2200, overlap=250):
    text = section["text"]
    if len(text) <= max_chars:
        item = dict(section)
        item["chunk_id"] = f"{section['raw_week']}:001"
        item["chunk_index"] = 1
        return [item]

    chunks = []
    start = 0
    index = 1
    while start < len(text):
        end = min(len(text), start + max_chars)
        if end < len(text):
            cut = text.rfind("\n", start, end)
            if cut > start + max_chars // 2:
                end = cut
        item = dict(section)
        item["text"] = text[start:end].strip()
        item["chunk_id"] = f"{section['raw_week']}:{index:03d}"
        item["chunk_index"] = index
        chunks.append(item)
        if end >= len(text):
            break
        start = max(0, end - overlap)
        index += 1
    return chunks


def tokenize(text):
    text = text.lower()
    base = TOKEN_RE.findall(text)
    terms = []
    cjk_buffer = []
    for token in base:
        if len(token) == 1 and "\u4e00" <= token <= "\u9fff":
            cjk_buffer.append(token)
        else:
            if cjk_buffer:
                joined = "".join(cjk_buffer)
                terms.extend(joined[i : i + 2] for i in range(max(0, len(joined) - 1)))
                cjk_buffer = []
            terms.append(token)
    if cjk_buffer:
        joined = "".join(cjk_buffer)
        terms.extend(joined[i : i + 2] for i in range(max(0, len(joined) - 1)))
    return [term for term in terms if term.strip()]


def build_index(source_paths, html_path=None):
    docs = []
    seen = set()
    for source in source_paths:
        source = Path(source)
        text = read_text(source)
        digest = sha256_text(text)
        if digest in seen:
            continue
        seen.add(digest)
        for section in split_week_sections(text, source):
            docs.extend(chunk_section(section))

    if not docs:
        raise SystemExit("找不到任何 '# Weekly Report - YxxWxx' 週報標題，請確認來源格式。")

    APP_DIR.mkdir(parents=True, exist_ok=True)
    with INDEX_PATH.open("w", encoding="utf-8") as f:
        for doc in docs:
            doc["html_path"] = str(html_path) if html_path else ""
            doc["html_anchor"] = html_anchor(doc["title"])
            doc["tokens"] = tokenize(doc["text"])
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")

    config = {
        "master_source": str(source_paths[0]),
        "html_path": str(html_path) if html_path else "",
        "last_indexed_at": datetime.now().isoformat(timespec="seconds"),
        "source_paths": [str(p) for p in source_paths],
        "chunk_count": len(docs),
    }
    write_json(CONFIG_PATH, config)
    return config


def load_index():
    if not INDEX_PATH.exists():
        raise SystemExit("尚未建立索引，請先執行：python weekly_agent.py init --source <週報.md>")
    docs = []
    with INDEX_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                docs.append(json.loads(line))
    return docs


def retrieve(query, top_k=8):
    docs = load_index()
    query_terms = tokenize(query)
    if not query_terms:
        return []

    df = defaultdict(int)
    doc_tfs = []
    for doc in docs:
        tf = Counter(doc.get("tokens") or tokenize(doc["text"]))
        doc_tfs.append(tf)
        for term in tf:
            df[term] += 1

    avg_len = sum(sum(tf.values()) for tf in doc_tfs) / max(1, len(doc_tfs))
    query_tf = Counter(query_terms)
    scored = []
    for doc, tf in zip(docs, doc_tfs):
        length = sum(tf.values()) or 1
        score = 0.0
        for term, q_weight in query_tf.items():
            if term not in tf:
                continue
            idf = math.log(1 + (len(docs) - df[term] + 0.5) / (df[term] + 0.5))
            denom = tf[term] + 1.2 * (1 - 0.75 + 0.75 * length / max(1, avg_len))
            score += idf * (tf[term] * 2.2 / denom) * (1 + math.log(q_weight))
        if score > 0:
            scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [{"score": round(score, 4), **doc} for score, doc in scored[:top_k]]


def make_snippet(text, query, width=520):
    terms = [term for term in tokenize(query) if len(term) >= 2]
    lowered = text.lower()
    hit = -1
    for term in terms:
        hit = lowered.find(term.lower())
        if hit >= 0:
            break
    if hit < 0:
        return textwrap.shorten(" ".join(text.split()), width=width, placeholder=" ...")

    start = max(0, hit - width // 3)
    end = min(len(text), start + width)
    snippet = " ".join(text[start:end].split())
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(text) else ""
    return prefix + snippet + suffix


def compact_evidence(results, query):
    blocks = []
    for idx, item in enumerate(results, 1):
        snippet = make_snippet(item["text"], query, width=1400)
        blocks.append(
            f"[{idx}] {item['raw_week']} ({item.get('date') or 'no date'}), "
            f"{Path(item['source_path']).name}:{item['start_line']}, "
            f"anchor={item.get('html_anchor','')}\n{snippet}"
        )
    return "\n\n".join(blocks)


def choose_top_k(query, requested=None):
    if requested:
        return max(3, min(20, int(requested)))
    terms = tokenize(query)
    if len(terms) <= 4:
        return 6
    if len(terms) <= 12:
        return 8
    return 10


def call_openai(query, results, use_web=False, model="gpt-4.1-mini"):
    api_key = get_openai_key()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY 尚未設定。可用左側設定面板儲存 key，或在啟動 server 的 PowerShell 先設定 key。")

    prompt = f"""你是 Sean Liu 的週報 AI Agent。
請用繁體中文回答。你必須：
1. 先根據「週報證據」回答，且每個重要結論附上週別引用，例如 (Y26W26)。
2. 如果週報證據不足，要明說。
3. 另外提供「Agent 補充觀點」，可使用一般工程知識；若本次有 Web Search，請把外部資訊和週報證據分開。
4. 最後列出引用來源，只使用 YxxWxx 格式、日期與行號；不要重複列 WxxYxx，也不要列 HTML anchor。

問題：
{query}

週報證據：
{compact_evidence(results, query)}
"""
    payload = {
        "model": model,
        "input": prompt,
    }
    if use_web:
        payload["tools"] = [{"type": "web_search_preview"}]

    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"OpenAI API 呼叫失敗：{exc.code}\n{detail}")
    except urllib.error.URLError as exc:
        raise SystemExit(f"OpenAI API 連線失敗：{exc}")

    texts = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in ("output_text", "text"):
                texts.append(content.get("text", ""))
    return "\n".join(texts).strip() or json.dumps(data, ensure_ascii=False, indent=2)


def local_answer(query, results):
    if not results:
        return "週報證據不足：索引中找不到明顯相關內容。你可以換一組關鍵字，或確認新週報是否已 update。"

    lines = ["## 週報回答", ""]
    lines.append("我找到以下幾個最相關的週報位置。")
    lines.append("")
    for item in results[:5]:
        lines.append(f"- {item['raw_week']}：{item.get('date') or 'no date'}，line {item['start_line']}，相關度 {item['score']}")
    lines.append("")
    lines.append("## Agent 補充觀點")
    lines.append("目前是本機檢索模式，主回答先保持保守，只列出週報證據位置。若要自動整理成完整結論，請設定 OpenAI key 後啟用 OpenAI 整理。")
    lines.append("")
    lines.append("## 引用位置")
    for item in results[:5]:
        lines.append(f"- {item['raw_week']} / {item.get('date') or 'no date'} / line {item['start_line']}")
    return "\n".join(lines)


def cmd_init(args):
    config = build_index([Path(args.source)], html_path=Path(args.html) if args.html else None)
    write_json(IMPORTS_PATH, [])
    print(f"完成索引：{config['chunk_count']} 個片段")
    print(f"設定檔：{CONFIG_PATH}")


def cmd_update(args):
    config = read_json(CONFIG_PATH, {})
    if not config:
        raise SystemExit("尚未 init，請先建立主索引。")

    imports = read_json(IMPORTS_PATH, [])
    new_week = Path(args.new_week)
    new_text = read_text(new_week)
    digest = sha256_text(new_text)
    if not any(item.get("sha256") == digest for item in imports):
        imports.append({"path": str(new_week), "sha256": digest, "imported_at": datetime.now().isoformat(timespec="seconds")})

    master = Path(config["master_source"])
    sources = [master] + [Path(item["path"]) for item in imports]

    if args.append_to_master:
        master_text = read_text(master)
        if new_text.strip() not in master_text:
            merged = new_text.strip() + "\n\n" + master_text.lstrip()
            master.write_text(merged, encoding="utf-8")
            sources = [master]
            imports = []

    new_config = build_index(sources, html_path=config.get("html_path") or None)
    write_json(IMPORTS_PATH, imports)
    print(f"更新完成：{new_config['chunk_count']} 個片段")


def cmd_ask(args):
    results = retrieve(args.question, top_k=args.top_k)
    answer = call_openai(args.question, results, use_web=args.web, model=args.model) if (args.web or args.llm) else None
    if answer:
        print(answer)
    else:
        print(local_answer(args.question, results))


def cmd_chat(args):
    print("Weekly Agent chat。輸入 exit / quit 離開。")
    while True:
        try:
            question = input("\n你：").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not question:
            continue
        if question.lower() in ("exit", "quit", "q"):
            return
        results = retrieve(question, top_k=args.top_k)
        answer = call_openai(question, results, use_web=args.web, model=args.model) if (args.web or args.llm) else None
        print("\nAI：")
        print(answer if answer else local_answer(question, results))


def api_answer(question, top_k=8, use_llm=False, use_web=False, model="gpt-4.1-mini"):
    top_k = choose_top_k(question, top_k)
    results = retrieve(question, top_k=top_k)
    answer = None
    warning = ""
    if use_llm or use_web:
        try:
            answer = call_openai(question, results, use_web=use_web, model=model)
        except Exception as exc:
            warning = f"OpenAI/Web Search 未啟用成功：{exc} 已先顯示週報本機檢索結果。"
    return {
        "answer": answer if answer else local_answer(question, results),
        "mode": ("openai-web" if use_web else "openai") if answer else "local",
        "top_k": top_k,
        "warning": warning,
        "sources": [
            {
                "week": item["week"],
                "raw_week": item["raw_week"],
                "date": item.get("date") or "",
                "line": item["start_line"],
                "score": item["score"],
                "source": Path(item["source_path"]).name,
                "html_anchor": item.get("html_anchor") or "",
                "snippet": make_snippet(item["text"], question, width=360),
            }
            for item in results[:top_k]
        ],
    }


class WeeklyAgentHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("[web] " + fmt % args + "\n")

    def send_json(self, status, payload):
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/status":
            config = read_json(CONFIG_PATH, {})
            imports = read_json(IMPORTS_PATH, [])
            api_key = get_openai_key()
            self.send_json(
                200,
                {
                    "ok": True,
                    "config": config,
                    "imports": imports,
                    "has_openai_key": bool(api_key),
                    "openai_key_masked": mask_secret(api_key),
                },
            )
            return
        if parsed.path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path not in ("/api/ask", "/api/openai-key"):
            self.send_json(404, {"ok": False, "error": "Not found"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(size).decode("utf-8")
            payload = json.loads(body) if body else {}
            if parsed.path == "/api/openai-key":
                set_openai_key(payload.get("api_key") or "")
                self.send_json(200, {"ok": True, "has_openai_key": True})
                return
            question = (payload.get("question") or "").strip()
            if not question:
                self.send_json(400, {"ok": False, "error": "請先輸入問題。"})
                return
            data = api_answer(
                question,
                top_k=int(payload.get("top_k") or 8),
                use_llm=bool(payload.get("llm")),
                use_web=bool(payload.get("web")),
                model=payload.get("model") or os.environ.get("WEEKLY_AGENT_MODEL", "gpt-4.1-mini"),
            )
            self.send_json(200, {"ok": True, **data})
        except Exception as exc:
            self.send_json(500, {"ok": False, "error": str(exc)})


def cmd_web(args):
    if not (WEB_DIR / "index.html").exists():
        raise SystemExit("找不到 web/index.html，請確認 Web UI 檔案存在。")
    load_index()
    server = ThreadingHTTPServer((args.host, args.port), WeeklyAgentHandler)
    url = f"http://{args.host}:{args.port}"
    print(f"Weekly Agent Web UI 已啟動：{url}")
    print("按 Ctrl+C 停止。")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止 Web UI。")
    finally:
        server.server_close()


def cmd_status(args):
    config = read_json(CONFIG_PATH, {})
    imports = read_json(IMPORTS_PATH, [])
    if not config:
        print("尚未建立索引。")
        return
    print(json.dumps({"config": config, "imports": imports}, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Weekly Report AI Agent")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="建立或重建索引")
    p_init.add_argument("--source", required=True, help="多年週報 Markdown 主檔")
    p_init.add_argument("--html", help="對應 HTML 檔，可選")
    p_init.set_defaults(func=cmd_init)

    p_update = sub.add_parser("update", help="匯入新一週週報並重建索引")
    p_update.add_argument("--new-week", required=True, help="新週報 Markdown")
    p_update.add_argument("--append-to-master", action="store_true", help="把新週報置頂合併回 master_source")
    p_update.set_defaults(func=cmd_update)

    p_ask = sub.add_parser("ask", help="詢問週報")
    p_ask.add_argument("question")
    p_ask.add_argument("--top-k", type=int, default=8)
    p_ask.add_argument("--llm", action="store_true", help="使用 OpenAI 整理回答，但不啟用 Web Search")
    p_ask.add_argument("--web", action="store_true", help="使用 OpenAI Web Search 補充回答")
    p_ask.add_argument("--model", default=os.environ.get("WEEKLY_AGENT_MODEL", "gpt-4.1-mini"))
    p_ask.set_defaults(func=cmd_ask)

    p_chat = sub.add_parser("chat", help="互動式詢問週報")
    p_chat.add_argument("--top-k", type=int, default=8)
    p_chat.add_argument("--llm", action="store_true", help="使用 OpenAI 整理回答，但不啟用 Web Search")
    p_chat.add_argument("--web", action="store_true", help="使用 OpenAI Web Search 補充回答")
    p_chat.add_argument("--model", default=os.environ.get("WEEKLY_AGENT_MODEL", "gpt-4.1-mini"))
    p_chat.set_defaults(func=cmd_chat)

    p_web = sub.add_parser("web", help="啟動本機 Web 對話 UI")
    p_web.add_argument("--host", default="127.0.0.1")
    p_web.add_argument("--port", type=int, default=8765)
    p_web.set_defaults(func=cmd_web)

    p_status = sub.add_parser("status", help="查看目前索引設定")
    p_status.set_defaults(func=cmd_status)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
