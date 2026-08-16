# Reading a HAR entry to an API request

A HAR file is JSON. Each entry wraps a `request` and its `response`. To derive a
clean, replayable API call from the entry for an action:

## Locate the entry
Filter entries to the XHR/fetch resource type performing the action you recorded.
```json
{
  "log": {
    "entries": [
      {
        "request": { "method": "POST", "url": "https://...", "headers": [...], "postData": {...} },
        "response": { "status": 200, "content": {...} }
      }
    ]
  }
}
```

## Extract these fields
- **method** → `request.method`
- **url** → `request.url` (full, with query string)
- **headers** → `request.headers` — keep only `content-type`, `accept`,
  `origin`, `referer`. Drop `cookie`, `authorization`, `content-length`, and
  `sec-*` for the clean rebuild.
- **body** → `request.postData.text` (URL-encoded form, JSON, or multipart)
- **dynamic tokens** → scan url + headers + body for session/csrf/nonce/signature
  values that change per request. These get a runtime placeholder, not literal
  replay.

## Rebuild minimal
```bash
curl -i -X POST 'https://...' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  --data '{"..."}'
```
Auth is added separately from your credential source by label — never paste the
captured `Authorization`/cookie.

## Verify
Compare the standalone call's status + response JSON shape against the HAR's
`response`. Non-2xx or mismatched shape usually means an expiring token or missing
auth — inspect the HAR for the rotating value, refresh, retry.