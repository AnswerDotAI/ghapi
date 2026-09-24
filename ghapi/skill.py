"""GitHub REST and GraphQL access, plus local git operations. Read before working with GitHub issues, PRs, CI, releases, branches, or gists, and before repo-local git operations.

`GhApi`: GitHub REST, endpoints generated from bundled OpenAPI metadata. `GhGql`: GraphQL, for nested reads that would take many REST calls. `Git` (fastgit): local checkout. Creating/inspecting clients sends no requests. Credentials come from the env; never print tokens or auth headers. Prefer async clients; `sync=True` makes generated endpoints blocking, but convenience methods (`api.read_issue`, `read_pr`, `gh_notifs`, ...) stay async, so check each callable's doc.

# Finding the right call

Read `doc(GhApi)`, create a client for the target owner/repo, then inspect the instance (class inspection can't show generated ops):

    api = GhApi(owner='AnswerDotAI', repo='ghapi')
    doc(api)
    xdir(api.actions, 'log')
    doc(api.actions.download_job_logs_for_workflow_run)

`doc(api)` lists groups; a group lists ops and subgroups; search big groups with `xdir`. Read an op's own `doc()` (params, defaults) before calling; call the op object, never `type(op).__call__`. `doc(GhApi)` also lists convenience methods combining several endpoints; read their bound forms (`doc(api.read_issue)`), which explain what endpoint summaries can't (general vs inline review comments; legacy statuses vs check runs).

# Workflows

- Issue/PR review: `api.read_issue` (structured fields), `read_pr` (one markdown string), `pr_file_diff` (one file's full diff). Display results bare; inspect fields when the summary isn't enough.
- Whole repo as model context: `toolslm.xml.repo2ctx`, not the contents API file by file; metadata endpoints when contents aren't needed.
- CI triage: read the whole `api.check_status`/`api.pr_status` report before picking failed jobs (a passing check beside a failing one is evidence), then `api.failed_step_log` per failed job before logs expire. Cross-repo reads can run concurrently; rule out a shared upstream failure before treating downstream failures as independent.
- Filing an issue: REST bypasses issue forms; read the form with `api.issue_template`, build the body with `issue_body`. Whole-PR comments go via the Issues API; inline review comments are a separate workflow.
- `gh_notifs`: recent notifications. `call_gh`: one-off call from sync code.
- List endpoints are paginated: `paged` iterates serially, `pages` fetches in parallel. `api.limit_rem`/`api.recv_hdrs`: rate limit, response headers.

# GraphQL

Discover via objects: the client, a fragment (`gql.repo('owner/name')`), or a schema type; read a fragment's doc before binding args and selecting fields. `gql.batch`: independent queries; `gql.paged`: long connections. Sandbox policy blocks mutations/subscriptions.

# Local changes and writes

`Git`: checkout state, diffs, branches, commits. Inspect it and the bound command before running; it returns errors as output rather than raising by default, so check each result. Keep unrelated work intact: external contributions go on their own branch/worktree, with fork vs upstream confirmed before publishing; never discard uncommitted work as cleanup.

Reading docs doesn't authorise writes. Sandbox policies allow a restricted git command set and read-only (GET/HEAD) GitHub ops. Confirm scope before posting, changing permissions, deleting, or publishing.
"""

from ghapi.all import GhApi, paged, pages, read_pr, pr_file_diff, gh_notifs, call_gh, issue_body
from ghapi.graphql import GhGql
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
    cmds = {'blame','branch','cat-file','config','describe','diff','log','ls-files','ls-tree','merge-base',
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

class GqlPolicy(AllowPolicy):
    "GraphQL query guard -- blocks mutations and subscriptions"
    def __call__(self, obj, args, kwargs, data):
        q = args[0] if args else ''
        if 'mutation' in q.lower() or 'subscription' in q.lower():
            raise PermissionError('Only GraphQL queries are allowed; mutations and subscriptions are blocked')

allow({Git: [('__call__', GitPolicy())], OpFunc: [('__call__', ReadOnlyGhPolicy())], GhGql: [('__call__', GqlPolicy())],
       GhApi: ['read_issue', 'check_status', 'pr_status', 'failed_step_log', 'issue_template']},
      paged, pages, read_pr, pr_file_diff, gh_notifs, issue_body)

__all__ = ['Git', 'GhApi', 'GhGql', 'call_gh', 'paged', 'pages', 'read_pr', 'pr_file_diff', 'gh_notifs', 'issue_body']
