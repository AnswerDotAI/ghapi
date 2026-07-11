"""GitHub REST API access via `GhApi`, plus local git operations via `fastgit.Git`. Use this for day-to-day GitHub work: reading/creating issues and PRs, checking CI status, managing releases/branches/gists, and repo-local git operations -- all from Python, no shelling out to `gh`/`git` needed.

`ghapi` is a full, always-up-to-date wrapper over the entire GitHub REST API, dynamically generated from GitHub's own OpenAPI spec. `fastgit` is a tiny complementary wrapper around the local `git` CLI, for anything that's about the local repo rather than GitHub's servers -- cheaper, and not rate-limited. As of v2, `ghapi` is async by default: `await` every API call (notebooks and modern REPLs support top-level `await`; scripts use `asyncio.run`). For sync code, `GhApi(sync=True)` gives a client whose generated endpoint calls block and return results directly (the convenience methods below stay async-only; drive those with `fastcore.aio.run_sync` on an async client. `paged`/`pages` have sync twins `sync_paged`/`sync_pages`).

# Auth

`api = GhApi()` authenticates automatically from the `GITHUB_TOKEN` environment variable (already set in most dev environments via `gh auth login`) -- no device-flow login needed. Pass `owner=`/`repo=` to the constructor to bind them as defaults for every call that needs them, so you don't have to repeat `owner, repo` on every method call:

    api = GhApi(owner='fastai', repo='ghapi')
    await api.issues.list_for_repo(state='open')   # owner/repo already bound

# Discovering the API

`api.<group>` (displayed bare, or via `doc()`) lists every endpoint in a group (issues, pulls, repos, checks, actions, gists, git, search, ...) with its signature and a link to GitHub's docs. `api['/path/{owner}/{repo}', 'GET']` looks up an endpoint by path+verb if you'd rather not use the grouped names. Endpoint names follow `<verb>_<noun>`, e.g. `issues.list_for_repo`, `issues.create`, `pulls.merge`. Displaying `api` itself lists every available group with a docs link. `doc()` works at every level of a live instance: `doc(api)`, `doc(api.issues)`, `doc(api.issues.create)`. It must be a live instance, since the API is generated at construction time: inspecting the `GhApi` *class* shows only the convenience methods and none of the endpoint groups.

# Reading an issue or PR (including comments and reviews)

`await api.read_issue(number)` is the single call for this -- it fetches title, body, and general comments, and for PRs also the unified diff, inline review comments, and review summaries (approved/changes-requested/commented), returning an `AttrDict` whose repr is a readable summary (title, body, diff size, comment counts). Display it bare instead of printing fields; the full diff stays in `.diff`:

    info = await api.read_issue(205)
    print(info)
    print(info.diff) # if needed
    # See info.title, info.body, info.comments, info.review_comments, info.reviews for details

When you want the whole thing as one LLM-ready markdown string rather than structured data, use the module-level `await read_pr(num_or_url, owner, repo, replies=True)` -- it accepts a pasted GitHub URL directly, reduces the diff to just headers and changed lines, and appends formatted comments/review comments/reviews.

# CI / check status

`await api.check_status(ref)` merges the two ways CI results get reported -- the modern Checks API (`checks.list_for_ref`, what GitHub Actions uses) and the legacy Commit Status API (`repos.get_combined_status_for_ref`, used by some external CI) -- into one call, given a SHA/branch/tag. `api.pr_status(pull_number)` is the same, resolved from a PR's head commit.

The result's repr is a one-line-per-check summary with a verdict computed from the check runs (the raw `state` field only reflects legacy statuses, so it reads `pending` on repos that only use Actions). Display it bare; drop to `.check_runs`/`.statuses` only when the summary isn't enough.

# Day-to-day work

Issues/PRs: `issues.create`, `issues.update` (title/body/state/labels/assignees), `issues.create_comment`, `issues.add_labels`, `pulls.create`, `pulls.merge`, `pulls.create_review`. List endpoints paginate at 30/page by default (100 max per page) -- for anything that might exceed one page, use `paged(api.issues.list_for_repo, ...)` (an async generator, one page per iteration: `async for`) or `await pages(api.issues.list_for_repo, n_pages, ...)` (fetches multiple pages in parallel; get `n_pages` from `api.last_page()` if not already known).

Many repos require issues to follow their issue-form template, and the API bypasses templates entirely, so maintainers will bounce a hand-composed body. Before `issues.create` on a repo you don't maintain, fetch the templates with `await api.issue_template()` (parsed yml forms, with the owner-level `.github` repo as fallback), then build the body with `issue_body(tmpl, {label: content})`: it emits the same `### <label>` sections GitHub's web form would, and raises on missing required sections.

# Repo overview

`api.repos.get()`, `list_languages()`, `get_readme()`, `list_branches()`/`list_tags()`, `compare_commits()`, `list_contributors()`. For dumping a repo's actual file contents as LLM-ready context (not just metadata), `await toolslm.xml.repo2ctx(owner, repo)` downloads a tarball and renders it as XML without cloning -- reach for that instead of manually walking `get_repo_files`/`get_repo_contents` when the goal is "show me this repo's contents."

# GraphQL

Use `gh_query(query, variables)` for GitHub GraphQL requests that are awkward or inefficient with REST, such as nested org/repo queries or cross-repo searches.

# Gists

`await api.create_gist(description, content, img_paths=...)` (uploads images and rewrites markdown links to their raw URLs) and `api.update_gist(id, content)` (replaces the first file's content) are async-only. `api.load_gist(id_or_url)` (accepts a bare id or `user/id`) and `api.gist_file(id)` (first file's contents) follow the client's mode: awaitable on an async client, direct results on `GhApi(sync=True)`.

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
- HTTP errors raise `fastspec.errors.APIError`, which carries `.status_code` and the endpoint called.
- `per_page` maxes out at 100; beyond that, use `paged`/`pages` rather than manually looping `page=`.
- Per-call headers on named endpoints use `_headers=` (e.g. `await api.pulls.get(n, _headers={'Accept': 'application/vnd.github.v3.diff'})` for the raw diff); plain `headers=` is a kwarg only for direct `api(path, verb, ...)` calls.
- `GITHUB_TOKEN` unset means unauthenticated (heavily rate-limited, no write access) -- `GhApi()` warns but doesn't raise.
"""

