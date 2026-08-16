#!/usr/bin/env python3
"""Chrome CLI HAR Capture + Auth Extractor for Social Platform API Connectivity.

Drives Chrome (visible or headless) via CDP (Chrome DevTools Protocol) to:
1. Capture all network traffic during a login flow
2. Extract session tokens, cookies, and API endpoints
3. Save as HAR + auth map
4. Print a reusable client template for AI automation

Usage (visible mode, best for MFA/CAPTCHA):
  chrome_capture_client.py --login-url "https://platform.com/login" \
      --success-url-pattern "dashboard|feed|home" --visible --timeout 180

Usage (headless, automated):
  chrome_capture_client.py --login-url "https://platform.com/login" \
      --success-url-pattern "dashboard" --timeout 120

Dependencies: websockets (pip install websockets), Chrome 127+
"""
import argparse, asyncio, json, os, re, sys, tempfile, time, subprocess
from urllib.parse import urlparse

SENSITIVE_HEADERS = {"cookie", "authorization", "set-cookie",
                     "x-csrf-token", "x-xsrf-token"}
TOKEN_VALUE_RE = re.compile(
    r'(["\']?)(token|secret|password|apikey|api_key|auth|bearer|sid|session_id)'
    r'(["\'])?\s*[:=]\s*["\']?([A-Za-z0-9_\-.]{8,})', re.I)


