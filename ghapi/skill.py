"""GitHub REST and GraphQL access, plus local git operations. Read before working with GitHub issues, PRs, CI, releases, branches, or gists, and before repo-local git operations.

Use `GhApi` for GitHub resources and `Git` for the local checkout. The REST surface comes from the bundled GitHub OpenAPI metadata. Use `GhGql` for nested reads or queries that would otherwise require many REST requests. Creating clients and inspecting their generated objects does not send requests.

# Discover before calling

Read `doc(GhApi)` before constructing a client. Configure the intended account and repository, then inspect the actual instance. Authentication can use environment credentials; do not print tokens or request authorization headers.

    api = GhApi(owner='AnswerDotAI', repo='ghapi')
    doc(api)
    xdir(api.actions, 'log')
    doc(api.actions.download_job_logs_for_workflow_run)

A root display lists groups. A group display lists operations and subgroups. Search large groups with `xdir` rather than rendering hundreds of entries. Read the selected operation's full docs, including parameter descriptions and defaults, before calling it. Class inspection cannot show generated operations. Do not substitute `type(operation).__call__` for the operation object.

Convenience methods are listed by `doc(GhApi)`; inspect their bound forms, such as `doc(api.read_issue)`. Their docs explain distinctions the endpoint summary cannot: general versus inline review comments, legacy status versus check-run verdicts, and the structure of returned results.

Use an async client unless the task requires blocking calls. Generated sync endpoints and async convenience methods have different calling requirements; read the constructor and selected callable rather than assuming one mode applies to everything.

# Workflows

For an issue or PR review, prefer the combined reading helpers over assembling many endpoint calls. Choose structured results or a formatted review according to what the next step needs. Display tuned result objects bare. Inspect their documented fields when the summary is insufficient.

For a whole repository's file contents as model context, inspect `toolslm.xml.repo2ctx` rather than walking the contents API file by file. Use repository metadata endpoints when file contents are not needed.

For CI triage, inspect the full status report before selecting failed jobs. A passing check beside a failing one is relevant evidence. Read failed-step logs while they remain available. Across repositories, independent reads can run concurrently; investigate shared upstream failures before treating every downstream failure as independent.

The REST API bypasses issue forms. Read the repository's templates before filing an issue, then use the form-building helper. General comments on a PR belong to the Issues API; inline code-review comments are a separate workflow.

Treat list endpoints as paginated. Use the pagination helpers rather than assuming the first response contains everything. Read their docs for iteration and concurrency. Rate limits and response metadata are exposed by the client.

GraphQL discovery is also object-based. Inspect the client, a query fragment, or a schema type. Read a fragment before binding its arguments and selecting fields. Use batching for independent queries and paging for long connections. In this skill's sandbox policy, mutations and subscriptions are blocked.

# Local changes and external writes

Use local Git for checkout state, diffs, branches, and commits. Inspect `Git` and the actual bound command before use. Check returned output for errors; lack of a raised exception is not proof of success.

Keep unrelated work intact. For an external contribution, isolate the task's changes on a suitable branch or worktree and confirm the fork and upstream destinations before publishing. Never discard uncommitted work as automatic cleanup.

Reading documentation does not authorize writes. The skill's sandbox policies allow a restricted set of Git commands and read-only generated GitHub operations. They do not grant unrestricted API access. Confirm the requested scope before posting, changing permissions, deleting resources, or publishing code.
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

allow({Git: [('__call__', GitPolicy())], OpFunc: [('__call__', ReadOnlyGhPolicy())], GhGql: [('__call__', GqlPolicy())]}, paged, pages, read_pr, pr_file_diff, gh_notifs)

__all__ = ['Git', 'GhApi', 'GhGql', 'call_gh', 'paged', 'pages', 'read_pr', 'pr_file_diff', 'gh_notifs', 'issue_body']
