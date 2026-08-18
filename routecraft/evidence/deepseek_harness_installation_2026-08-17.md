# Official DeepSeek Harness local installation

## Installed identity

- Install path: `RESEARCH_WORKSPACE\deepseek-harness-local`
- Official remote: `https://github.com/deepseek-ai/deepseek-harness.git`
- Pinned commit: `47f943859bef60e4160492346772ded9b24f765a`
- Package version: `0.1.0-rc.5`
- Checkout: detached, full working tree, sparse checkout disabled
- Final Git status: clean (`0` porcelain entries)
- License: MIT

The previous third-party Python environment is not present in this directory. The installed tree contains neither `venv` nor `sample_msgs.json`.

## Reproducible toolchain

- Portable Node.js: `RESEARCH_WORKSPACE\tools\node-v24.19.0-win-x64`
- Node.js version: `v24.19.0` (Krypton LTS)
- Node archive: `node-v24.19.0-win-x64.zip`
- Verified Node archive SHA-256: `57F71AB3652E797D84ACDDC79C81CC9FF1C6DDB2A1974CDB83F00FEE9BFF4C73`
- Checksum source: Node.js official `SHASUMS256.txt`
- npm: `11.17.0`
- pnpm: `11.7.0`, matching the repository `packageManager` field
- `pnpm-lock.yaml` SHA-256: `6177EC61BDB8194EB5A606813A62FFB0AB2CC7FDFE2CD6E0249DCBFE4BCE58E0`

Node is installed inside the research workspace and was not added to the machine-wide `PATH`.

## Installation and verification

Executed successfully:

```text
pnpm install --frozen-lockfile
pnpm run build
node apps/cli/lib/bin.js --version
node apps/cli/lib/bin.js --help
pnpm dsh --version
```

The frozen installation covered 238 workspaces and installed 923 external packages. Windows native setup completed for `node-pty`, `koffi`, esbuild, and lefthook. Linux-only Landlock packages emitted expected unsupported-platform warnings and were not selected for Windows execution.

Targeted keyless tests:

```text
packages/core/agent-loop/tests/agent.spec.ts
packages/core/agent-loop/tests/request-error.spec.ts
packages/core/session/tests/fork.spec.ts
packages/llm/llm/tests/call-config.spec.ts
packages/llm/token-meter/tests/token-meter.spec.ts
packages/llm/llm-retry/tests/retry.spec.ts
```

Result: **6/6 test files passed; 90/90 tests passed**.

Web smoke test:

- Started the built CLI with the `web` profile on `127.0.0.1:3087`.
- `GET /` returned HTTP `200`.
- The smoke process was then stopped, and the port was verified closed.
- No DeepSeek API call or API key was used.

Built CLI SHA-256: `C0226687BB20F45C603EC6FE50F3DE16D1C3510C3A803304EC575EF9BC366C62`.

## How to run

Workspace launcher:

```powershell
RESEARCH_WORKSPACE\scripts\run_deepseek_harness.ps1 --version
RESEARCH_WORKSPACE\scripts\run_deepseek_harness.ps1 web
```

The launcher uses the pinned local Node runtime and built CLI. If `DSH_HOME` is unset, it uses `RESEARCH_WORKSPACE\.dsh-home`; any caller-provided `DSH_HOME` is respected. A real agent task requires `DEEPSEEK_API_KEY` or another configured provider credential, but the installation, build, tests, CLI checks, and Web smoke test do not.

## Primary sources

- Official repository: https://github.com/deepseek-ai/deepseek-harness/tree/47f943859bef60e4160492346772ded9b24f765a
- Official Node.js v24 release directory: https://nodejs.org/download/release/latest-v24.x/
- Official Node.js release status: https://nodejs.org/en/about/previous-releases
