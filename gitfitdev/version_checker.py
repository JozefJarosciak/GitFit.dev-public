"""
Version checker for GitFit.dev - Check for updates from GitHub releases
"""
import json
import threading
import time
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from packaging import version as pkg_version

from . import version


class VersionChecker:
    """Handles version checking and update notifications"""

    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.current_version = version.__version__
        self.github_api_url = version.__github_api_releases__
        self.check_interval = 24 * 60 * 60  # 24 hours in seconds
        self.last_check_time = 0
        self.latest_version = None
        self.update_available = False
        self.update_callback = None
        self._checking = False

    def set_update_callback(self, callback):
        """Set callback function to be called when update is available"""
        self.update_callback = callback

    def should_check_for_updates(self):
        """Check if it's time to check for updates"""
        if self.config_manager:
            last_check = getattr(self.config_manager, 'last_version_check', 0)
            auto_check = getattr(self.config_manager, 'auto_check_updates', True)
            return auto_check and (time.time() - last_check) > self.check_interval
        return (time.time() - self.last_check_time) > self.check_interval

    def check_for_updates_async(self):
        """Start async version check"""
        if not self._checking and self.should_check_for_updates():
            self._checking = True
            thread = threading.Thread(target=self._check_for_updates_worker, daemon=True)
            thread.start()

    def _check_for_updates_worker(self):
        """Background worker to check for updates"""
        try:
            self.check_for_updates()
        finally:
            self._checking = False

    def check_for_updates(self):
        """Check GitHub API for the latest release"""
        try:
            # Create request with User-Agent header
            req = Request(self.github_api_url)
            req.add_header('User-Agent', f'GitFit.dev/{self.current_version}')
            req.add_header('Accept', 'application/vnd.github.v3+json')

            with urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())

            latest_version = data.get('tag_name', '').lstrip('v')

            if latest_version:
                self.latest_version = latest_version

                # Compare versions using packaging library for proper semantic versioning
                try:
                    current_ver = pkg_version.parse(self.current_version)
                    latest_ver = pkg_version.parse(latest_version)

                    self.update_available = latest_ver > current_ver

                    # Store last check time
                    if self.config_manager:
                        self.config_manager.last_version_check = time.time()
                        self.config_manager.latest_known_version = latest_version

                    self.last_check_time = time.time()

                    # Call update callback if update available
                    if self.update_available and self.update_callback:
                        release_info = {
                            'version': latest_version,
                            'url': data.get('html_url', ''),
                            'download_url': self._get_download_url(data),
                            'release_notes': data.get('body', ''),
                            'published_at': data.get('published_at', '')
                        }
                        self.update_callback(release_info)

                except Exception as e:
                    print(f"Error parsing version numbers: {e}")

        except (URLError, HTTPError, json.JSONDecodeError) as e:
            print(f"Error checking for updates: {e}")
        except Exception as e:
            print(f"Unexpected error during update check: {e}")

    def _get_download_url(self, release_data):
        """Extract appropriate download URL from release assets"""
        import platform

        assets = release_data.get('assets', [])
        system = platform.system().lower()

        # Priority order for different platforms
        platform_patterns = {
            'windows': ['.exe', 'windows', 'win'],
            'darwin': ['.dmg', '.app', 'macos', 'mac'],
            'linux': ['.AppImage', 'linux']
        }

        patterns = platform_patterns.get(system, [])

        # Find best matching asset
        for pattern in patterns:
            for asset in assets:
                if pattern.lower() in asset.get('name', '').lower():
                    return asset.get('browser_download_url', '')

        # Fallback to first asset or release page
        if assets:
            return assets[0].get('browser_download_url', release_data.get('html_url', ''))

        return release_data.get('html_url', '')

    def get_update_info(self):
        """Get information about available update"""
        return {
            'current_version': self.current_version,
            'latest_version': self.latest_version,
            'update_available': self.update_available,
            'last_check': self.last_check_time
        }

    def force_check(self):
        """Force an immediate version check"""
        self.last_check_time = 0
        if self.config_manager:
            self.config_manager.last_version_check = 0
        self.check_for_updates_async()

    def disable_auto_check(self):
        """Disable automatic update checking"""
        if self.config_manager:
            self.config_manager.auto_check_updates = False

    def enable_auto_check(self):
        """Enable automatic update checking"""
        if self.config_manager:
            self.config_manager.auto_check_updates = True