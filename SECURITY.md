# Security Policy

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Email: cadence.linardi@gmail.com

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact

You will receive a response within 48 hours. Please allow reasonable time to patch before public disclosure.

## Automated Security

- **TruffleHog** scans every push and PR for accidentally committed secrets
- **Dependabot** opens PRs for dependency updates daily (auto-merged)

## GH_PAT Security Model

### Scope

The GH_PAT (GitHub Personal Access Token) requires:
- epo — full control of private repositories
- workflow — update GitHub Actions workflows
- dmin:repo_hook — manage repository hooks

### Blast Radius

The sync-repo-settings.yml workflow **propagates GH_PAT to every owned non-archived repository** as a repository secret. This means:

- If the PAT is compromised, an attacker has write access to ALL repositories
- The PAT is used with --admin flag in bot auto-merge workflows, bypassing all branch protection

### Mitigation

- PAT stored only in GitHub Encrypted Secrets (never in source code)
- TruffleHog scans every push and PR to prevent accidental PAT exposure
- PAT should be rotated quarterly (recommended)
- Consider using a fine-grained PAT with minimal scope when GitHub supports it for all required operations

### Auto-merge --admin Pattern

Bot PRs (Dependabot, Snyk, Sourcery, DeepSource, Copilot SWE) are merged with --admin to bypass branch protection. This is acceptable because:

1. These bots only modify dependency manifests and lockfiles
2. TruffleHog and CodeQL scan every commit regardless of merge method
3. The Build Check workflow validates the build before --admin merge is triggered
