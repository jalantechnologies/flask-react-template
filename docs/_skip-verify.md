# Docs-only CI skip verification

Throwaway doc to confirm that after the #836 fix, a documentation-only pull
request skips `test-backend`, `test-frontend`, `scan`, and `sonarqube` while
`lint`, `label`, and `codereview` still run. Delete once confirmed.
