# Skills Manager CLI

A powerful command-line interface for managing "vibe coding" skills in your Antigravity or Claude Code projects. This tool bridges your centralized global skills repository with your local project environments.

## 📖 Table of Contents
- [Design Architecture](#-design-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [User Manual](#-user-manual)
  - [Managing Skills](#managing-skills)
  - [Managing Bundles](#managing-bundles)
  - [Managing Workflows](#managing-workflows)
  - [Project Maintenance](#project-maintenance)

---

## 🏗 Design Architecture

The **Skills Manager** operates on a simple but effective linking philosophy:

1.  **Global Repository (Source of Truth)**:
    -   All skills are stored centrally in your home directory (e.g., `~/.agent/skills` or `%USERPROFILE%\.agent\skills`).
    -   This repository is typically a clone of `antigravity-awesome-skills`.

2.  **Project Integration (Symlinks)**:
    -   When you "install" a skill into a project, the tool creates a **Symbolic Link** from the global repo to your project's `.agent/skills/` folder.
    -   **Benefit**: You don't duplicate files. Updates to the global repo are immediately available to your project.
    -   **Benefit**: Saves disk space and keeps skills consistent.

3.  **Bundle System**:
    -   The tool parses the `BUNDLES.md` file from the global repository documentation.
    -   It treats markdown headers as "Pack Names" and link lists as "Skill Collections".
    -   This allows for dynamic, curated installations without hardcoding lists in the script.

4.  **Workflow System**:
    -   Based on `~/.agent/skills/data/workflows.json`.
    -   Workflows represent end-to-end task flows (e.g., "Ship a SaaS MVP") with recommended skills.
    -   Provides a higher-level abstraction than bundles for goal-oriented setup.

5.  **Interactive Terminal Output**:
    -   **Clickable Links**: Skill names in the output are clickable links (OSC 8 hyperlinks) pointing directly to the skill's `SKILL.md` file or directory.
    -   **Rich Formatting**: Uses ANSI escape codes for clear, colored output.

---

## ⚙ Prerequisites

-   **Python 3.8+** installed and available in your PATH.
-   **Global Skills Repository** installed at:
    -   Windows: `%USERPROFILE%\.agent\skills`
    -   Linux/Mac: `~/.agent/skills`
    -   *Installation*:
        ```bash
        git clone https://github.com/sickn33/antigravity-awesome-skills.git ~/.agent/skills
        ```

---

## 🚀 Installation

1.  Copy the `skills_manager.py` script to your project root or a directory in your PATH.
2.  (Optional) Create an alias or shell function for easier access:
    ```powershell
    # PowerShell Profile
    function skills { python c:\path\to\skills_manager.py $args }
    ```

---

## 📘 User Manual

### Managing Skills

#### List Project Skills
View skills currently installed in your active project.
```bash
python skills_manager.py list
```

#### List Global Skills
View all skills available in your global repository.
```bash
python skills_manager.py list --global
```

#### Search Skills
Find a skill by name (supports fuzzy matching).
```bash
python skills_manager.py search "planning"
# Output: concise-planning, planning-with-files...
```

#### Install a Skill
Add a specific skill to your current project.
```bash
python skills_manager.py install concise-planning
```

#### Uninstall a Skill
Remove a specific skill from your current project.
```bash
python skills_manager.py uninstall concise-planning
```

---

### Managing Bundles
Bundles are curated sets of skills (e.g., "Essentials", "Security Engineer") defined in your global documentation.

#### Search Bundles
Find bundles by name or by the skills they contain.
```bash
python skills_manager.py bundle search "react"
# Output: Web Wizard, TypeScript & JavaScript...
```

#### List Bundles
See all available skill packs.
```bash
python skills_manager.py bundle list
```

#### Install a Bundle
Install all skills contained in a specific pack.
```bash
python skills_manager.py bundle install "Essentials"
```

#### Uninstall a Bundle
Remove all skills associated with a specific pack.
```bash
python skills_manager.py bundle uninstall "Essentials"
```

---

### Managing Workflows
Workflows are goal-oriented collections of skills designed for specific tasks (e.g., "Ship specific MVP", "Security Audit").

#### List Workflows
View all available workflows and their descriptions.
```bash
python skills_manager.py workflow list
```

#### Search Workflows
Find workflows by ID, name, description, or included skills.
```bash
python skills_manager.py workflow search "SaaS"
```

#### Install Workflow Skills
Install all skills recommended for a specific workflow.
```bash
python skills_manager.py workflow install ship-saas-mvp
```

---

### Project Maintenance

#### Clear All Skills
Wipe the slate clean. Removes ALL skills from the current project.
```bash
# Interactive mode (asks for confirmation)
python skills_manager.py clear

# Force mode (no confirmation)
python skills_manager.py clear --force
```
