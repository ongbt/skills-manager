# Gemini (Project Constitution)

## Data Schemas

### Skill
- Name: string (directory name)
- Path: string (absolute path to global skill directory)
- Description: string (derived from SKILL.md or metadata)

### Bundle
- Name: string (e.g., "The Essentials Starter Pack")
- Skills: List[string] (list of skill names)

### Workflow
- ID: string
- Name: string
- Description: string
- Steps: List[Step]
- RecommendedSkills: List[string]

## Behavioral Rules
- **Platform:** Primary support for Windows (Use PowerShell for symlinks).
- **Safety:** Uninstalling a skill from a project must NEVER delete the source skill from the Global Repository.
- **Matching:** Search must be case-insensitive and support fuzzy matching (ignoring symbols like `-`, `_`).
- **Dependencies:** Minimal dependencies. Use standard library where possible.

## Architectural Invariants
- **Global Skills Repo:** `$env:USERPROFILE\.agent\skills\skills` (Windows)
- **Project Skills Dir:** `./.agent/skills/`
- **Bundles Definition:** `$env:USERPROFILE\.agent\skills\docs\BUNDLES.md`
- **Workflows Definition:** `$env:USERPROFILE\.agent\skills\data\workflows.json`

## Maintenance Log
- [x] Initialized project memory.
- [x] Defined initial data schemas and rules based on REQUIREMENT.md.
