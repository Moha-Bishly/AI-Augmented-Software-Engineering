# Scoped Test Guidance

This instruction applies exclusively when authoring, modifying, or reviewing tests.

## Testing Principles
1. **Public API Testing**: Exercise the application via `fastapi.testclient.TestClient`. Do not call private functions or mutate database state directly inside tests unless testing a pure unit helper.
2. **Comprehensive Coverage**: Every feature or change must contain:
   - A success/happy-path assertion verifying expected HTTP status (e.g. 200, 307) and payload/headers.
   - Failure and edge-case assertions verifying appropriate error responses (e.g. 400 Bad Request, 404 Not Found, 409 Conflict).
3. **Test Isolation & Independence**:
   - Each test must be completely self-contained and runnable independently in any order.
   - Do not rely on records inserted by prior tests. Use unique codes/aliases or reset state if needed.
4. **Behavioral Assertions**:
   - Assert on observable external behavior (HTTP status code, response JSON schema, redirection headers), rather than internal database schemas or private variables.
