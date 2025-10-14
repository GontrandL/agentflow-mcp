# File Organization Guide: Best Practices for AI-Generated Codebases

## Executive Summary

This guide provides comprehensive best practices for organizing files in AI-generated codebases, preventing file explosion, and maintaining a clean, scalable project structure.

**Key Metrics:**
- Industry standard: **20-50 files per directory maximum**
- Python modules: **500 lines per file maximum** (SPARC methodology)
- Documentation: **Single source of truth** with automated generation
- File size limit: **500KB per file** (excluding binaries)

---

## 1. Directory Structure Best Practices

### 1.1 Feature-Based Organization (Recommended for Large Projects)

```
project/
├── src/                          # Source code
│   ├── features/                 # Feature-based modules
│   │   ├── authentication/       # Self-contained feature
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── services.py
│   │   │   ├── routes.py
│   │   │   └── tests/
│   │   ├── dashboard/
│   │   └── api/
│   ├── shared/                   # Shared utilities
│   │   ├── utils/
│   │   ├── constants/
│   │   └── types/
│   └── config/                   # Configuration
├── tests/                        # Test files (mirror src/)
├── docs/                         # Documentation
│   ├── guides/                   # User guides
│   ├── api/                      # API documentation
│   └── architecture/             # System design docs
├── scripts/                      # Build/deployment scripts
├── assets/                       # Static assets
│   ├── images/
│   └── data/
├── archive/                      # OLD/deprecated code
└── .claudecode/                  # AI assistant rules
```

### 1.2 Package-Based Organization (Monorepo)

```
monorepo/
├── apps/                         # Applications
│   ├── web/                      # Web application
│   ├── api/                      # API service
│   └── mobile/                   # Mobile app
├── packages/                     # Shared libraries
│   ├── ui-components/
│   ├── data-models/
│   └── utilities/
├── tools/                        # Build tools
├── docs/                         # Documentation
└── configs/                      # Shared configs
```

### 1.3 Domain-Driven Design (DDD)

```
project/
├── domains/                      # Business domains
│   ├── billing/
│   │   ├── entities/
│   │   ├── services/
│   │   ├── repositories/
│   │   └── interfaces/
│   ├── users/
│   └── products/
├── infrastructure/               # Technical infrastructure
│   ├── database/
│   ├── cache/
│   └── messaging/
└── application/                  # Application layer
    ├── commands/
    ├── queries/
    └── handlers/
```

---

## 2. File Naming Conventions

### 2.1 Python Files

```python
# Modules: snake_case
user_authentication.py
data_processor.py
api_client.py

# Tests: test_ prefix or _test suffix
test_user_authentication.py
user_authentication_test.py

# Private modules: _ prefix
_internal_helpers.py
_cache_utils.py

# Constants: UPPERCASE
CONSTANTS.py
CONFIG.py
```

### 2.2 Documentation Files

```markdown
# Primary docs: UPPERCASE.md
README.md
CHANGELOG.md
CONTRIBUTING.md
LICENSE.md

# Feature docs: kebab-case.md
user-authentication.md
api-integration.md
deployment-guide.md

# Architecture docs: architecture/*.md
architecture/system-design.md
architecture/data-flow.md
```

### 2.3 Configuration Files

```
# Root config files
.env.example
.gitignore
pyproject.toml
docker-compose.yml

# Feature configs: feature.config.*
auth.config.yaml
database.config.json
```

---

## 3. File Size and Count Limits

### 3.1 Hard Limits (Enforced by Pre-Commit Hooks)

| Category | Limit | Rationale |
|----------|-------|-----------|
| **Python files** | 500 lines | SPARC methodology, maintainability |
| **Markdown files** | 1000 lines | Readability, single responsibility |
| **JSON/YAML** | 500KB | Performance, parsing speed |
| **Images** | 1MB | Repository size, git performance |
| **Binary files** | 5MB | Block accidental large commits |

### 3.2 Soft Limits (Warnings)

