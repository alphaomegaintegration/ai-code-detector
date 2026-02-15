## 2026-02-15 - Stored XSS in HTML Report Generation
**Vulnerability:** User-controlled inputs (filenames, repository URLs, branch names) were directly interpolated into HTML report strings without sanitization. This allowed attackers to execute arbitrary JavaScript in the context of the report viewer by crafting malicious filenames or repository metadata.
**Learning:** Even in CLI tools that generate static reports, output encoding is critical. Filenames and git metadata should be treated as untrusted input when rendered in HTML.
**Prevention:** Always use `html.escape()` (or a templating engine with auto-escaping) when inserting variable data into HTML contexts. Manually replacing specific characters like `<` and `>` is often insufficient and error-prone.
