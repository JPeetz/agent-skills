# Security Patterns Reference

OWASP-inspired patterns and anti-patterns to detect during code review.
This is a practical reference — use it to identify issues, not as an
exhaustive security audit guide.

---

## Injection Vulnerabilities

### SQL Injection

**Anti-pattern (flag as BLOCKER):**

```python
# Python — string formatting into SQL
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
cursor.execute("SELECT * FROM users WHERE name = '%s'" % name)
```

```javascript
// JavaScript — string concatenation
db.query("SELECT * FROM users WHERE id = " + userId);
db.query(`SELECT * FROM users WHERE email = '${email}'`);
```

```go
// Go — fmt.Sprintf into query
db.Query(fmt.Sprintf("SELECT * FROM users WHERE id = %s", userID))
```

```java
// Java — string concatenation
stmt.executeQuery("SELECT * FROM users WHERE name = '" + name + "'");
```

**Correct pattern:**

```python
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

```javascript
db.query("SELECT * FROM users WHERE id = $1", [userId]);
```

```go
db.Query("SELECT * FROM users WHERE id = $1", userID)
```

```java
PreparedStatement stmt = conn.prepareStatement("SELECT * FROM users WHERE name = ?");
stmt.setString(1, name);
```

**What to flag**: Any database query built with string formatting, concatenation,
or template literals using user-controlled data. Also flag ORM methods that
allow raw SQL with untrusted input — e.g. `Model.raw()`, `sequelize.query()`
without parameter binding.

### OS Command Injection

**Anti-pattern (BLOCKER):**

```python
os.system(f"convert {user_file} output.pdf")
subprocess.run(f"pdf2txt {user_input}", shell=True)
```

```javascript
exec(`convert ${userFile} output.pdf`);
execSync(userInput);
```

```go
exec.Command("sh", "-c", "convert "+userInput+" output.pdf")
```

**Correct pattern:**

```python
subprocess.run(["convert", user_file, "output.pdf"], shell=False)
```

```go
exec.Command("convert", userInput, "output.pdf")
```

**What to flag**: `shell=True`, `exec()`, `os.system()`, `popen()` with string
commands containing user input. Command arguments should always be passed as
arrays/lists.

### Cross-Site Scripting (XSS)

**Anti-pattern (BLOCKER):**

```javascript
// Setting innerHTML with user data
element.innerHTML = userComment;
document.write(userInput);

// React dangerouslySetInnerHTML
<div dangerouslySetInnerHTML={{__html: userBio}} />

// jQuery
$('#content').html(userData);
```

```python
# Template without auto-escaping
from jinja2 import Markup
return Markup(f"<div>{user_input}</div>")
```

**Correct pattern:**

```javascript
element.textContent = userComment;

// React — JSX escapes by default
<div>{userBio}</div>

// If HTML is needed, use DOMPurify
import DOMPurify from 'dompurify';
element.innerHTML = DOMPurify.sanitize(userHtml);
```

**What to flag**: Any place user-controlled data is inserted into HTML/DOM
without sanitization or proper escaping. Check `innerHTML`, `outerHTML`,
`document.write()`, `insertAdjacentHTML()`, and template engines without
auto-escaping.

---

## Authentication & Authorization

### Broken Authentication

**Anti-pattern (BLOCKER):**

```python
# Timing-vulnerable comparison
if input_password == stored_password:
    login()

# Using MD5/SHA-1 for passwords
hashlib.md5(password.encode()).hexdigest()

# Weak random for tokens
import random
token = ''.join(random.choice(string.ascii_letters) for _ in range(32))
```

```javascript
// Weak random
const token = Math.random().toString(36).substring(2);

// Timing-vulnerable comparison
if (inputToken === storedToken) { /* early exit on first mismatch */ }
```

**Correct pattern:**

```python
import secrets
import hmac
token = secrets.token_urlsafe(32)
# Constant-time comparison
hmac.compare_digest(input_token, stored_token)
```

```javascript
const crypto = require('crypto');
const token = crypto.randomBytes(32).toString('hex');
// Constant-time comparison
crypto.timingSafeEqual(Buffer.from(input), Buffer.from(stored));
```

### Missing Authorization Checks

**Anti-pattern (BLOCKER):**

```python
# No ownership check
@app.route('/api/users/<user_id>/settings')
def get_settings(user_id):
    return User.query.get(user_id).settings

