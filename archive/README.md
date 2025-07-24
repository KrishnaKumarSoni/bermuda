# Archive Directory

This directory contains archived files that were moved from the main repository to reduce clutter and maintain focus on active development files.

## Archived on: July 23, 2025

## Directory Structure:

### 📂 `legacy-html/`
**Legacy Frontend Files**
- `app.html` (44KB) - Legacy main application file, replaced by `index.html`
- `app_old.html` (82KB) - Even older version with different UI approach

**Status**: Inactive - All functionality moved to `frontend/index.html`

### 📂 `test-files/` 
**Test Scripts & Results** (45 files, ~1MB total)
- Authentication tests (`auth_*.py`, `auth_*.json`)
- Chat functionality tests (`chat_*.py`, `comprehensive_chat_*.py`)
- Form creation tests (`comprehensive_form_*.py`, `corrected_form_*.py`) 
- API validation tests (`test_*.py`, `yaml_spec_validation_*.py`)
- Test results and summaries (`*results.json`, `*summary.py`)
- Test environment (`test_env/` - Python virtual environment)

**Status**: Historical test data - Tests may be outdated

### 📂 `spec-files/`
**YAML Specifications** (7 files, ~43KB total)
- `api-endpoints.yaml` - API endpoint specifications
- `data-models.yaml` - Data model definitions  
- `form-creator-xp.yaml` - Form creator experience spec
- `llm-prompts-and-chains.yaml` - LLM prompt configurations
- `product-overview.yaml` - Product specification
- `respondant-chat-xp.yaml` - Chat experience specification  
- `ui-components.yaml` - UI component specifications

**Status**: Design specifications - May be referenced for future development

### 📂 `debug-files/`
**Debug & Temporary Files** (5 files, ~1.8MB total)
- `debug_screenshot.png` - Debug screenshot
- `image.png` & `image copy.png` - Temporary images
- `deployment.log` - Build/deployment logs
- `run_local_server.py` - Local development server script

**Status**: Temporary files - Can be deleted if disk space needed

### 📂 `build-files/`
**Build System Files**
- `.vercel/` - Vercel deployment configuration (not used - using Firebase)
- `.bolt/` - Bolt.new configuration files  
- `src/` - Tailwind CSS source files (compiled to `frontend/style.css`)
- `cache-buster.txt` - Cache busting configuration (unused)
- `.vercelignore` - Vercel ignore file (not used)
- `requirements.txt` - Legacy requirements file (outdated deps vs `api/requirements.txt`)

**Status**: Build artifacts - May be needed for build system changes

### 📂 `unused-api/`
**Unused API Files** (2 files)
- `infer.py` - Duplicate inference endpoint (main.py routes to creator.py instead)
- `conversation.py` - Legacy conversation manager (imported but never called)

**Status**: Dead code - Safely removed from active codebase

---

## Recovery Instructions

If you need to restore any archived files:

1. **Legacy HTML**: Copy from `legacy-html/` to `frontend/` (⚠️ Will conflict with current `index.html`)
2. **Tests**: Copy from `test-files/` to root directory
3. **Specs**: Copy from `spec-files/` to root directory  
4. **Debug Files**: Copy from `debug-files/` to root directory
5. **Build Files**: Copy from `build-files/` to appropriate locations

## Disk Space Saved

- **Total archived**: ~3.2MB
- **Files archived**: 60+ files
- **Directories cleaned**: Python `__pycache__` directories removed

## Active Files Remaining

- `frontend/index.html` - Main application (current)
- `frontend/style.css` - Compiled Tailwind CSS
- `api/` - Backend Python code
- Configuration files (`.firebaserc`, `firebase.json`, `package.json`, etc.)
- Documentation (`README.md`, `CLAUDE.md`, `TEST_CASES.md`)