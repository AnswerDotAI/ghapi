# NB: this file is designed for an LLM reader, not a human. Add it to your LLM's context and ask it to explain.
"""GitHub REST (`GhApi`) and GraphQL (`GhGql`), plus local git via `fastgit` (`Git`). Read before working with GitHub issues, PRs, CI, releases, branches, or gists, or any repo-local git operations.

- GraphQL (`GhGql`) over REST (`GhApi`): nested reads that would take many REST calls
- credentials from env; never print tokens, auth headers
- prefer async clients    /under `sync=True`, convenience methods stay async

# Finding the right call

- `doc(GhApi)`: convenience methods; bound docs (`doc(api.read_issue)`) cover what endpoint summaries can't: general vs inline review comments, legacy statuses vs check runs
- endpoints: call the op object, never `type(op).__call__`

# Workflows

- review: `api.read_issue`, `read_pr`, `pr_file_diff`
- repo as model context: `toolslm.xml.repo2ctx`, not per-file contents; metadata endpoints when contents aren't needed
- CI: whole `api.check_status` or `api.pr_status` report before picking failed jobs    /passing check beside failing one is evidence
- failed job: `api.failed_step_log`, before logs expire
- across repos: reads can run concurrently; rule out shared upstream failure before treating failures as independent
- new issue: `api.issue_template`    /REST bypasses issue forms
- comments: whole PR: Issues API; inline review: Pulls API (`xdir(api.pulls, 'review_comment')`)
- `api.limit_rem`: rate limit; `api.recv_hdrs`: response headers

# GraphQL

- discover from client, fragment (`gql.repo('owner/name')`) or schema type; fragment's doc before args, fields
- `gql.batch`: independent queries; `gql.paged`: long connections

# Local git

- `Git` (fastgit): subcommand = method, `_` for `-` (`git.cherry_pick(sha)`); keyword = flag; `__`: paths after `--` (`git.diff(stat=True, __='src')` → `git diff --stat -- src`)
- external diff tool shortens or changes output: `no_ext_diff=True`
- errors return as output by default: check each result
- keep unrelated work; external contributions: own branch or worktree, fork vs upstream confirmed before publishing; never discard uncommitted work as cleanup

# Writes

- docs don't authorise them; confirm scope before posting, permission changes, deleting, publishing
- sandbox: git restricted; GitHub REST GET, HEAD only; GraphQL: no mutations, subscriptions
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