| Category | Limit | Action |
|----------|-------|--------|
| **Files per directory** | 50 | Suggest subdirectories |
| **Markdown files in root** | 10 | Move to docs/ |
| **Python module depth** | 3 levels | Flatten structure |
| **Total project files** | 500 | Review for consolidation |

### 3.3 Counting Rules

**EXCLUDE from counts:**
- `.venv/`, `node_modules/`, `venv/`
- `.git/`, `.pytest_cache/`, `__pycache__/`
- `build/`, `dist/`, `.egg-info/`

**INCLUDE in counts:**
- `src/`, `lib/`, `app/`, `features/`
- `tests/`, `docs/`, `scripts/`
- Root configuration files

---

## 4. Documentation Organization

### 4.1 Single Source of Truth Principle

**Problem:** Duplicate documentation leads to:
- Conflicting information
- Maintenance overhead
- Developer confusion

**Solution:** Generate documentation from code + structured sources

```yaml
Documentation Sources:
  Code:
    - Docstrings (Python)
    - Type hints
    - Inline comments

  Structured Docs:
    - README.md (overview)
    - docs/guides/ (tutorials)
    - docs/api/ (auto-generated)
    - CHANGELOG.md (auto-generated from commits)

  Generated Outputs:
    - Static site (MkDocs/Docusaurus)
    - API reference (Sphinx/mkdocstrings)
    - README badges (shields.io)
```

### 4.2 Documentation Hierarchy

```
docs/
├── index.md                      # Landing page
├── getting-started/              # Onboarding
│   ├── installation.md
│   ├── quickstart.md
│   └── configuration.md
├── guides/                       # How-to guides
│   ├── authentication.md
│   ├── deployment.md
│   └── troubleshooting.md
├── api/                          # Auto-generated API docs
│   ├── index.md
│   ├── authentication.md
│   └── endpoints.md
├── architecture/                 # System design
│   ├── overview.md
│   ├── data-flow.md
│   └── decisions/                # ADRs (Architecture Decision Records)
│       ├── 001-database-choice.md
│       └── 002-auth-strategy.md
└── reference/                    # Reference materials
    ├── glossary.md
    └── faq.md
```

### 4.3 Automated Documentation Tools

**MkDocs (Python Projects)**
```yaml
# mkdocs.yml
site_name: Project Name
theme: material
plugins:
  - search
  - mkdocstrings:  # Auto-generate API docs from docstrings
      handlers:
        python:
          paths: [src]
  - git-revision-date-localized  # Show last update dates
nav:
  - Home: index.md
  - Getting Started: getting-started/
  - Guides: guides/
  - API Reference: api/
```

**Docusaurus (React Projects)**
```javascript
// docusaurus.config.js
module.exports = {
  title: 'Project Name',
  tagline: 'Tagline',
  plugins: [
    'docusaurus-plugin-typedoc',  // Auto-generate from TypeScript
    '@docusaurus/plugin-content-docs',
  ],
};
```

---

## 5. Archival Strategies

### 5.1 What to Archive

**Archive when:**
- Code not used in 90+ days
- Superseded by new implementation
- Experimental features not adopted
- Old migration scripts (post-migration)
- Outdated documentation

**Delete when:**
- Temporary files older than 7 days
- Test outputs/logs older than 30 days
- Duplicate files (identical content)
- Auto-generated files in git

### 5.2 Archive Structure

```
archive/
├── YYYY-MM/                      # Archived by month
│   ├── old-feature/
│   │   ├── ARCHIVED_README.md    # Why archived, alternatives
│   │   └── code/
│   └── deprecated-scripts/
└── INDEX.md                      # Archive manifest
```

### 5.3 Archive Metadata

```markdown
# ARCHIVED_README.md

## Archive Information
- **Archived Date:** 2025-10-12
- **Archived By:** Claude Code Agent
- **Reason:** Superseded by new authentication system
- **Replacement:** src/features/authentication/

## Original Purpose
[Description of what this code did]

## Dependencies
[What depended on this code]

## Migration Path
[How to migrate to new system]
```

