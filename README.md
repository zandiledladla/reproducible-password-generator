# Reproducible Password Generator

COS738 cybersecurity assignment with a Python/Tkinter desktop application and a JavaScript browser implementation. The same memorable input and output length produce the same password in both versions.

## Features

- PBKDF2-HMAC-SHA256 derivation with 200,000 iterations.
- Configurable output length from 8 to 128 characters, including uppercase, lowercase, digits and symbols.
- Input validation, masked fields, copy, clear and optional plaintext export.
- Background derivation keeps the desktop interface responsive.
- Automated Python tests and Python/JavaScript consistency checks.

## Run

Requires Python 3 with Tkinter for the desktop interface. No third-party Python packages are needed.

```bash
python password_gui.py
```

For the browser interface, run from the repository folder:

```bash
python -m http.server 8000
```

Open http://localhost:8000 in a modern browser. Web Crypto requires localhost or HTTPS.

## Tests

```bash
python -m unittest discover -s tests -v
node tests/test_translation.js
```

The cross-language tests require Node.js and Python. On systems where Python has another command name, set the `PYTHON` environment variable accordingly.

## Context and limitations

This project is an AI-assisted re-engineering of a supplied educational example for COS738, including a JavaScript translation. It demonstrates password derivation, interface design, validation and testing; it is not a production password manager. The public fixed salt does not protect weak memorable inputs from guessing. There is no site-specific input, so reusing an input and length reproduces the same password across uses. Inputs are case- and space-sensitive, with no Unicode normalisation. Exported files are unencrypted, and clipboard history may retain copied output. Use demonstration inputs only.
