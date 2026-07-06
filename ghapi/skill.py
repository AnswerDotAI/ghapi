"""GitHub REST API access via `GhApi`, plus local git operations via `fastgit.Git`. Use this for day-to-day GitHub work: reading/creating issues and PRs, checking CI status, managing releases/branches/gists, and repo-local git operations -- all from Python, no shelling out to `gh`/`git` needed.

`ghapi` is a full, always-up-to-date wrapper over the entire GitHub REST API, dynamically generated from GitHub's own OpenAPI spec. `fastgit` is a tiny complementary wrapper around the local `git` CLI, for anything that's about the local repo rather than GitHub's servers -- cheaper, and not rate-limited.

# Auth

`api = GhApi()` authenticates automatically from the `GITHUB_TOKEN` environment variable (already set in most dev environments via `gh auth login`) -- no device-flow login needed. Pass `owner=`/`repo=` to the constructor to bind them as defaults for every call that needs them, so you don't have to repeat `owner, repo` on every method call:

    api = GhApi(owner='fastai', repo='ghapi')
    api.issues.list_for_repo(state='open')   # owner/repo already bound

# Discovering the API

`print(api.<group>)` lists every endpoint in a group (issues, pulls, repos, checks, actions, gists, git, search, ...) with its signature and a link to GitHub's docs. `api['/path/{owner}/{repo}', 'GET']` looks up an endpoint by path+verb if you'd rather not use the grouped names. Endpoint names follow `<verb>_<noun>`, e.g. `issues.list_for_repo`, `issues.create`, `pulls.merge`. Displaying `api` itself lists every available group with a docs link.

# Reading an issue or PR (including comments and reviews)

`api.read_issue(number)` is the single call for this -- it fetches title, body, and general comments, and for PRs also the unified diff, inline review comments, and review summaries (approved/changes-requested/commented), returning an `AttrDict` whose repr is a readable summary (title, body, diff size, comment counts). Display it bare instead of printing fields; the full diff stays in `.diff`:

    info = api.read_issue(205)
    info.title, info.body, info.diff, info.comments, info.review_comments, info.reviews

This exists because GitHub's REST API doesn't treat these uniformly: a PR *is* an issue, so its general comments come from `issues.list_comments`, not `pulls.*`; the diff needs a special `Accept` header; and review comments/reviews are yet another pair of endpoints. `read_issue` also transparently falls back to a linked commit's diff for a plain issue that was closed by a commit reference (e.g. "Fixes #123").

When you want the whole thing as one LLM-ready markdown string rather than structured data, use the module-level `read_pr(num_or_url, owner, repo, replies=True)` -- it accepts a pasted GitHub URL directly, reduces the diff to just headers and changed lines, and appends formatted comments/review comments/reviews.

# CI / check status

`api.check_status(ref)` merges the two ways CI results get reported -- the modern Checks API (`checks.list_for_ref`, what GitHub Actions uses) and the legacy Commit Status API (`repos.get_combined_status_for_ref`, used by some external CI) -- into one call, given a SHA/branch/tag. `api.pr_status(pull_number)` is the same, resolved from a PR's head commit.

The result's repr is a one-line-per-check summary with a verdict computed from the check runs (the raw `state` field only reflects legacy statuses, so it reads `pending` on repos that only use Actions). Display it bare; drop to `.check_runs`/`.statuses` only when the summary isn't enough.

# Day-to-day work

Issues/PRs: `issues.create`, `issues.update` (title/body/state/labels/assignees), `issues.create_comment`, `issues.add_labels`, `pulls.create`, `pulls.merge`, `pulls.create_review`. List endpoints paginate at 30/page by default (100 max per page) -- for anything that might exceed one page, use `paged(api.issues.list_for_repo, ...)` (a generator, one page per iteration) or `pages(api.issues.list_for_repo, n_pages, ...)` (fetches multiple pages in parallel; get `n_pages` from `api.last_page()` if not already known).

# Repo overview

`api.repos.get()`, `list_languages()`, `get_readme()`, `list_branches()`/`list_tags()`, `compare_commits()`, `list_contributors()`. For dumping a repo's actual file contents as LLM-ready context (not just metadata), `toolslm.xml.repo2ctx(owner, repo)` downloads a tarball and renders it as XML without cloning -- reach for that instead of manually walking `get_repo_files`/`get_repo_contents` when the goal is "show me this repo's contents."

# Gists

`api.create_gist(description, content, img_paths=...)` (uploads images and rewrites markdown links to their raw URLs), `api.load_gist(id_or_url)` (accepts a bare id or `user/id`), `api.gist_file(id)` (first file's contents), `api.update_gist(id, content)` (replaces the first file's content).

# Local git (fastgit)

For anything that's about the local repo/working tree rather than GitHub itself -- current branch, staged diff, a local commit, log -- `Git` (from `fastgit`, but exported by `ghapi.skill`) wraps the `git` CLI directly:

    g = Git('.')
    g.status()
    g.log('-1', pretty='format:%s')            # kwargs become flags
    g.add('foo.py'); g.commit(m='fix foo')
    g.log('--oneline', __=['some/path'])       # `__` passes positional path args after `--`

`Git.__call__` prints (not raises) on a `CalledProcessError` unless you pass `mute_errors=True` -- check the return value, don't assume no exception means success.

# Gotchas

- A PR *is* an issue for general comments (`issues.list_comments`, not `pulls.*`) -- inline code-review comments are the separate `pulls.list_review_comments`.
- Rate limits: register `limit_cb` on `GhApi(...)` to get called back whenever the remaining quota changes, or check `api.limit_rem` any time.
- `per_page` maxes out at 100; beyond that, use `paged`/`pages` rather than manually looping `page=`.
- `GITHUB_TOKEN` unset means unauthenticated (heavily rate-limited, no write access) -- `GhApi()` warns but doesn't raise.
"""

from ghapi.all import GhApi, paged, pages, read_pr
from fastgit import Git

__all__ = ['GhApi', 'paged', 'pages', 'read_pr', 'Git']