---

## 6. AI-Generated Code Management

### 6.1 Tracking AI-Generated Files

**Add metadata to AI-generated files:**

```python
"""
User Authentication Service

This module handles user authentication and session management.

Generated: 2025-10-12 by Claude Code
Last Modified: 2025-10-15 by Human Developer
AI Confidence: High
Reviewed: Yes (John Doe, 2025-10-13)
"""
```

**Create AI attribution file:**

```yaml
# .ai-attribution.yaml
files:
  - path: src/features/auth/service.py
    generated_by: Claude Code
    generated_date: 2025-10-12
    reviewed: true
    reviewer: John Doe
    review_date: 2025-10-13
    modifications: Minor bug fixes

  - path: src/features/dashboard/routes.py
    generated_by: Claude Code
    generated_date: 2025-10-15
    reviewed: false
    notes: Needs testing
```

### 6.2 Quality Control for AI-Generated Code

```python
# Pre-commit hook: check_ai_code.py
def validate_ai_generated_file(filepath):
    """Validate AI-generated code meets standards."""
    checks = [
        has_docstring(),
        has_type_hints(),
        has_tests(),
        passes_linting(),
        under_line_limit(500),
        has_human_review(),
    ]
    return all(checks)
```

### 6.3 AI Code Review Checklist

- [ ] **Documentation:** Docstrings, type hints, comments
- [ ] **Tests:** Unit tests, integration tests
- [ ] **Security:** No hardcoded secrets, input validation
- [ ] **Performance:** No obvious bottlenecks
- [ ] **Style:** Follows project conventions
- [ ] **Dependencies:** Uses approved libraries only
- [ ] **Error Handling:** Proper exception handling
- [ ] **Human Review:** Code reviewed by developer

---

## 7. Safeguards and Automation

### 7.1 Pre-Commit Hooks

**File Management Hooks:**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-added-large-files
        args: ['--maxkb=500']
      - id: check-merge-conflict
      - id: trailing-whitespace
      - id: end-of-file-fixer

  - repo: local
    hooks:
      - id: file-count-check
        name: Check file count per directory
        entry: python scripts/check_file_count.py
        language: python
        pass_filenames: false

      - id: file-organization-check
        name: Validate file organization
        entry: python scripts/check_file_organization.py
        language: python
        pass_filenames: false

      - id: python-line-count
        name: Check Python file line count
        entry: python scripts/check_line_count.py --max-lines=500
        language: python
        files: \.py$
```

### 7.2 GitHub Actions Workflow

```yaml
# .github/workflows/file-management.yml
name: File Management

on: [push, pull_request]

jobs:
  file-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Check file explosion
        run: |
          python scripts/FILE_MANAGEMENT_SYSTEM.py check_file_explosion

      - name: Generate file manifest
        run: |
          python scripts/FILE_MANAGEMENT_SYSTEM.py generate_file_manifest

      - name: Check for consolidation opportunities
        run: |
          python scripts/FILE_MANAGEMENT_SYSTEM.py suggest_consolidation
```

### 7.3 Automated Cleanup Scripts

**Weekly Cleanup (Cron Job):**

```bash
#!/bin/bash
# scripts/weekly_cleanup.sh

# Archive old files
python scripts/FILE_MANAGEMENT_SYSTEM.py archive_old_files --age=90

# Delete temporary files
find . -name "*.tmp" -mtime +7 -delete
find . -name "*.log" -mtime +30 -delete

# Generate updated manifest
python scripts/FILE_MANAGEMENT_SYSTEM.py generate_file_manifest

