# Release Process

This document describes how to create releases for refib.

## Prerequisites

1. Ensure you have a PyPI API token set up as a GitHub secret named `PYPI_API_TOKEN`
2. Make sure all tests pass on the main branch
3. Update the version in `setup.py`
4. Update the `CHANGELOG.rst` with release notes

## Creating a Release

### Option 1: Using GitHub CLI

```bash
# Create and push a tag
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0

# Create GitHub release
gh release create v0.1.0 \
  --title "v0.1.0" \
  --notes "See CHANGELOG.rst for details"
```

### Option 2: Using GitHub Web Interface

1. Go to https://github.com/uncorrelited/refib/releases
2. Click "Create a new release"
3. Choose "Create a new tag" and enter `v0.1.0` (replace with your version)
4. Set the release title to `v0.1.0`
5. Copy the relevant section from `CHANGELOG.rst` into the release description
6. Click "Publish release"

## What Happens Next

When you create a GitHub release, the `publish.yml` workflow automatically:
1. Builds the Python package
2. Uploads it to PyPI using the configured API token

## Creating Your First Release

Since v0.1.0 is already on PyPI, create a GitHub release for it:

```bash
git tag -a v0.1.0 -m "Release version 0.1.0" 
git push origin v0.1.0
gh release create v0.1.0 --title "v0.1.0" --notes "Initial release. See CHANGELOG.rst for details"
```

This will make your GitHub repository show:
- ✅ Releases: 1 release published
- ✅ Packages: Published to PyPI