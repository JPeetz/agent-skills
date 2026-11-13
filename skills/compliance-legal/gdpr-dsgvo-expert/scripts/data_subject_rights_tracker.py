#!/usr/bin/env python3
"""Data subject rights request tracker (GDPR Art. 15-22).

Tracks requests against the Art. 12(3) one-month deadline and records the
two-month extension when it is invoked. State lives in a JSON file so the
tracker has no dependencies and the file itself is the accountability record.

Standard library only. Python 3.8+.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys

VERSION = "0.1.0"

RIGHTS = {
    "access": ("Art. 15", "Right of access"),
    "rectification": ("Art. 16", "Right to rectification"),
    "erasure": ("Art. 17", "Right to erasure ('right to be forgotten')"),
    "restriction": ("Art. 18", "Right to restriction of processing"),
    "portability": ("Art. 20", "Right to data portability"),
    "objection": ("Art. 21", "Right to object"),
    "automated": ("Art. 22", "Rights regarding automated decision-making"),
    "info": ("Art. 13-14", "Right to be informed"),
    "recipients": ("Art. 19", "Notification of recipients"),
}

STATUSES = ["open", "in_progress", "awaiting_subject", "completed", "refused", "partially_refused"]

DEFAULT_STORE = "dsr_requests.json"


# ---------------------------------------------------------------------------
# Date helpers (stdlib only -- no dateutil)
# ---------------------------------------------------------------------------

def parse_date(value):
    if isinstance(value, dt.date):
        return value
    try:
        return dt.date.fromisoformat(str(value))
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"invalid date '{value}' -- use YYYY-MM-DD"
        )


def add_months(d, months):
    """Add calendar months, clamping the day to the target month's length.

    2026-01-31 + 1 month -> 2026-02-28 (not March 3rd).
    """
    month_index = d.month - 1 + months
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    # clamp
    day = d.day
    while True:
        try:
            return dt.date(year, month, day)
        except ValueError:
            day -= 1


def deadline_for(received, extended=False):
    base = add_months(received, 1)
    if extended:
        return add_months(base, 2), base
    return base, None


def days_left(deadline, today=None):
    today = today or dt.date.today()
    return (deadline - today).days


# ---------------------------------------------------------------------------
# Store
# ---------------------------------------------------------------------------

def load_store(path):
    if not os.path.exists(path):
        return {"version": 1, "next_id": 1, "requests": []}
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    data.setdefault("version", 1)
    data.setdefault("next_id", 1)
    data.setdefault("requests", [])
    return data


def save_store(path, data):
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")
    os.replace(tmp, path)


def find(data, req_id):
    for req in data["requests"]:
        if req["id"].lower() == req_id.lower():
            return req
    return None


def decorate(req, today=None):
    """Attach computed deadline fields to a request (not persisted)."""
    received = parse_date(req["received"])
    extended = bool(req.get("extension", {}).get("applied"))
    deadline, original = deadline_for(received, extended)
    out = dict(req)
    out["deadline"] = deadline.isoformat()
    out["original_deadline"] = original.isoformat() if original else deadline.isoformat()
    out["days_left"] = days_left(deadline, today)
    terminal = req.get("status") in ("completed", "refused", "partially_refused")
    out["overdue"] = (out["days_left"] < 0) and not terminal
    if terminal and req.get("closed"):
        out["days_used"] = (parse_date(req["closed"]) - received).days
    return out


def summarize(requests, today=None):
    today = today or dt.date.today()
    dec = [decorate(r, today) for r in requests]
    open_reqs = [r for r in dec if r["status"] not in ("completed", "refused", "partially_refused")]
    overdue = [r for r in open_reqs if r["overdue"]]
    due_7 = [r for r in open_reqs if 0 <= r["days_left"] <= 7]
    closed = [r for r in dec if r.get("days_used") is not None]
    within = [r for r in closed if r["days_used"] <= 30]
    by_right = {}
    for r in dec:
        by_right[r["right"]] = by_right.get(r["right"], 0) + 1
    by_status = {}
    for r in dec:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
    return {
        "total": len(dec),
        "open": len(open_reqs),
        "overdue": overdue,
        "due_within_7_days": due_7,
        "by_right": by_right,
        "by_status": by_status,
        "closed_count": len(closed),
        "closed_within_deadline": len(within),
        "compliance_rate": (
            round(100.0 * len(within) / len(closed), 1) if closed else None
        ),
    }


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_add(args):
    data = load_store(args.store)
    received = parse_date(args.received) if args.received else dt.date.today()
    req = {
        "id": f"DSR-{data['next_id']:04d}",
        "subject": args.subject,
        "right": args.right,
        "received": received.isoformat(),
        "channel": args.channel,
        "status": "open",
        "identity_verified": False,
        "identity_method": None,
        "notes": args.notes or "",
        "created": dt.datetime.now().isoformat(timespec="seconds"),
        "closed": None,
        "outcome": None,
        "extension": {"applied": False, "reason": None, "notified": None},
    }
    data["next_id"] += 1
    data["requests"].append(req)
    save_store(args.store, data)
    dec = decorate(req)
    print(f"created {req['id']} ({RIGHTS[req['right']][1]})")
    print(f"  received: {dec['received']}   deadline: {dec['deadline']}   days left: {dec['days_left']}")
    print("  next: verify identity, then scope the search across all systems")
    return 0


def cmd_list(args):
    data = load_store(args.store)
    reqs = data["requests"]
    if args.status:
        wanted = set(args.status)
        reqs = [r for r in reqs if r["status"] in wanted]
    if args.right:
        reqs = [r for r in reqs if r["right"] == args.right]
    if not reqs:
        print("no matching requests")
        return 0
    rows = [decorate(r) for r in reqs]
    rows.sort(key=lambda r: r["deadline"])
    print(f"{'ID':<10} {'RIGHT':<13} {'STATUS':<16} {'RECEIVED':<11} {'DEADLINE':<11} {'DAYS':>5}  SUBJECT")
    for r in rows:
        flag = " OVERDUE" if r["overdue"] else ""
        print(
            f"{r['id']:<10} {r['right']:<13} {r['status']:<16} {r['received']:<11} "
            f"{r['deadline']:<11} {r['days_left']:>5}  {r['subject']}{flag}"
        )
    return 0


def cmd_due(args):
    data = load_store(args.store)
    rows = [decorate(r) for r in data["requests"]]
    open_rows = [r for r in rows if r["status"] not in ("completed", "refused", "partially_refused")]
    if args.overdue:
        open_rows = [r for r in open_rows if r["overdue"]]
    else:
        open_rows = [r for r in open_rows if r["days_left"] <= args.within]
    if not open_rows:
        print(f"nothing due within {args.within} day(s)")
        return 0
    open_rows.sort(key=lambda r: r["days_left"])
    for r in open_rows:
        state = f"OVERDUE by {abs(r['days_left'])}d" if r["overdue"] else f"{r['days_left']}d left"
        print(f"{r['id']}  {r['right']:<13} {r['deadline']}  {state:<16} {r['subject']}")
    return 0


def cmd_status(args):
    data = load_store(args.store)
    req = find(data, args.id)
    if not req:
        print(f"error: no request {args.id}", file=sys.stderr)
        return 2

    if args.verify_identity:
        req["identity_verified"] = True
        req["identity_method"] = args.verify_identity or "documented"
        print(f"{req['id']}: identity verified via {req['identity_method']}")

    if args.extend:
        if req.get("status") in ("completed", "refused", "partially_refused"):
            print("error: cannot extend a closed request", file=sys.stderr)
            return 2
        dec = decorate(req)
        if dec["days_left"] < 0:
            print(
                "warning: the original deadline has already passed -- an extension "
                "notified now is not a valid Art. 12(3) extension",
                file=sys.stderr,
            )
        req["extension"] = {
            "applied": True,
            "reason": args.reason or "complex or numerous request",
            "notified": args.notified or dt.date.today().isoformat(),
        }
        print(
            f"{req['id']}: extended by two months ({req['extension']['reason']}); "
            f"notice recorded {req['extension']['notified']}"
        )

    if args.set:
        req["status"] = args.set
        if args.set in ("completed", "refused", "partially_refused"):
            req["closed"] = (parse_date(args.closed) if args.closed else dt.date.today()).isoformat()
            req["outcome"] = args.outcome or req.get("outcome")
        print(f"{req['id']}: status = {req['status']}")

    if args.note:
        existing = req.get("notes") or ""
        req["notes"] = (existing + "\n" if existing else "") + args.note
        print(f"{req['id']}: note added")

    save_store(args.store, data)
    dec = decorate(req)
    print(f"  deadline {dec['deadline']}  days left {dec['days_left']}  status {dec['status']}")
    return 0


def cmd_response(args):
    data = load_store(args.store)
    req = find(data, args.id)
    if not req:
        print(f"error: no request {args.id}", file=sys.stderr)
        return 2
    dec = decorate(req)
    article, label = RIGHTS[req["right"]]
    L = []
    a = L.append
    a(f"Subject: Your {label.lower()} request {req['id']}")
    a("")
    a(f"Dear {req['subject']},")
    a("")
    a(
        f"We refer to your request received on {dec['received']}, made under {article} of the "
        "General Data Protection Regulation."
    )
    a("")
    if req["right"] == "access":
        a("We process the following categories of your personal data:")
        a("")
        a("- account and contact details you provided")
        a("- transaction records relating to your use of our service")
        a("- technical records generated when you use the service")
        a("")
        a("Purposes of processing, recipients, retention periods, and the source of the data")
        a("are set out in the enclosed extract of our record of processing activities.")
        a("")
        a("A copy of the personal data undergoing processing is attached in a commonly used")
        a("machine-readable format.")
    elif req["right"] == "erasure":
        a("We have erased the personal data covered by your request, except where a legal")
        a("obligation requires continued storage. Where retention is required, we have")
        a("restricted processing to that obligation alone (Art. 18).")
    elif req["right"] == "rectification":
        a("We have corrected the personal data you identified as inaccurate. Recipients to")
        a("whom the data was disclosed have been informed (Art. 19).")
    elif req["right"] == "portability":
        a("The data you provided, together with any data generated by your use of the")
        a("service, is attached in a structured, commonly used, machine-readable format.")
    elif req["right"] == "objection":
        a("We have stopped processing your personal data for the purpose you objected to.")
        a("Where the processing was based on direct marketing, the objection is absolute.")
    elif req["right"] == "restriction":
        a("Processing of your personal data is now restricted: we store it but do not")
        a("otherwise process it until the matter is resolved.")
    elif req["right"] == "automated":
        a("We have provided an explanation of the logic involved in the decision, the")
        a("significance and envisaged consequences, and the safeguards available to you.")
    else:
        a("We have actioned your request as described below.")
    a("")
    if req.get("extension", {}).get("applied"):
        a(
            "This request was extended by two months under Art. 12(3) because of its "
            f"complexity ({req['extension'].get('reason')}). Notice of the extension was "
            f"given on {req['extension'].get('notified')}."
        )
        a("")
    a("You may lodge a complaint with the competent supervisory authority, and you have")
    a("the right to a judicial remedy (Art. 77, Art. 79).")
    a("")
    a("Kind regards,")
    a("Data Protection Team")
    a("")
    a("---")
    a(f"Draft generated for {req['id']}. Review before sending: confirm scope, redact")
    a("third-party data, and check any refusal ground against Art. 12(5) / Art. 17(3).")
    print("\n".join(L))
    return 0


def cmd_report(args):
    data = load_store(args.store)
    today = parse_date(args.today) if args.today else dt.date.today()
    s = summarize(data["requests"], today)
    print(f"Data subject rights report  ({today.isoformat()})")
    print(f"Store: {os.path.abspath(args.store)}")
    print("")
    print(f"Total requests:        {s['total']}")
    print(f"Open:                  {s['open']}")
    print(f"Overdue:               {len(s['overdue'])}")
    print(f"Due within 7 days:     {len(s['due_within_7_days'])}")
    if s["closed_count"]:
        print(
            f"Closed:                {s['closed_count']}  "
            f"({s['closed_within_deadline']} within deadline, {s['compliance_rate']}%)"
        )
    else:
        print("Closed:                0")
    if s["by_right"]:
        print("\nBy right:")
        for right, count in sorted(s["by_right"].items(), key=lambda kv: -kv[1]):
            print(f"  {right:<14} {count}")
    if s["by_status"]:
        print("\nBy status:")
        for status, count in sorted(s["by_status"].items(), key=lambda kv: -kv[1]):
            print(f"  {status:<18} {count}")
    if s["overdue"]:
        print("\nOVERDUE (Art. 12(3) breach -- escalate to the DPO):")
        for r in s["overdue"]:
            print(f"  {r['id']}  {r['right']:<13} due {r['deadline']}  {abs(r['days_left'])}d late  {r['subject']}")
    if args.json:
        print("")
        print(json.dumps({k: v for k, v in s.items() if k not in ("overdue", "due_within_7_days")}, indent=2))
    return 1 if s["overdue"] and args.fail_on_overdue else 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(
        description="Track GDPR data subject requests against the Art. 12(3) deadline.",
    )
    p.add_argument("--store", default=DEFAULT_STORE, help=f"JSON store path (default: {DEFAULT_STORE})")
    p.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    sub = p.add_subparsers(dest="command", required=True)

    a = sub.add_parser("add", help="record a new request")
    a.add_argument("--subject", required=True, help="subject identifier (use a pseudonym, not the name)")
    a.add_argument("--right", required=True, choices=sorted(RIGHTS), help="right invoked")
    a.add_argument("--received", help="date received YYYY-MM-DD (default: today; the clock starts here)")
    a.add_argument("--channel", default="email", help="how the request arrived")
    a.add_argument("--notes", help="free-text note")
    a.set_defaults(func=cmd_add)

    l = sub.add_parser("list", help="list requests")
    l.add_argument("--status", action="append", choices=STATUSES, help="filter by status (repeatable)")
    l.add_argument("--right", choices=sorted(RIGHTS), help="filter by right")
    l.set_defaults(func=cmd_list)

    d = sub.add_parser("due", help="show requests approaching or past the deadline")
    d.add_argument("--within", type=int, default=7, help="days ahead to look (default: 7)")
    d.add_argument("--overdue", action="store_true", help="only already-overdue requests")
    d.set_defaults(func=cmd_due)

    s = sub.add_parser("status", help="update a request")
    s.add_argument("--id", required=True)
    s.add_argument("--set", choices=STATUSES, help="new status")
    s.add_argument("--closed", help="closing date YYYY-MM-DD (default: today)")
    s.add_argument("--outcome", help="outcome summary for the record")
    s.add_argument("--note", help="append a note")
    s.add_argument("--verify-identity", metavar="METHOD", nargs="?", const="documented",
                   help="mark identity verified, optionally recording the method")
    s.add_argument("--extend", action="store_true", help="apply the Art. 12(3) two-month extension")
    s.add_argument("--reason", help="extension reason (complex or numerous request)")
    s.add_argument("--notified", help="date the subject was notified of the extension YYYY-MM-DD")
    s.set_defaults(func=cmd_status)

    r = sub.add_parser("response", help="generate a response template")
    r.add_argument("--id", required=True)
    r.set_defaults(func=cmd_response)

    rep = sub.add_parser("report", help="compliance report")
    rep.add_argument("--today", help="evaluate as of this date YYYY-MM-DD (default: today)")
    rep.add_argument("--json", action="store_true", help="append a JSON summary")
    rep.add_argument("--fail-on-overdue", action="store_true", help="exit 1 if anything is overdue")
    rep.set_defaults(func=cmd_report)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except argparse.ArgumentTypeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