# Commit changes
git add archive/ PROJECT_FILE_INDEX.md
git commit -m "chore: weekly file cleanup and archival"
```

---

## 8. File Lifecycle Management

### 8.1 File Creation Workflow

```
1. AI suggests file → 2. Validate location → 3. Check limits → 4. Create file → 5. Add metadata → 6. Generate docs → 7. Commit
```

**Validation Checklist:**
- [ ] File in correct directory
- [ ] Filename follows conventions
- [ ] Size under limits
- [ ] Directory file count under 50
- [ ] No duplicates
- [ ] Proper documentation
- [ ] Tests included (for code)

### 8.2 File Modification Workflow

```
1. Modify file → 2. Run pre-commit → 3. Update docs → 4. Update manifest → 5. Commit
```

### 8.3 File Deletion Workflow

```
1. Identify unused file → 2. Check dependencies → 3. Archive (don't delete) → 4. Update docs → 5. Update manifest → 6. Commit
```

---

## 9. Monitoring and Metrics

### 9.1 Key Metrics to Track

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| **Total files** | < 500 | > 750 |
| **Files per directory** | < 50 | > 75 |
| **Python files > 500 lines** | 0 | > 5 |
| **Markdown files in root** | < 10 | > 15 |
| **Duplicate files** | 0 | > 3 |
| **Files without tests** | < 10% | > 25% |
| **AI-generated unreviewed** | < 20% | > 50% |

### 9.2 Weekly Health Check

```bash
# scripts/weekly_health_check.sh

echo "=== File Management Health Check ==="

# Count files by type
echo "Python files: $(find src -name '*.py' | wc -l)"
echo "Markdown files: $(find . -maxdepth 1 -name '*.md' | wc -l)"
echo "Total project files: $(find . -type f -not -path '*/\.*' | wc -l)"

# Check for violations
python scripts/FILE_MANAGEMENT_SYSTEM.py health_check

# Generate report
python scripts/FILE_MANAGEMENT_SYSTEM.py generate_report > reports/file-health-$(date +%Y%m%d).md
```

---

## 10. Migration and Consolidation

### 10.1 Consolidation Triggers

**When to consolidate:**
- Multiple files < 100 lines with same purpose
- Duplicate logic across files
- Files per directory > 50
- Total markdown files > 50
- Overlapping documentation

### 10.2 Consolidation Strategies

**Strategy 1: Merge Small Files**
```python
# Before: 5 files with utilities
utils/string_utils.py    (50 lines)
utils/date_utils.py      (75 lines)
utils/file_utils.py      (60 lines)
utils/validation.py      (80 lines)
utils/formatting.py      (40 lines)

# After: 1 consolidated file
utils/common.py          (305 lines, well-organized sections)
```

**Strategy 2: Create Sub-packages**
```python
# Before: 60 files in features/
features/auth1.py
features/auth2.py
...
features/user60.py

# After: Organized sub-packages
features/
├── auth/
│   ├── __init__.py
│   ├── login.py
│   └── session.py
├── users/
│   ├── __init__.py
│   ├── profile.py
│   └── settings.py
└── admin/
```

**Strategy 3: Documentation Consolidation**
```markdown
# Before: 8 separate docs
DASHBOARD_SUMMARY.md
DASHBOARD_QUICKSTART.md
DASHBOARD_API.md
DASHBOARD_DEPLOYMENT.md
...

# After: Single comprehensive doc
docs/dashboard/
├── index.md           (overview + quickstart)
├── api-reference.md   (API docs)
└── deployment.md      (deployment guide)
```

---

## 11. Tools and Resources

### 11.1 Recommended Tools

**Python:**
- `ruff` - Fast linter and formatter
- `mypy` - Type checking
- `pytest` - Testing framework
- `mkdocs` - Documentation generator
- `pre-commit` - Git hook manager

**File Management:**
- `fd` - Fast file finder (alternative to find)
- `rg` (ripgrep) - Fast grep alternative
- `tree` - Directory visualization
- `ncdu` - Disk usage analyzer

**Documentation:**
- MkDocs Material theme
- mkdocstrings (Python API docs)
- Docusaurus (React projects)
- Sphinx (advanced Python docs)

### 11.2 Integration Examples

**Package Manager Integration:**
```toml
# pyproject.toml
[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W"]
exclude = [".venv", "archive"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
exclude = ['archive/']

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
```

---

## 12. Best Practices Checklist

### Daily
- [ ] Run pre-commit hooks on all commits
- [ ] Keep root directory to < 15 files
- [ ] Document AI-generated code

### Weekly
- [ ] Run health check script
- [ ] Review file count metrics
- [ ] Update PROJECT_FILE_INDEX.md
- [ ] Archive unused files

### Monthly
- [ ] Full consolidation review
- [ ] Update documentation
- [ ] Clean up test outputs
- [ ] Review AI attribution logs

### Quarterly
- [ ] Major refactoring/reorganization if needed
- [ ] Update file organization rules
- [ ] Team training on conventions
- [ ] Tool/process improvements

---

## 13. Common Anti-Patterns to Avoid

### 13.1 File Organization Anti-Patterns

❌ **Anti-Pattern: Flat Structure**
```
project/
├── file1.py
├── file2.py
├── file3.py
... (100+ files)
```
✅ **Solution: Hierarchical Organization**

❌ **Anti-Pattern: Deep Nesting**
```
src/app/modules/features/components/common/utils/helpers/
```
✅ **Solution: Max 3 levels deep**

❌ **Anti-Pattern: Mixed Concerns**
```
src/
├── auth.py
├── auth_test.py
├── user.py
├── user_test.py
├── dashboard.py
```
✅ **Solution: Separate by concern (src/, tests/)**

### 13.2 Documentation Anti-Patterns

❌ **Anti-Pattern: Documentation Explosion**
```
README.md
README_v2.md
README_FINAL.md
README_DASHBOARD.md
DASHBOARD_QUICKSTART.md
DASHBOARD_SUMMARY.md
DASHBOARD_GUIDE.md
```
✅ **Solution: Consolidated docs/ directory**

❌ **Anti-Pattern: Outdated Docs**
- Documentation not updated with code
- Conflicting information in different files

✅ **Solution: Auto-generated docs from code**

### 13.3 AI Code Anti-Patterns

❌ **Anti-Pattern: No Human Review**
- Committing AI code without review
- No validation or testing

✅ **Solution: Mandatory review checklist**

❌ **Anti-Pattern: No Attribution**
- Can't tell AI vs human code
- No audit trail

✅ **Solution: AI attribution metadata**

---

## 14. Emergency File Explosion Response

**If you find yourself with 1000+ files:**

### Phase 1: Assessment (1 hour)
```bash
# Run analysis
python scripts/FILE_MANAGEMENT_SYSTEM.py analyze_explosion

# Generate reports
python scripts/FILE_MANAGEMENT_SYSTEM.py generate_report
python scripts/FILE_MANAGEMENT_SYSTEM.py suggest_consolidation
```

### Phase 2: Quick Wins (2 hours)
1. Archive old/unused files
2. Delete temporary files
3. Consolidate small files
4. Move docs to docs/

### Phase 3: Restructuring (1 day)
1. Implement feature-based structure
2. Create sub-packages
3. Consolidate documentation
4. Update import paths

### Phase 4: Prevention (ongoing)
1. Install pre-commit hooks
2. Set up CI/CD checks
3. Weekly health checks
4. Team training

---

## Conclusion

**Key Takeaways:**

1. **Structure matters:** Use feature-based or package-based organization
2. **Limits prevent chaos:** Enforce 50 files/directory, 500 lines/file
3. **Automate everything:** Pre-commit hooks, CI/CD, cleanup scripts
4. **Single source of truth:** Generate docs from code
5. **Track AI code:** Attribution, review, validation
6. **Monitor health:** Weekly checks, quarterly reviews

**Success Metrics:**
- Files per directory: < 50
- Python files: < 500 lines
- Documentation: Single source, auto-generated
- AI code: 100% reviewed
- Total files: < 500 (excluding dependencies)

---

**Version:** 1.0
**Last Updated:** 2025-10-12
**Maintained by:** Claude Code Research Agent
