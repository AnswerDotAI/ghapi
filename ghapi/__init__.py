"""A python client for the GitHub API

Modules:

- `ghapi.graphql`: Query GitHub's GraphQL API: schema-aware chained queries, one-request batching, and raw GraphQL
- `ghapi.skill`: GitHub REST API access via `GhApi`, plus local git operations via `fastgit.Git`. Use this for day-to-day GitHub work: reading/creating issues and PRs, checking CI status, managing releases/branches/gists, and repo-local git operations -- all from Python, no shelling out to `gh`/`git` needed."""

__version__ = "2.1.2"
