# Layer 1: Architecture (CLI Design SOP)

## CLI Arguments
### Standard Structure
`skills_manager.py <command> <subcommand> [args]`

### Output Formats
- Success: Green checkmark `✅` or similar.
- Warning: Yellow warning sign `⚠️`.
- Error: Red cross `❌`.
- Info: Blue Info icon `ℹ️`.

### Error Handling
- **Input Validation:** Check if arguments are present and valid.
- **File System Errors:** Handle `FileNotFoundError`, `PermissionError`, etc. gracefully.
- **Safety Checks:** Explicitly check against deletion of global files.

## Command Specifications

### `list`
- `skills_manager.py list` (Default: Project skills)
- `skills_manager.py list -g` (Global skills)

### `search`
- `skills_manager.py search <query>` (Global skills)
- Fuzzy matching required (case-insensitive, ignore symbols).

### `install`
- `skills_manager.py install <skill_name> [skill_name_2 ...]`
- Accepts one or more skill names.
- Create symlink for each.
- Windows: Use PowerShell `New-Item -ItemType SymbolicLink`.
- Verify existence first.

### `uninstall`
- `skills_manager.py uninstall <skill_name> [skill_name_2 ...]`
- Accepts one or more skill names.
- Remove symlink/directory in project for each.
- **CRITICAL:** Ensure target is not in Global Repo.

### `bundle`
- `skills_manager.py bundle list`
- `skills_manager.py bundle search <query>`
- `skills_manager.py bundle install <bundle_name> [bundle_name_2 ...]`
- `skills_manager.py bundle uninstall <bundle_name> [bundle_name_2 ...]`

### `workflow`
- `skills_manager.py workflow list`
- `skills_manager.py workflow search <query>`
- `skills_manager.py workflow install <workflow_name> [workflow_name_2 ...]`
- `skills_manager.py workflow uninstall <workflow_name> [workflow_name_2 ...]`

## Future Extensions
- Consider `update` command to pull latest changes from git.
