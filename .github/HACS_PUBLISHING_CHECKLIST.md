# HACS Publishing Checklist

This repository has been prepared for HACS publishing according to the official requirements.

## ✅ Completed Requirements

### Repository Files
- [x] **hacs.json** - Updated with:
  - `name` field (required)
  - `country: "AR"` field (Argentina-specific integration)
  - `content_in_root: false`
  - `filename: "argentina_smn"`
  - `render_readme: true`
  - `homeassistant: "2024.1.0"`

- [x] **manifest.json** - Updated with:
  - Full integration name: "SMN - Servicio Meteorológico Nacional"
  - Codeowners: `@catastrophicode`
  - Issue tracker URL
  - Valid version: `1.0.0` (SemVer format)
  - All required fields (domain, name, config_flow, documentation, etc.)

- [x] **README.md** - Comprehensive documentation with:
  - Installation instructions
  - Configuration guide
  - Features list
  - Example automations
  - Troubleshooting section

- [x] **INFO.md** - Created for HACS UI display

- [x] **LICENSE** - MIT License added

### GitHub Actions
- [x] **HACS Validation** (`.github/workflows/hacs.yml`)
  - Runs on push, pull_request, daily schedule, and manual trigger
  - Uses `hacs/action@main` with category: integration
  - Validates repository structure and requirements

- [x] **Hassfest Validation** (`.github/workflows/hassfest.yml`)
  - Runs on push, pull_request, daily schedule, and manual trigger
  - Uses `home-assistant/actions/hassfest@master`
  - Validates Home Assistant integration manifest

### Repository Structure
- [x] Single integration in `custom_components/argentina_smn/`
- [x] All required files in proper locations
- [x] No content in root (custom component in subdirectory)

## ⚠️ Manual Steps Required

### 1. Repository Settings on GitHub

You need to manually configure these settings on GitHub:

#### Add Repository Description
1. Go to repository settings on GitHub
2. Add description: "Home Assistant integration for Argentina's National Weather Service (SMN)"

#### Add Repository Topics
1. Go to repository settings on GitHub
2. Add these topics (see `.github/TOPICS.md`):
   - `home-assistant`
   - `hacs`
   - `weather`
   - `argentina`
   - `smn`
   - `integration`
   - `home-assistant-integration`
   - `homeassistant`
   - `weather-forecast`
   - `weather-alerts`

#### Enable Issues
1. Go to repository settings on GitHub
2. Ensure "Issues" is enabled under Features

### 2. Create a GitHub Release

HACS requires at least one GitHub release:

1. Go to "Releases" on GitHub
2. Click "Create a new release"
3. Create tag: `v1.0.0`
4. Release title: `v1.0.0 - Initial Release`
5. Add release notes describing the integration features
6. Publish release

**Important**: Use tags, not just releases. The tag name should match the version in `manifest.json`.

### 3. Submit to HACS Default Repository (Optional)

For inclusion in the default HACS store:

#### Prerequisites
1. **Brands Repository**: Submit to [home-assistant/brands](https://github.com/home-assistant/brands)
   - Fork the repository
   - Add integration assets (logo, icon)
   - Follow their contribution guidelines
   - Submit PR

2. **Repository Requirements** (all met ✅):
   - Valid manifest.json
   - hacs.json with name field
   - At least one release
   - Repository not archived
   - Country key set (AR)

#### Submission Process
1. Fork [hacs/default](https://github.com/hacs/default)
2. Add your repository to the appropriate JSON file
3. Submit pull request
4. Wait for review and approval

## 📋 Validation

### Test Locally
You can test HACS validation locally:

```bash
# Install HACS action
docker pull ghcr.io/hacs/action:latest

# Run validation
docker run --rm -v $(pwd):/github/workspace \
  ghcr.io/hacs/action:latest \
  --category integration
```

### GitHub Actions
Once you push changes, GitHub Actions will automatically:
- Validate HACS requirements
- Validate Home Assistant manifest
- Run on every push/PR
- Run daily to catch any deprecations

## 📚 Documentation References

All changes follow official HACS documentation:
- [HACS Publishing Guide](https://www.hacs.xyz/docs/publish/start/)
- [Integration Requirements](https://www.hacs.xyz/docs/publish/integration/)
- [Include in Default Store](https://www.hacs.xyz/docs/publish/include/)
- [GitHub Action](https://www.hacs.xyz/docs/publish/action/)
- [HACS Action Repository](https://github.com/hacs/action)

## 🎯 Next Steps

1. Merge this branch to main/master
2. Complete manual steps above (description, topics, issues)
3. Create v1.0.0 release
4. Test installation via HACS custom repository
5. (Optional) Submit to home-assistant/brands
6. (Optional) Submit to HACS default repository

## ✨ Testing Installation

Users can install from HACS as a custom repository:

1. Open HACS in Home Assistant
2. Go to Integrations
3. Click three dots (top right) → Custom repositories
4. Add URL: `https://github.com/catastrophicode/ha-ar-smn`
5. Category: Integration
6. Click Add

Once approved for default HACS, users can search for "SMN" directly in HACS.
