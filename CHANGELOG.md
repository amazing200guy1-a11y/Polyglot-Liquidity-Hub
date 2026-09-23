# Changelog

## [1.1.0] — 2026-09-23
### Added
- Shared `conftest.py` for Python microservice test fixtures.
- `pytest.ini` with `asyncio_mode = auto`.
- MIT license applied across all components.
- `.gitignore` for Python, Java, Node, and Go build artifacts.

## [1.0.0] — 2026-09-20
### Added
- Go goroutine-based channel multiplexer (`routing-go/go_router.go`).
- Python async stream coordinator (`microservice-python/stream_bridge.py`).
- Java 17 FIX adapter node (`network-java/FixAdapterNode.java`).
- TypeScript / Next.js operator cockpit (`frontend-nextjs/dashboard.tsx`).
- CSS3 global styles with CSS variables (`frontend-nextjs/global-styles.css`).
- Multi-language CI via GitHub Actions.