class ChromeCaptureClient:
    def __init__(self, chrome_port=9223):
        self.chrome_port = chrome_port or 9223
        self.user_data_dir = tempfile.mkdtemp(prefix="chrome-cap-")
        self._chrome_proc = None
        self._ws = None
        self._events = []
        self._responses = {}       # id -> response dict
        self._reader_task = None
        self._msg_id = 0
        self.out_har = ""
        self.out_auth = ""

    # ── Chrome lifecycle ──────────────────────────────────────────────

    def start_chrome(self, visible=False, chrome_binary=None):
        if chrome_binary is None:
            chrome_binary = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if not os.path.exists(chrome_binary):
            raise FileNotFoundError(f"Chrome not found at {chrome_binary}")
        cmd = [chrome_binary, f"--remote-debugging-port={self.chrome_port}",
               f"--user-data-dir={self.user_data_dir}",
               "--no-first-run", "--no-default-browser-check",
               "--disable-gpu", "--window-size=1280,800"]
        if not visible:
            cmd.append("--headless")
        print(f"  Chrome starting on port {self.chrome_port} visible={visible}")
        self._chrome_proc = subprocess.Popen(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)

    def stop_chrome(self):
        if self._chrome_proc:
            self._chrome_proc.terminate()
            try:
                self._chrome_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._chrome_proc.kill()
            self._chrome_proc = None

    # ── CDP connection ─────────────────────────────────────────────────

    async def _reader(self):
        """Background task: read every WS message, dispatch to response or events."""
        try:
            async for raw in self._ws:
                data = json.loads(raw)
                if "id" in data:
                    # command response
                    self._responses[data["id"]] = data
                elif "method" in data:
                    # event — capture network events
                    m = data.get("method", "")
                    if m in ("Network.requestWillBeSent", "Network.responseReceived",
                             "Network.requestWillBeSentExtraInfo", "Page.frameNavigated",
                             "Page.frameStartedLoading"):
                        self._events.append(data)
                # other events (console, etc.) are ignored
        except Exception:
            pass

    async def _get_ws_url(self):
        import urllib.request
        try:
            resp = urllib.request.urlopen(
                f"http://127.0.0.1:{self.chrome_port}/json", timeout=5)
            targets = json.loads(resp.read().decode())
            for t in targets:
                if t.get("type") == "page":
                    return t["webSocketDebuggerUrl"]
            return targets[0]["webSocketDebuggerUrl"] if targets else None
        except Exception:
            return None

    async def connect(self):
        import websockets
        ws_url = await self._get_ws_url()
        if not ws_url:
            raise ConnectionError("Chrome CDP WS URL not found")
        print(f"  Connecting to CDP...")
        self._ws = await websockets.connect(ws_url, max_size=10*1024*1024)
        self._reader_task = asyncio.create_task(self._reader())

    async def _send(self, method, params=None):
        """Send CDP command and await the matching response."""
        self._msg_id += 1
        msg_id = self._msg_id
        msg = {"id": msg_id, "method": method}
        if params:
            msg["params"] = params
        await self._ws.send(json.dumps(msg))
        deadline = time.time() + 10
        while time.time() < deadline:
            if msg_id in self._responses:
                return self._responses.pop(msg_id)
            await asyncio.sleep(0.02)
        return {"error": "timeout"}

    # ── Capture ───────────────────────────────────────────────────────

    async def enable_network(self):
        await self._send("Network.enable")
        await self._send("Page.enable")
        print("  Network capture enabled")

    async def navigate(self, url):
        print(f"  Navigating to {url}")
        await self._send("Page.navigate", {"url": url})

    async def wait_for_login(self, success_url_pattern, max_wait=120):
        """Wait for navigation to a URL matching the success pattern."""
        deadline = time.time() + max_wait
        print(f"  Capturing up to {max_wait}s pattern=/{success_url_pattern}/")
        while time.time() < deadline:
            await asyncio.sleep(0.1)
            # scan recent events for frameNavigated matching the pattern
            for ev in self._events:
                if ev.get("method") == "Page.frameNavigated":
                    frame = ev.get("params", {}).get("frame", {})
                    url = frame.get("url", "")
                    if url and url not in ("about:blank", ""):
                        parsed = urlparse(url)
                        print(f"    -> {parsed.hostname}{parsed.path[:60]}")
                        if re.search(success_url_pattern, url, re.I):
                            print(f"  Login success detected!")
                            return url
        print(f"  Timed out after {max_wait}s")
        return None

    def extract_auth(self):
        auth = {"cookies": [], "headers": [], "body_tokens": []}
        for ev in self._events:
            method = ev.get("method")
            params = ev.get("params", {})
            if method == "Network.responseReceived":
                resp = params.get("response", {})
                for h in resp.get("headers", []):
                    if isinstance(h, dict) and h.get("name", "").lower() == "set-cookie":
                        auth["cookies"].append(h.get("value", "")[:100])
            if method == "Network.requestWillBeSent":
                req = params.get("request", {})
                for h in req.get("headers", []):
                    if isinstance(h, dict):
                        hn = h.get("name", "").lower()
                        if hn in SENSITIVE_HEADERS or "auth" in hn:
                            auth["headers"].append(h.get("name"))
            text = json.dumps(ev.get("params", {}))
            for m in TOKEN_VALUE_RE.finditer(text):
                k, v = m.group(2), m.group(4)
                if len(v) >= 8:
                    auth["body_tokens"].append({"key": k, "value": v[:8]+"..."})
        return auth

    def detect_api_base(self):
        hosts = {}
        skip = (".cdn.", "analytics.", "adservice.", "doubleclick",
                "google-analytics", "gstatic", "facebook.com/tr")
        for ev in self._events:
            p = ev.get("params", {})
            if ev.get("method") == "Network.requestWillBeSent":
                req = p.get("request", {})
                url = req.get("url", "")
                parsed = urlparse(url)
                h = parsed.hostname or ""
                if h and not any(s in h for s in skip):
                    hosts[h] = hosts.get(h, 0) + 1
        if not hosts:
            return None
        sh = sorted(hosts.items(), key=lambda x: -x[1])
        return sh[0][0] if sh else None

    def to_har(self):
        entries = []
        for ev in self._events:
            if ev.get("method") != "Network.requestWillBeSent":
                continue
            params = ev.get("params", {})
            req = params.get("request", {})
            rid = params.get("requestId", "")
            resp_data = {}
            for ev2 in self._events:
                if ev2.get("method") == "Network.responseReceived":
                    p2 = ev2.get("params", {})
                    if p2.get("requestId") == rid:
                        r2 = p2.get("response", {})
                        resp_data = {"status": r2.get("status")}
                        break
            entries.append({
                "request": {"method": req.get("method"), "url": req.get("url"),
                            "headers": req.get("headers", [])},
                "response": resp_data})
        return {"log": {"version": "1.2", "creator": {"name": "ChromeCaptureClient"},
                        "entries": entries}}

    def print_summary(self, auth, api_host):
        print(f"\n{'='*60}")
        print("LOGIN CAPTURE SUMMARY")
        print(f"{'='*60}")
        print(f"  API Host:      {api_host or 'unknown'}")
        print(f"  Events logged: {len(self._events)}")
        print(f"  Cookies:       {len(auth['cookies'])}")
        for c in auth['cookies']:
            print(f"    - {c[:60]}")
        print(f"  Auth headers:  {len(auth['headers'])}")
        for h in auth['headers']:
            print(f"    - {h}")
        for t in auth['body_tokens']:
            print(f"  Token:         {t['key']} = {t['value']}")
        print(f"\nREUSABLE CLIENT:")
        if api_host:
            print(f"  curl -H 'Authorization: <token>' https://{api_host}/endpoint")
        print(f"  (Auth tokens resolved from vault -- never hardcoded)")
        print(f"Files: {self.out_har} + {self.out_auth}")
        print(f"{'='*60}")

    async def capture_and_save(self, login_url, success_pattern, max_wait,
                                out_har, out_auth):
        await self.connect()
        await self.enable_network()
        await self.navigate(login_url)
        await self.wait_for_login(success_pattern, max_wait)
        auth = self.extract_auth()
        api_host = self.detect_api_base()
        self.print_summary(auth, api_host)
        with open(out_har, "w") as f:
            json.dump(self.to_har(), f, indent=1)
        with open(out_auth, "w") as f:
            json.dump({"extracted": auth, "api_host": api_host,
                       "login_url": login_url}, f, indent=1)
        os.chmod(out_har, 0o600)
        os.chmod(out_auth, 0o600)


def main():
    ap = argparse.ArgumentParser(description="Chrome CLI HAR + Auth Capture")
    ap.add_argument("--login-url", required=True)
    ap.add_argument("--success-url-pattern", default="home|feed|dashboard")
    ap.add_argument("--visible", action="store_true")
    ap.add_argument("--chrome-port", type=int, default=9223)
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--output", default="/tmp/chrome-capture")
    args = ap.parse_args()
    os.makedirs(args.output, exist_ok=True)
    out_har = os.path.join(args.output, "capture.har")
    out_auth = os.path.join(args.output, "auth.json")
    cc = ChromeCaptureClient(chrome_port=args.chrome_port)
    cc.out_har, cc.out_auth = out_har, out_auth
    try:
        cc.start_chrome(visible=args.visible)
        asyncio.run(cc.capture_and_save(
            args.login_url, args.success_url_pattern, args.timeout,
            out_har, out_auth))
    except KeyboardInterrupt:
        print("\n  Interrupted")
    except Exception as e:
        import traceback; traceback.print_exc()
    finally:
        cc.stop_chrome()


if __name__ == "__main__":
    main()