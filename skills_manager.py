#!/usr/bin/env python3
"""
Skills Manager CLI - Requirement-based Implementation
Reference: .agent/skills/scripts/skills_manager.py
"""

import argparse
import sys
import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional

# --- Configuration as per REQUIREMENT.md ---
GLOBAL_SKILLS_REPO_WINDOWS = Path(os.path.expandvars(r"$USERPROFILE\.agent\skills\skills"))
# Linux/Mac fallback:
GLOBAL_SKILLS_REPO_UNIX = Path.home() / ".agent" / "skills" / "skills"

if os.name == 'nt':
    GLOBAL_SKILLS_REPO = GLOBAL_SKILLS_REPO_WINDOWS
else:
    GLOBAL_SKILLS_REPO = GLOBAL_SKILLS_REPO_UNIX

PROJECT_SKILLS_DIR = Path.cwd() / ".agent" / "skills"

BUNDLES_FILE_WINDOWS = Path(os.path.expandvars(r"$USERPROFILE\.agent\skills\docs\BUNDLES.md"))
BUNDLES_FILE_UNIX = Path.home() / ".agent" / "skills" / "docs" / "BUNDLES.md"

if os.name == 'nt':
    BUNDLES_FILE = BUNDLES_FILE_WINDOWS
else:
    BUNDLES_FILE = BUNDLES_FILE_UNIX


# --- Helper Functions ---
def print_success(msg):
    print(f"\033[92m✅ {msg}\033[0m")

def print_warning(msg):
    print(f"\033[93m⚠️  {msg}\033[0m")

def print_error(msg):
    print(f"\033[91m❌ {msg}\033[0m")

def print_info(msg):
    print(f"\033[94mℹ️  {msg}\033[0m")

def get_skill_names(directory: Path) -> List[str]:
    """Return a sorted list of skill names (directories) in the given path."""
    if not directory.exists():
        return []
    return sorted([d.name for d in directory.iterdir() if d.is_dir() and not d.name.startswith('.')])

def get_symlink_names(directory: Path) -> List[str]:
    """Return a sorted list of symlinks in the given path."""
    if not directory.exists():
        return []
    return sorted([d.name for d in directory.iterdir() if d.is_symlink()])

# --- Command Implementations ---

def list_global():
    """3.1.1 List Global Skills"""
    print_info(f"Listing Global Skills from: {GLOBAL_SKILLS_REPO}")
    skills = get_skill_names(GLOBAL_SKILLS_REPO)
    
    if skills:
        for skill in skills:
            print(f"  • {skill}")
        print(f"\nTotal: {len(skills)} global skills")
    else:
        print_warning("No global skills found.")

def list_project():
    """3.1.2 List Project Skills"""
    print_info(f"Listing Project Skills in: {PROJECT_SKILLS_DIR}")
    
    # Project skills might be directories (copied) or symlinks
    if not PROJECT_SKILLS_DIR.exists():
        print_warning("Project .agent/skills directory does not exist.")
        return

    items = sorted([x for x in PROJECT_SKILLS_DIR.iterdir()])
    skills_found = 0
    
    for item in items:
        if item.name.startswith('.'):
            continue
            
        is_symlink = item.is_symlink()
        is_dir = item.is_dir()
        
        if is_symlink:
            try:
                target = os.readlink(item)
                print(f"  • {item.name} \033[90m-> {target}\033[0m (Symlink)")
            except OSError:
                 print(f"  • {item.name} (Invalid Symlink)")
            skills_found += 1
        elif is_dir:
            print(f"  • {item.name} (Local Directory)")
            skills_found += 1
            
    print(f"\nTotal: {skills_found} installed skills")

