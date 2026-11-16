# LensQL
AI-powered learning tool to support SQL learning, with a focus on common error patterns and learning objectives

## Tests

Run `make test` to test only the app. The `dev` and `prod` targets also run
this app check before starting.

Run `make test_dependencies` to clone fresh copies of `sqlerrors`, `sqlscope`,
`sqlchecker`, and `sqlexercise` from GitHub into a temporary directory, install
them into LensQL's `.venv`, and run all four dependency suites. Local sibling
repositories and their tests are ignored. This command requires network access.
Every dependency suite runs even if an earlier suite fails; any failure fails
the command. Temporary checkouts are removed on success or failure. Installed
packages remain available in `.venv` after cleanup.

Use `PYTEST_ARGS="-q"` with either target to pass options to pytest.

## To Do
- [ ] Focus on learning objectives
- [ ] Focus on common error patterns
- [ ] Prevent over-reliance on fix button
- [ ] Make users more aware of their learning process
