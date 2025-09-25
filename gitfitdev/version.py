"""
Version information for GitFit.dev
Auto-updated from version_config.py
"""

# Import from centralized version config
try:
    from ..version_config import BUILD_INFO
    __version__ = BUILD_INFO["version"]
    __release_date__ = BUILD_INFO["release_date"]
    __author__ = BUILD_INFO["author"]
    __github_repo__ = BUILD_INFO["github_repo"]
    __github_api_releases__ = BUILD_INFO["github_api_releases"]
except ImportError:
    # Fallback values for installed versions
    __version__ = "1.0.6"
    __release_date__ = "2025-09-25"
    __author__ = "GitFit.dev Team"
    __github_repo__ = "https://github.com/JozefJarosciak/GitFit.dev-public"
    __github_api_releases__ = "https://api.github.com/repos/JozefJarosciak/GitFit.dev-public/releases/latest"