# No role check
@app.route('/admin/delete-user/<user_id>')
@login_required  # Authenticated but not authorized!
def delete_user(user_id):
    User.query.get(user_id).delete()
```

**What to flag**: Any endpoint or function that performs a sensitive action
without verifying the caller has permission. Check every new route, controller,
resolver, or handler. Look for decorator-only auth without role verification.

### JWT Validation Issues

**Anti-pattern (BLOCKER):**

```python
# Not verifying signature
payload = jwt.decode(token, options={"verify_signature": False})

# Not checking expiry
payload = jwt.decode(token, key, algorithms=["HS256"])

# Using 'none' algorithm allowed
jwt.decode(token, verify=False)
```

**What to flag**: JWT decoding without signature verification, without expiry
check, without audience/issuer validation, or with `alg: "none"` permitted.

---

## Sensitive Data Exposure

### Hardcoded Secrets

**Anti-pattern (BLOCKER):**

```python
API_KEY = "sk_live_4a8b9c2d3e4f5g6h7i8j"
DATABASE_URL = "postgres://user:password123@prod-db:5432/mydb"
AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
```

```javascript
const STRIPE_KEY = "sk_live_abc123xyz";
const config = { password: "admin123" };
```

```yaml
# docker-compose.yml
environment:
  - DATABASE_PASSWORD=super_secret_prod_password
```

**Correct pattern:**

```python
import os
API_KEY = os.environ.get("API_KEY")
```

```javascript
const STRIPE_KEY = process.env.STRIPE_SECRET_KEY;
```

**What to flag**: Any string literal that looks like a secret. Patterns to
search for: `sk_live_`, `sk-`, `pk_live_`, `-----BEGIN`, `api_key`, `secret`,
`password`, `token`, `credential` assigned to literal strings.

### Sensitive Data in Logs

**Anti-pattern (BLOCKER):**

```python
logger.info(f"User {email} logged in with password {password}")
logger.debug(f"Request headers: {request.headers}")  # Contains Authorization
```

```javascript
console.log("User data:", { email, ssn, creditCard });
```

**What to flag**: Log statements that include passwords, tokens, PII, session
IDs, or full request/response bodies.

---

## CSRF & SSRF

### Cross-Site Request Forgery

**Anti-pattern (BLOCKER):**

```python
# State-changing endpoint without CSRF protection
@app.route('/transfer', methods=['POST'])
def transfer():
    amount = request.form['amount']
    to_account = request.form['to']
    # No CSRF token check
    perform_transfer(amount, to_account)
```

**What to flag**: POST/PUT/DELETE endpoints that change state without CSRF
tokens. Especially dangerous in cookie-based auth setups.

### Server-Side Request Forgery (SSRF)

**Anti-pattern (BLOCKER):**

```python
@app.route('/fetch')
def fetch_url():
    url = request.args.get('url')
    return requests.get(url).text  # User controls the URL!
```

```javascript
app.get('/proxy', async (req, res) => {
    const url = req.query.url;
    const response = await fetch(url);  // SSRF!
    res.send(await response.text());
});
```

**What to flag**: Any endpoint that fetches a URL provided by the user without
validating it against an allowlist. Especially dangerous in cloud environments
where internal metadata endpoints (169.254.169.254) are accessible.

---

## Insecure Deserialization

**Anti-pattern (BLOCKER):**

```python
import pickle
data = pickle.loads(request.data)  # Remote code execution!

import yaml
data = yaml.load(request.data)  # Unsafe! Use yaml.safe_load()

