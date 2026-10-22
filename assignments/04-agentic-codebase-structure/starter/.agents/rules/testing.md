---
description: Scoped guidance for testing link-shortener endpoints
globs: ["test_*.py", "tests/**"]
---

# Scoped Test Guidance

1. **Public API First**: Test behavior through `TestClient(app)` rather than internal functions.
2. **Success & Failure Coverage**: Always test the happy path and at least one failure/edge condition.
3. **Isolation**: Tests must not depend on execution order or shared state between tests.
4. **Behavioral Focus**: Verify observable status codes, JSON response bodies, and redirect headers.
