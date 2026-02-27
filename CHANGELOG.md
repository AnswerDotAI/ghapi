# Release notes

<!-- do not remove -->

## 1.0.11

### New Features

- Use Content-Type to determine response parsing ([#205](https://github.com/AnswerDotAI/ghapi/pull/205)), thanks to [@erikgaas](https://github.com/erikgaas)


## 1.0.10

### New Features

- `GhApi.get_repo_contents` method ([#190](https://github.com/AnswerDotAI/ghapi/pull/190)), thanks to [@KeremTurgutlu](https://github.com/KeremTurgutlu)


## 1.0.9

### New Features

- Update API ([#203](https://github.com/AnswerDotAI/ghapi/issues/203))
- Add GraphQL support ([#202](https://github.com/AnswerDotAI/ghapi/pull/202)), thanks to [@erikgaas](https://github.com/erikgaas)
- Support for Python 3.13 and 3.14 ([#200](https://github.com/AnswerDotAI/ghapi/pull/200)), thanks to [@hugovk](https://github.com/hugovk)
- Add py.typed file so that typecheckers recognize this library as typed ([#194](https://github.com/AnswerDotAI/ghapi/pull/194)), thanks to [@jedesroches](https://github.com/jedesroches)


## 1.0.8

### Bugs Squashed

- rm `GitPython` dep ([#199](https://github.com/AnswerDotAI/ghapi/pull/199)), thanks to [@KeremTurgutlu](https://github.com/KeremTurgutlu)



## 1.0.7

### New Features

- Avoid quoting slash, thanks @soemiran ([#196](https://github.com/AnswerDotAI/ghapi/issues/196))
- Create gist with imgs ([#195](https://github.com/AnswerDotAI/ghapi/pull/195)), thanks to [@KeremTurgutlu](https://github.com/KeremTurgutlu)


## 1.0.6

### New Features

- Automatically decode response based on path ([#183](https://github.com/fastai/ghapi/pull/183)), thanks to [@radam9](https://github.com/radam9)
- Expose timeout [#174](https://github.com/fastai/ghapi/pull/174)), thanks to [@HarikrishnanBalagopal](https://github.com/HarikrishnanBalagopal)

### Bugs Squashed

- Github now requires branch, author, and committer in file update calls ([#184](https://github.com/fastai/ghapi/issues/184))
- Remove the check which removes `None` values ([#171](https://github.com/fastai/ghapi/pull/171)), thanks to [@shreve](https://github.com/shreve)


## 1.0.3

### New Features

- add `authenticate` arg which allows unauthenticated `GhApi` clients even if `GITHUB_TOKEN` is set ([#150](https://github.com/fastai/ghapi/pull/150)), thanks to [@seeM](https://github.com/seeM)


## 1.0.1

### New Features

- warn if no GitHub token found ([#145](https://github.com/fastai/ghapi/issues/145))
- set `GITHUB_DEBUG=1` to print requests sent to GitHub


## 1.0.0

### New Features

- add `delete_file` and `create_file` ([#143](https://github.com/fastai/ghapi/issues/143))
- Add a "Documentation" link to the sidebar on PyPI ([#106](https://github.com/fastai/ghapi/pull/106)), thanks to [@nedbat](https://github.com/nedbat)
- Add support for media types ([#102](https://github.com/fastai/ghapi/pull/102)), thanks to [@lfdebrux](https://github.com/lfdebrux)

### Bugs Squashed

- Fix links to GitHub docs ([#136](https://github.com/fastai/ghapi/pull/136)), thanks to [@hwine](https://github.com/hwine)


## 0.1.21

### Bugs Squashed

- fix `create_gist`


## 0.1.20

### New Features

- add `create_gist` ([#129](https://github.com/fastai/ghapi/issues/129))

### Bugs Squashed

- `HTTP Error 422: Unprocessable Entity` returned for `issues.add_labels` in version `0.1.17` ([#69](https://github.com/fastai/ghapi/issues/69))


## 0.1.19

### New Features

- Remove need to URL-quote some parameters ([#54](https://github.com/fastai/ghapi/issues/54))


## 0.1.18

### Bugs Squashed

- `HTTP Error 422: Unprocessable Entity` returned for `issues.add_labels` ([#69](https://github.com/fastai/ghapi/issues/69))


## 0.1.17


### Bugs Squashed

- Fix ability to define scopes ([#53](https://github.com/fastai/ghapi/pull/53)), thanks to [@danpalmer](https://github.com/danpalmer)


## 0.1.15

### New Features

- make `actions_group` a context manager ([#33](https://github.com/fastai/ghapi/issues/33))


## 0.1.14

### New Features

- `text` property for `GhEvent` ([#23](https://github.com/fastai/ghapi/issues/23))

### Bugs Squashed

- broken links in index.html page ([#27](https://github.com/fastai/ghapi/issues/27))
- Bug: `paged` does not pass `kwargs` to operation ([#24](https://github.com/fastai/ghapi/issues/24))


## 0.1.13


### Bugs Squashed

- missing import in auth ([#21](https://github.com/fastai/ghapi/issues/21))


## 0.1.11

### Bugs Squashed

- missing webbrowser import ([#20](https://github.com/fastai/ghapi/issues/20))


## 0.1.10

- Add `load_sample_events`, which loads a file of 1000 sample public events


## 0.1.8

### New Features

- add `fetch_events` ([#19](https://github.com/fastai/ghapi/issues/19))


## 0.1.7

### New Features

- parallel `pages` ([#18](https://github.com/fastai/ghapi/issues/18))
- add `GhDeviceAuth` ([#15](https://github.com/fastai/ghapi/issues/15))
- add `date2gh` ([#14](https://github.com/fastai/ghapi/issues/14))


## 0.1.6

### New Features

- add `paged` ([#13](https://github.com/fastai/ghapi/issues/13))
- add `gh_date` ([#12](https://github.com/fastai/ghapi/issues/12))


## 0.1.1

### New Features

- add `list_tags` and `list_branches` ([#2](https://github.com/fastai/ghapi/issues/2))

### Bugs Squashed

- `GhApi` pickle recursion error ([#3](https://github.com/fastai/ghapi/issues/3))


## 0.1.0

- First release with full API coverage

