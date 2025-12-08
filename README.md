# AgentFlow
This repository contains the AgentFlow project (backend + frontend).

## Developer workspace settings
To avoid VS Code showing Markdown linting errors for every `.md` file in the project, this workspace contains the following:

- `.markdownlintignore` — ignore all markdown files for markdownlint CLI
- `.vscode/settings.json` — workspace settings to ignore markdown files, and disable built-in markdown validator

If you'd like to re-enable markdownlint in your local workspace, remove or edit the `"markdownlint.ignore"` setting from `.vscode/settings.json`.

