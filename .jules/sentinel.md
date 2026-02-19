## 2026-02-15 - Stored XSS in HTML Report Generation
**Vulnerability:** User-controlled inputs (filenames, repository URLs, branch names) were directly interpolated into HTML report strings without sanitization. This allowed attackers to execute arbitrary JavaScript in the context of the report viewer by crafting malicious filenames or repository metadata.
**Learning:** Even in CLI tools that generate static reports, output encoding is critical. Filenames and git metadata should be treated as untrusted input when rendered in HTML.
**Prevention:** Always use `html.escape()` (or a templating engine with auto-escaping) when inserting variable data into HTML contexts. Manually replacing specific characters like `<` and `>` is often insufficient and error-prone.

## 2026-02-15 - Symlink Traversal via Repo Scanning
**Vulnerability:** The scanner followed symlinks inside repositories that pointed to sensitive files outside the repo root (e.g., `/etc/passwd`), leading to arbitrary file read and potential information disclosure in reports.
**Learning:** `pathlib.Path.rglob()` yields symlinks pointing outside the directory by default. When scanning untrusted repositories, file paths must be validated to ensure they resolve within the repository boundary.
**Prevention:** Use `file_path.resolve().relative_to(repo_root)` to enforce that all scanned files are contained within the intended directory.
