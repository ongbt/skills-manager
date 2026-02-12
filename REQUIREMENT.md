# Skills Manager CLI Requirements

## 1. Overview
Develop a Command Line Interface (CLI) tool to manage "vibe coding" skills for Antigravity, Claude Code, and compatible agents. This tool acts as a bridge between a locally cloned global skills repository and a specific project's configuration.

**Reference Repository:** [antigravity-awesome-skills](https://github.com/sickn33/antigravity-awesome-skills)

## 2. Terminology & Paths
*   **Global Skills Repository**: The source directory where all skills are cloned.
    *   **Windows Path**: `$env:USERPROFILE\.agent\skills\skills`
    *   **Linux/Mac Path**: `~/.agent/skills/skills`
*   **Project Skills Directory**: The destination directory in the user's current project where skills are installed.
    *   **Path**: `./.agent/skills/`
*   **Bundle Definition**: Located at `$env:USERPROFILE\.agent\skills\docs\BUNDLES.md`.

## 3. Functional Requirements

### 3.1. Skill Discovery
#### 3.1.1. List Global Skills
*   **Description**: List all available skills found in the Global Skills Repository.
*   **Behavior**: Traverse the global skills folder and display valid skill directories.

#### 3.1.2. List Project Skills
*   **Description**: List skills currently installed in the active project.
*   **Behavior**: Check the local `./.agent/skills/` folder and list installed skills.

#### 3.1.3. Search Skills
*   **Description**: Search for skills in the Global Repository using a query string.
*   **Matching Logic**:
    *   **Fuzzy Matching**: Should support matching ignoring symbols (e.g., `-`, `_`).
    *   **Scope**: Support "starts with" and "contains" matching.
    *   **Case Sensitivity**: Search must be case-insensitive.

### 3.2. Skill Management
#### 3.2.1. Install Skill
*   **Description**: Install a specific skill into the current project.
*   **Mechanism**: Create a **Symbolic Link** (preferred) from the Global Repository to the Project Skills Directory.
*   **Validation**: Verify the skill exists in the Global Repository before attempting installation.
*   **Error Handling**: Inform the user if the skill does not exist or if it is already installed.
*   **Implementation Note (Windows)**:
    ```powershell
    New-Item -Path '.\.agent\skills\<skill-name>' -ItemType SymbolicLink -Value "$env:USERPROFILE\.agent\skills\skills\<skill-name>"
    ```

#### 3.2.2. Uninstall Skill
*   **Description**: Remove a skill from the current project.
*   **Mechanism**: Delete the symbolic link or folder in the Project Skills Directory. 
*   **Safety**: Ensure that the specific operation **does not** delete the source skill from the Global Repository.

### 3.3. Bundle Management
*   **Description**: Support operations related to Skill Bundles as referenced in the documentation.
*   **Source**: `$env:USERPROFILE\.agent\skills\docs\BUNDLES.md` (or relative `../docs/BUNDLES.md` from the skills repo).
*   **Feature**: Ability to parse the bundle file and potentially install groups of skills (detailed requirements to be defined based on file format).

## 4. Technical Requirements
*   **Platform**: Primary support for Windows (due to specific path and command requirements).
*   **Execution Location**: The CLI must be runnable from the root of the target project.
*   **Dependencies**: Minimal dependencies preferred for ease of distribution.
