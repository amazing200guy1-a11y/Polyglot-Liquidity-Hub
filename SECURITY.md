# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | Yes       |

## Reporting a Vulnerability

Contact: security@mehd.ai — Subject: `[SECURITY] Polyglot-Liquidity-Hub`

Do NOT open a public GitHub issue for security vulnerabilities.

## Component Notes

- **Go**: Router uses non-blocking channel sends — slow consumers are dropped, not stalled.
- **Java**: FIX adapter uses object pooling to prevent heap allocation under load.
- **Python**: All outbound HTTP calls use `httpx.AsyncClient` with explicit timeout bounds.
- **TypeScript**: No credentials handled in the frontend layer.