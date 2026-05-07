# Contributing

The project uses [uv](https://github.com/astral-sh/uv) for dependencies and local workflows.

## Checks

From the repository root:

```bash
uv sync
uv run ./lint
uv run ./test
uv run ./typecheck
```

Or run everything:

```bash
uv run ./all
```

## Documentation site (this site)

Install documentation dependencies and serve locally:

```bash
uv sync --extra docs
uv run mkdocs serve
```

Build a static site (same command CI uses):

```bash
uv run ./docs-build
```

The built output is written to `site/` (gitignored).

## Hosting

Published docs are intended for [Read the Docs](https://readthedocs.org/) using `mkdocs.yml` (see `.readthedocs.yaml`). Maintainers can alternatively deploy the `site/` output to GitHub Pages or another static host.

## Legacy Sphinx files

The `docs/conf.py` tree is an older Sphinx scaffold kept in-repo for reference; the canonical doc build for Read the Docs is MkDocs as configured in `mkdocs.yml`.