import marshal
code = marshal.loads(user_input)  # Code execution!
```

```javascript
// Node.js — eval on deserialized data
const obj = eval(`(${userInput})`);
```

```php
$data = unserialize($_GET['data']);  // Object injection!
```

**What to flag**: `pickle.load[s]()`, `yaml.load()` (not `safe_load`),
`marshal.load[s]()`, `eval()` on serialized data, PHP `unserialize()`,
Java `ObjectInputStream` on untrusted data.

---

## Cryptographic Weaknesses

### Weak Randomness

**Anti-pattern (BLOCKER):**

```python
import random
token = random.randint(100000, 999999)  # Not crypto-secure
random.choice(string.ascii_letters)     # Predictable
```

```javascript
Math.random()  // Not crypto-secure
Math.floor(Math.random() * 1000000)
```

**Correct pattern:**

```python
import secrets
token = secrets.randbelow(1000000)
```

```javascript
const crypto = require('crypto');
crypto.randomInt(1000000);
```

### Weak Hashing for Passwords

**Anti-pattern (BLOCKER):**

```python
hashlib.md5(password.encode()).hexdigest()
hashlib.sha1(password.encode()).hexdigest()
hashlib.sha256(password.encode()).hexdigest()  # Too fast, no salt
```

**Correct pattern:**

```python
import bcrypt
hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# Or passlib
from passlib.hash import argon2
hash = argon2.hash(password)
```

### Weak Encryption

**Anti-pattern (BLOCKER):**

```python
from Crypto.Cipher import DES  # Broken
from Crypto.Cipher import ARC4  # RC4 — broken
# ECB mode — deterministic, reveals patterns
cipher = AES.new(key, AES.MODE_ECB)
# Static IV
iv = b'1234567890123456'  # Same IV every time!
```

---

## Path Traversal & File Operations

**Anti-pattern (BLOCKER):**

```python
# Path traversal
@app.route('/download')
def download():
    filename = request.args.get('file')
    return send_file(f'/var/data/{filename}')  # ../../etc/passwd

# Zip slip
import zipfile
with zipfile.ZipFile(uploaded_zip) as z:
    z.extractall('/var/data')  # File may contain ../../../etc/cron.d/malicious
```

**Correct pattern:**

```python
import os
base = '/var/data'
filename = os.path.basename(request.args.get('file'))  # Strip path
full_path = os.path.join(base, filename)
# Verify result is still within base
if not os.path.realpath(full_path).startswith(os.path.realpath(base)):
    raise SecurityError("Path traversal detected")
```

---

## Race Conditions

**Anti-pattern (MAJOR):**

```python
# TOCTOU — check then use
if os.path.exists(filepath):
    with open(filepath) as f:  # File may have changed between check and open
        process(f.read())

# Double-spend risk
balance = get_balance(user_id)
if balance >= amount:
    deduct(user_id, amount)  # What if two requests pass the check simultaneously?
```

**Correct pattern:**

```python
# Atomic operation
UPDATE accounts SET balance = balance - $amount
WHERE user_id = $user_id AND balance >= $amount
# Check affected rows to confirm success
```

**What to flag**: Check-then-act patterns on shared state, especially in
financial or auth contexts. Look for SELECT → UPDATE patterns without
transactions or row-level locking.

---

## Information Disclosure

**Anti-pattern (MAJOR/MINOR):**

```python
# Verbose error messages
except Exception as e:
    return jsonify({"error": str(e)}), 500  # Stack trace to client

# Debug endpoint in production
@app.route('/debug/config')
def debug_config():
    return jsonify(app.config)  # Exposes all config including secrets
```

```javascript
// Stack trace in response
app.use((err, req, res, next) => {
    res.status(500).json({ error: err.stack });  // Leaks internals!
});
```

---

## Dependency & Supply Chain

**What to flag during dependency reviews:**

- New dependencies with no GitHub stars, no recent commits, single maintainer
- Name confusion: `dateutil` vs `python-dateutil`, `lodash` vs `lodas`
- Dependencies pulling in large transitive dependency trees
- Pinning to git URLs or local paths
- Version ranges that auto-upgrade to potentially compromised versions (`^1.0.0`, `~2.3`, `*`)
- Dependencies with known CVEs (check against osv.dev / GitHub Advisory DB)

---

## Quick Scan Checklist

When reviewing a diff, scan for these patterns quickly:

1. **Secret strings**: `key`, `secret`, `password`, `token`, `auth`, `credential` with literal values
2. **String formatting into queries**: `f"SELECT`, `"SELECT` + concatenation, `.format(` into SQL
3. **Dangerous functions**: `eval`, `exec`, `system`, `popen`, `shell=True`, `pickle.load`, `yaml.load`, `innerHTML`, `dangerouslySetInnerHTML`
4. **Missing authorization**: New routes/endpoints without `@require_auth` or equivalent
5. **Weak random**: `Math.random`, `random.randint`, `random.choice`
6. **Weak hashing**: `md5`, `sha1`, `sha256` used on passwords
7. **Path construction**: String concatenation for file paths with user input
8. **Error info leak**: Stack traces or internal paths in HTTP responses
9. **Version ranges**: New deps with `^`, `~`, `>=` instead of pinned versions
10. **Sensitive data in logs**: `console.log` / `logger.info` with tokens, passwords, or PII