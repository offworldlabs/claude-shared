# claude-shared

Offworld Labs' org-wide Claude Code resource: a **plugin marketplace** (`offworld`)
plus **shared reference docs** used across every repo in the organisation.

- `plugins/core` — the `core` plugin; its `setup-repo` skill bundles the shared rules, `.claude/settings.json`, `CLAUDE.md`, and CI workflow templates used to scaffold new repos.
- `docs/` — on-demand org-wide docs (architecture, contracts, decisions, runbooks).

## Install

Install once per machine, at user scope:

```
/plugin marketplace add offworldlabs/claude-shared
/plugin install core@offworld
```

## Adopting in a consuming repo

Adoption is driven by Claude Code, not manual copying. With `core` installed
(see Install above), open any new repo, start Claude Code, and ask:

> set this repo up per `claude-shared`

Claude invokes the `core:setup-repo` skill, which writes `.claude/settings.json`
(registering the marketplace and enabling `core`), a `CLAUDE.md`, the shared rules,
the Claude review workflows, and your stack's tooling — then installs deps and
helps you flesh out `CLAUDE.md`. See `docs/runbooks/github-actions-claude-review.md`
for the one manual follow-up (the `CLAUDE_CODE_OAUTH_TOKEN` secret).

## Contributing

Skills graduate from personal experimentation into the shared `core` plugin
through review:

1. **Develop personally first.** Iterate on the skill in your own `~/.claude/`
   until it works.
2. **Never merge a skill you haven't run.** A skill that hasn't been exercised
   end-to-end does not go in.
3. **Test locally before opening the PR.** Add this checkout as a local
   marketplace and reload:
   ```
   /plugin marketplace add ./path/to/claude-shared
   /plugin install core@offworld
   /reload-plugins
   ```
4. **Open a PR** moving the skill into `plugins/core/skills/<name>/SKILL.md`.
5. **Bump the plugin version** in `plugins/core/.claude-plugin/plugin.json` on
   every merged change. The version is the update signal for the entire org —
   without a bump, no one receives the change.