def search_skills(query: str):
    """3.1.3 Search Skills"""
    print_info(f"Searching for '{query}' in Global Skills...")
    if not GLOBAL_SKILLS_REPO.exists():
        print_error("Global skills repository not found.")
        return

    all_skills = get_skill_names(GLOBAL_SKILLS_REPO)
    matches = []
    
    # Normalize query: lower case, remove symbols for 'fuzzy' check if needed
    # Requirement: ignore symbols like "-" in matching
    def normalize(s):
        return "".join(c for c in s if c.isalnum()).lower()
    
    norm_query = normalize(query)
    
    for skill in all_skills:
        # Standard case-insensitive search
        if query.lower() in skill.lower():
            matches.append(skill)
            continue
            
        # Fuzzy search (stripping symbols)
        if norm_query and norm_query in normalize(skill):
            matches.append(skill)

    # Dedup matches
    matches = sorted(list(set(matches)))

    if matches:
        for m in matches:
            print(f"  • {m}")
        print(f"\nFound {len(matches)} matches.")
    else:
        print_warning("No matching skills found.")

def install_skill(skill_name: str):
    """3.2.1 Install Skill"""
    source_path = GLOBAL_SKILLS_REPO / skill_name
    dest_path = PROJECT_SKILLS_DIR / skill_name

    # 1. Validation
    if not source_path.exists():
        print_error(f"Skill '{skill_name}' not found in global repo.")
        return

    if dest_path.exists():
        print_warning(f"Skill '{skill_name}' is already installed in this project.")
        if dest_path.is_symlink():
            print(f"    (It's a symlink to: {os.readlink(dest_path)})")
        return

    # 2. Ensure destination directory exists
    PROJECT_SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    # 3. Create Symlink
    print_info(f"Installing {skill_name}...")
    try:
        if os.name == 'nt':
            # Use PowerShell for reliable symlinking on Windows without requiring admin if Dev Mode is on,
            # or simply because it handles the specialized permission checks better sometimes.
            # But os.symlink is standard. Let's try os.symlink first.
            try:
                os.symlink(source_path, dest_path)
                print_success(f"Installed {skill_name}")
            except OSError as e:
                # Fallback to PowerShell as suggested in requirements
                cmd = [
                    "powershell", "-Command",
                    f"New-Item -Path '{dest_path}' -ItemType SymbolicLink -Value '{source_path}'"
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                     print_success(f"Installed {skill_name} (via PowerShell)")
                else:
                    print_error(f"Failed to install skill: {result.stderr}")
        else:
            os.symlink(source_path, dest_path)
            print_success(f"Installed {skill_name}")

    except Exception as e:
        print_error(f"Installation failed: {e}")

def uninstall_skill(skill_name: str):
    """3.2.2 Uninstall Skill"""
    target = PROJECT_SKILLS_DIR / skill_name

    if not target.exists() and not target.is_symlink(): # check is_symlink for broken links
        print_error(f"Skill '{skill_name}' is not installed in this project.")
        return

    try:
        if target.is_symlink() or target.is_file(): # Windows treated symlinked dirs as files sometimes in old pyt
            target.unlink()
            print_success(f"Uninstalled {skill_name} (Symlink removed)")
        elif target.is_dir():
            # Safety check: ensure we aren't deleting the global repo somehow
            # (Though path logic prevents this, explicit check is good)
            if GLOBAL_SKILLS_REPO in target.parents:
                 print_error("Safety Stop: Target seems to be inside Global Repo. Aborting.")
                 return
            
            # Ask for confirmation potentially, but requirements didn't specify interactive confirm.
            shutil.rmtree(target)
            print_success(f"Uninstalled {skill_name} (Directory removed)")
            
    except Exception as e:
        print_error(f"Uninstallation failed: {e}")

def parse_bundles() -> dict:
    """
    Parse BUNDLES.md to extract bundle names and their associated skills.
    Returns a dict: { 'Bundle Name': ['skill1', 'skill2', ...] }
    """
    if not BUNDLES_FILE.exists():
        return {}

    bundles = {}
    current_bundle = None
    
    with open(BUNDLES_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Detect Bundle Header (using ### as the delimiter for bundle names)
            if line.startswith('### '):
                # Example: ### 🚀 The "Essentials" Starter Pack
                raw_name = line.replace('###', '').strip()
                # Clean up name: remove emojis, quotes, excessive text
                # We'll keep the full name as the key for display, but index it nicely
                current_bundle = raw_name
                bundles[current_bundle] = []
                continue
            
            # Detect Skill Link
            # Example: - [`concise-planning`](../skills/concise-planning/): Description
            if current_bundle and line.startswith('- [`'):
                try:
                    # Extract link part: (../skills/concise-planning/)
                    start = line.find('(')
                    end = line.find(')')
                    if start != -1 and end != -1:
                        link = line[start+1:end]
                        # Extract skill name from link
                        # link looks like ../skills/concise-planning/ or just ../skills/concise-planning
                        parts = link.split('/')
                        # Filter out empty strings and '..' and 'skills'
                        valid_parts = [p for p in parts if p and p not in ('..', 'skills')]
                        if valid_parts:
                            skill_name = valid_parts[0]
                            bundles[current_bundle].append(skill_name)
                except Exception:
                    continue
                    
    # Filter out empty bundles
    return {k: v for k, v in bundles.items() if v}

def list_bundles():
    """3.3.1 List Bundles"""
    print_info(f"Listing Bundles from: {BUNDLES_FILE}")
    bundles = parse_bundles()
    
    if not bundles:
        print_warning("No bundles found or BUNDLES.md is missing.")
        return

    for bundle_name, skills in bundles.items():
        print(f"\n📦 \033[1m{bundle_name}\033[0m")
        print(f"   Contains {len(skills)} skills: {', '.join(skills[:5])}{'...' if len(skills)>5 else ''}")
        
    print(f"\nTotal: {len(bundles)} bundles available.")

def install_bundle(bundle_query: str):
    """3.3.2 Install Bundle"""
    bundles = parse_bundles()
    
    # Fuzzy match bundle name
    matches = [b for b in bundles.keys() if bundle_query.lower() in b.lower()]
    
    if not matches:
        print_error(f"No bundle found matching '{bundle_query}'")
        return
    
    if len(matches) > 1:
        print_warning(f"Multiple bundles match '{bundle_query}':")
        for m in matches:
            print(f"  • {m}")
        print("Please be more specific.")
        return
    
    target_bundle = matches[0]
    skills_to_install = bundles[target_bundle]
    
    print_info(f"Installing bundle: \033[1m{target_bundle}\033[0m ({len(skills_to_install)} skills)")
    
    success_count = 0
    for skill in skills_to_install:
        # Check if skill exists in listed global skills to avoid errors
        # (Though install_skill verifies this too, it's good to be noisy here)
        print(f"  Installing {skill}...")
        install_skill(skill)
        success_count += 1
        
    print_success(f"Bundle installation complete. processed {success_count} skills.")

def uninstall_bundle(bundle_query: str):
    """3.3.3 Uninstall Bundle"""
    bundles = parse_bundles()
    
    # Fuzzy match bundle name
    matches = [b for b in bundles.keys() if bundle_query.lower() in b.lower()]
    
    if not matches:
        print_error(f"No bundle found matching '{bundle_query}'")
        return
    
    if len(matches) > 1:
        print_warning(f"Multiple bundles match '{bundle_query}':")
        for m in matches:
            print(f"  • {m}")
        print("Please be more specific.")
        return
    
    target_bundle = matches[0]
    skills_to_remove = bundles[target_bundle]
    
    print_info(f"Uninstalling bundle: \033[1m{target_bundle}\033[0m ({len(skills_to_remove)} skills)")
    
    success_count = 0
    for skill in skills_to_remove:
        print(f"  Uninstalling {skill}...")
        uninstall_skill(skill)
        success_count += 1
        
    print_success(f"Bundle uninstallation complete. Processed {success_count} skills.")

def clear_all_skills(force: bool = False):
    """3.4 Clear All Skills"""
    if not PROJECT_SKILLS_DIR.exists():
        print_warning("Project skills directory not found.")
        return

    # Gather items to remove (symlinks and directories)
    items_to_remove = []
    for item in PROJECT_SKILLS_DIR.iterdir():
        if item.name.startswith('.'):
            continue
        items_to_remove.append(item.name)
    
    if not items_to_remove:
        print_info("No skills installed in this project.")
        return

    if not force:
        print_warning(f"This will remove {len(items_to_remove)} skills from the current project.")
        try:
            response = input("Are you sure you want to proceed? [y/N]: ").strip().lower()
            if response != 'y':
                print_info("Operation cancelled.")
                return
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return

    print_info(f"Removing {len(items_to_remove)} skills...")
    
    success_count = 0
    for skill_name in items_to_remove:
        target = PROJECT_SKILLS_DIR / skill_name
        try:
            if target.is_symlink() or target.is_file():
                target.unlink()
            elif target.is_dir():
                # Safety check (redundant but good practice)
                if GLOBAL_SKILLS_REPO in target.parents:
                     print_error(f"Skipping {skill_name}: Seems to be inside Global Repo.")
                     continue
                shutil.rmtree(target)
            
            print(f"  Removed {skill_name}")
            success_count += 1
        except Exception as e:
            print_error(f"Failed to remove {skill_name}: {e}")

    print_success(f"Cleared {success_count} skills.")

# --- Main CLI ---

def main():
    parser = argparse.ArgumentParser(description="Skills Manager CLI for Antigravity")
    subparsers = parser.add_subparsers(dest="noun", help="Available commands")

    # --- Skill Commands (Implicit/Top-level) ---
    
    # list (Project skills by default, global with flag)
    list_parser = subparsers.add_parser("list", help="List skills")
    list_parser.add_argument("-g", "--global", dest="is_global", action="store_true", help="List available global skills")
    
    # search
    search_parser = subparsers.add_parser("search", help="Search for global skills")
    search_parser.add_argument("query", help="Search term")

    # install
    install_parser = subparsers.add_parser("install", help="Install a skill to current project")
    install_parser.add_argument("skill_name", help="Name of the skill to install")

    # uninstall
    uninstall_parser = subparsers.add_parser("uninstall", help="Remove a skill from current project")
    uninstall_parser.add_argument("skill_name", help="Name of the skill to remove")

    # clear
    clear_parser = subparsers.add_parser("clear", help="Remove all skills from current project")
    clear_parser.add_argument("-f", "--force", action="store_true", help="Skip confirmation prompt")

    # --- Bundle Commands ---
    # Create a subparser for 'bundle'
    bundle_parser = subparsers.add_parser("bundle", help="Manage skill bundles")
    bundle_subparsers = bundle_parser.add_subparsers(dest="verb", help="Bundle actions")

    # bundle list
    bundle_subparsers.add_parser("list", help="List available skill bundles")
    
    # bundle install <name>
    bi_parser = bundle_subparsers.add_parser("install", help="Install all skills in a bundle")
    bi_parser.add_argument("bundle_name", help="Name (or part of name) of the bundle")

    # bundle uninstall <name>
    bu_parser = bundle_subparsers.add_parser("uninstall", help="Uninstall all skills in a bundle")
    bu_parser.add_argument("bundle_name", help="Name (or part of name) of the bundle")

    # Arguments parsing
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    # Routing
    if args.noun == "list":
        if args.is_global:
            list_global()
        else:
            list_project()
    elif args.noun == "search":
        search_skills(args.query)
    elif args.noun == "install":
        install_skill(args.skill_name)
    elif args.noun == "uninstall":
        uninstall_skill(args.skill_name)
    elif args.noun == "clear":
        clear_all_skills(args.force)
    elif args.noun == "bundle":
        if args.verb == "list":
            list_bundles()
        elif args.verb == "install":
            install_bundle(args.bundle_name)
        elif args.verb == "uninstall":
            uninstall_bundle(args.bundle_name)
        else:
            bundle_parser.print_help()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