from ghapi.all import GhApi, paged, pages, read_pr, pr_file_diff, gh_notifs, call_gh, issue_body
from ghapi.graphql import gh_query
from fastgit import Git
from pyskills import AllowPolicy, allow
from fastspec.oapi import OpFunc

class ReadOnlyGhPolicy(AllowPolicy):
    def __call__(self, obj, args, kwargs, data):
        endp = 'api.github.com'
        if endp not in obj.base_url:               raise PermissionError(f"Endpoint '{endp}' is allowed not '{obj.base_url}'")
        if obj.verb.upper() not in ('GET','HEAD'): raise PermissionError(f"Only GET and HEAD are allowed for '{endp}'")

allow({OpFunc: [('__call__', ReadOnlyGhPolicy())]})
class GitPolicy(AllowPolicy):
    "Allow only safecmd-default git subcommands"
    cmds = {
        'blame','branch','cat-file','config','describe','diff','log','ls-files','ls-tree','merge-base',
        'remote','rev-parse','shortlog','show','stash','status','tag','fetch','add','commit','switch','checkout'}

    def __call__(self, obj, args, kwargs, data):
        cmd = args[0] if args else None
        if cmd not in self.cmds: raise PermissionError(f"git {cmd} not allowed")
        if cmd == 'config':
            vals = [str(x) for x in args[1:]]
            if not vals or vals[0] not in ('--get', '--list'): raise PermissionError("only git config --get/--list allowed")
        if cmd == 'stash':
            vals = [str(x) for x in args[1:]]
            if vals[:1] != ['list']: raise PermissionError("only git stash list allowed")

_gh_query_orig = gh_query
def _gh_query_guard(query, variables=None):
    "GraphQL query guard — blocks mutations and subscriptions"
    if 'mutation' in query.lower() or 'subscription' in query.lower():
        raise PermissionError('Only GraphQL queries are allowed; mutations and subscriptions are blocked')
    return _gh_query_orig(query, variables)
gh_query = _gh_query_guard

allow({Git: [('__call__', GitPolicy())], OpFunc: [('__call__', ReadOnlyGhPolicy())]}, gh_query, paged, pages, read_pr, pr_file_diff, gh_notifs)

__all__ = ['Git', 'GhApi', 'gh_query', 'call_gh', 'paged', 'pages', 'read_pr', 'pr_file_diff', 'gh_notifs', 'issue_body']
