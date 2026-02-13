import pytest
from pathlib import Path
import os
import shutil
import sys
import importlib
import json

# Add project root to sys.path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import skills_manager

@pytest.fixture
def mock_dirs(tmp_path, monkeypatch):
    """
    Sets up a temporary directory structure mimicking the real environment.
    """
    # 1. Mock Global Repo
    global_repo = tmp_path / "global_skills"
    global_repo.mkdir()
    
    # Create some dummy skills
    (global_repo / "skill-alpha").mkdir()
    (global_repo / "skill-beta").mkdir()
    (global_repo / "complex-skill-gamma").mkdir()
    (global_repo / "writing-plans").mkdir() # For fuzzy search test
    (global_repo / "hidden-skill").mkdir() # Should be ignored if starts with .? Script says "not d.name.startswith('.')"
    (global_repo / ".hidden-dir").mkdir()

    # 2. Mock Project Repo
    project_repo = tmp_path / "project_skills"
    project_repo.mkdir()

    # 3. Mock Bundles File
    bundles_file = tmp_path / "BUNDLES.md"
    bundles_content = """
# Bundles
### 🚀 The "Starter" Pack
- [`skill-alpha`](../skills/skill-alpha/)
- [`skill-beta`](../skills/skill-beta/)

### 🔧 The "Complex" Pack
- [`complex-skill-gamma`](../skills/complex-skill-gamma/)
"""
    bundles_file.write_text(bundles_content, encoding="utf-8")

    # 4. Mock Workflows File
    workflows_file = tmp_path / "workflows.json"
    workflows_content = {
        "workflows": [
            {
                "id": "test-workflow",
                "name": "Test Workflow",
                "description": "A test workflow",
                "steps": [
                    {
                        "title": "Step 1",
                        "recommendedSkills": ["skill-alpha", "skill-beta"]
                    }
                ]
            }
        ]
    }
    workflows_file.write_text(json.dumps(workflows_content), encoding="utf-8")

    # 5. Patch the module-level constants
    monkeypatch.setattr(skills_manager, "GLOBAL_SKILLS_REPO", global_repo)
    monkeypatch.setattr(skills_manager, "PROJECT_SKILLS_DIR", project_repo)
    monkeypatch.setattr(skills_manager, "BUNDLES_FILE", bundles_file)
    monkeypatch.setattr(skills_manager, "WORKFLOWS_FILE", workflows_file)

    return global_repo, project_repo, bundles_file, workflows_file

def test_list_global(mock_dirs, capsys):
    skills_manager.list_global()
    captured = capsys.readouterr()
    
    assert "skill-alpha" in captured.out
    assert "skill-beta" in captured.out
    assert "complex-skill-gamma" in captured.out
    assert "hidden-dir" not in captured.out

def test_search_skills_fuzzy(mock_dirs, capsys):
    # Search for "writingplans" (should match "writing-plans")
    skills_manager.search_skills("writingplans")
    captured = capsys.readouterr()
    assert "writing-plans" in captured.out
    assert "Found 1 matches" in captured.out

    # Search for "complex_skill" (should match "complex-skill-gamma")
    skills_manager.search_skills("complex_skill")
    captured = capsys.readouterr()
    assert "complex-skill-gamma" in captured.out

def test_install_skill(mock_dirs):
    _, project_repo, _, _ = mock_dirs
    
    # Install
    skills_manager.install_skill("skill-alpha")
    
    installed_path = project_repo / "skill-alpha"
    assert installed_path.exists()
    assert installed_path.is_symlink()
    
    # Verify target
    target = os.readlink(installed_path)
    # On Windows, readlink might return absolute path, let's just check existence
    assert Path(target).name == "skill-alpha"

def test_install_nonexistent_skill(mock_dirs, capsys):
    skills_manager.install_skill("fake-skill")
    captured = capsys.readouterr()
    assert "not found" in captured.out

def test_uninstall_skill(mock_dirs, capsys):
    _, project_repo, _, _ = mock_dirs
    
    # Install first
    skills_manager.install_skill("skill-beta")
    assert (project_repo / "skill-beta").exists()

    # Uninstall
    skills_manager.uninstall_skill("skill-beta")
    captured = capsys.readouterr()
    
    assert not (project_repo / "skill-beta").exists()
    assert "Uninstalled skill-beta" in captured.out

def test_parse_bundles(mock_dirs):
    bundles = skills_manager.parse_bundles()
    
    assert '🚀 The "Starter" Pack' in bundles
    starter_skills = bundles['🚀 The "Starter" Pack']
    assert "skill-alpha" in starter_skills
    assert "skill-beta" in starter_skills
    assert "complex-skill-gamma" not in starter_skills

    assert '🔧 The "Complex" Pack' in bundles
    complex_skills = bundles['🔧 The "Complex" Pack']
    assert "complex-skill-gamma" in complex_skills

def test_install_bundle(mock_dirs, capsys):
    _, project_repo, _, _ = mock_dirs
    
    # Install Bundle by partial name
    skills_manager.install_bundle("Starter")
    
    assert (project_repo / "skill-alpha").exists()
    assert (project_repo / "skill-beta").exists()
    assert not (project_repo / "complex-skill-gamma").exists()

def test_uninstall_bundle(mock_dirs):
    _, project_repo, _, _ = mock_dirs
    
    # Setup: Install all skills manually first
    skills_manager.install_skill("skill-alpha")
    skills_manager.install_skill("skill-beta")
    
    assert (project_repo / "skill-alpha").exists()
    
    # Uninstall Bundle
    skills_manager.uninstall_bundle("Starter")
    
    assert not (project_repo / "skill-alpha").exists()
    assert not (project_repo / "skill-beta").exists()

def test_clear_all_skills(mock_dirs, monkeypatch):
    _, project_repo, _, _ = mock_dirs
    
    # Setup
    skills_manager.install_skill("skill-alpha")
    skills_manager.install_skill("complex-skill-gamma")
    
    assert len(list(project_repo.iterdir())) == 2
    
    # Mock input to confirm 'y'
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    
    skills_manager.clear_all_skills(force=False)
    
    assert len(list(project_repo.iterdir())) == 0

def test_clear_all_skills_force(mock_dirs):
    _, project_repo, _, _ = mock_dirs
    
    # Setup
    skills_manager.install_skill("skill-alpha")
    
    # Clear with force=True (no input needed)
    skills_manager.clear_all_skills(force=True)
    
    assert len(list(project_repo.iterdir())) == 0

def test_parse_workflows(mock_dirs):
    workflows = skills_manager.parse_workflows()
    assert "test-workflow" in workflows
    assert workflows["test-workflow"]["name"] == "Test Workflow"

def test_install_workflow(mock_dirs):
    _, project_repo, _, _ = mock_dirs
    
    # Install workflow
    skills_manager.install_workflow("test-workflow")
    
    assert (project_repo / "skill-alpha").exists()
    assert (project_repo / "skill-beta").exists()
