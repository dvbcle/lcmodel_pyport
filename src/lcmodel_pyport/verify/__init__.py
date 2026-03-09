"""Verification package.

Keep package init import-light to avoid circular imports between
`pipeline.*` and `verify.evidence` during test collection.
"""

__all__: list[str] = []
