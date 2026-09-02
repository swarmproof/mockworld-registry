# mockworld-registry

The public index of community [mockworld](https://github.com/swarmproof/mockworld) mocks.
`mockworld add mock:<name>` resolves against `registry.json` in this repo.

```bash
pip install mockworld-mcp
mockworld search weather
mockworld add mock:weather      # checksum-verified + safety-gated
mockworld run mock:weather
```

## How it works (index-as-repo)

- `registry.json` maps each `mock:<name>` → a source, version, and sha256 checksum.
- Each mock lives in its own subdirectory under [`mocks/`](./mocks). Sources use the
  `github:owner/repo@ref/subdir` scheme, so a mock is just a folder in this repo —
  no release assets, no separate repos.
- On `add`, the client fetches the subdirectory, **verifies the checksum**, runs the
  mock through `mockworld validate`, and refuses handler code that reaches for the
  network/subprocess/filesystem (untrusted-code safety gate).

## Contributing a mock

See [CONTRIBUTING.md](./CONTRIBUTING.md). In short: `mockworld new mymock`, build it,
`mockworld pack ./mymock` to get your `registry.json` entry, then open a PR adding
`mocks/mymock/` and the entry.
