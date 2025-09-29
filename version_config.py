"""
Centralized version configuration for GitFit.dev
This is the SINGLE source of truth for version information
"""

# MAIN VERSION - UPDATE ONLY THIS LINE FOR NEW RELEASES
VERSION = "1.0.0"

# Auto-generated from main version (don't edit these)
VERSION_TUPLE = tuple(map(int, VERSION.split('.')))
VERSION_WITH_V = f"v{VERSION}"
RELEASE_DATE = "2025-09-28"

# Build information
BUILD_INFO = {
    "version": VERSION,
    "version_tuple": VERSION_TUPLE,
    "version_with_v": VERSION_WITH_V,
    "release_date": RELEASE_DATE,
    "author": "GitFit.dev Team",
    "github_repo": "https://github.com/JozefJarosciak/GitFit.dev-public",
    "github_api_releases": "https://api.github.com/repos/JozefJarosciak/GitFit.dev-public/releases/latest"
}

# Export for easy access
__version__ = VERSION
__release_date__ = RELEASE_DATE
__github_repo__ = BUILD_INFO["github_repo"]
__github_api_releases__ = BUILD_INFO["github_api_releases"]