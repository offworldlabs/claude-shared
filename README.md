# claude-shared

Offworld Labs' org-wide Claude Code resource: a **plugin marketplace** (`offworld`)
plus **shared reference docs** used across every repo in the organisation.

- `plugins/core` — the `core` plugin (skills, commands, agents, hooks).
- `rules/` — shared rules symlinked into each repo's `.claude/rules/`.
- `docs/` — on-demand org-wide docs (architecture, contracts, decisions, runbooks).
- `templates/` — drop-in `settings.json` and `CLAUDE.md` for new repos.

## Install

In any repo, add the marketplace and install the plugin:

```
/plugin marketplace add offworldlabs/claude-shared
/plugin install core@offworld
```

## Adopting in a consuming repo

For zero-setup adoption, copy the template settings into the repo so everyone
who trusts the folder gets the marketplace and `core` plugin automatically:

```bash
mkdir -p .claude
cp path/to/claude-shared/templates/settings.json .claude/settings.json
```

`.claude/settings.json` registers the `offworld` marketplace via
`extraKnownMarketplaces` and enables `core@offworld` via `enabledPlugins`, so
opening the repo prompts installation with no manual `/plugin` commands.

Symlink the shared rules into the repo so they stay in sync with this repo:

```bash
mkdir -p .claude/rules
ln -s ../../path/to/claude-shared/rules/security.md   .claude/rules/security.md
ln -s ../../path/to/claude-shared/rules/code-style.md .claude/rules/code-style.md
```

Point the repo's `CLAUDE.md` at this repo's `docs/` for org-wide context instead
of duplicating it (see `templates/CLAUDE.md`).

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
