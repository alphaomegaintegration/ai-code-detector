## 2024-05-22 - Argument Injection via Git Branch Name
**Vulnerability:** Unvalidated user input passed to `git clone --branch <INPUT>` allows argument injection if input starts with `-`.
**Learning:** Git commands can interpret arguments starting with `-` as options even when preceded by flags like `--branch` (depending on context/version/parser).
**Prevention:** Always validate inputs passed to shell commands. For git refs, ensure they don't start with `-` and only contain safe characters (alphanumeric, `/`, `_`, `.`, `-`).
