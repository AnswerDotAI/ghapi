"""A python client for the GitHub API

Modules:

- `ghapi.graphql`: Query GitHub's GraphQL API: schema-aware chained queries, one-request batching, and raw GraphQL
- `ghapi.skill`: GitHub REST API access via `GhApi`, plus local git operations via `fastgit.Git`. Trigger: ALWAYS read before reading/creating issues and PRs, checking CI status, managing releases/branches/gists, and doing repo-local git operations."""

__version__ = "2.1.3"
