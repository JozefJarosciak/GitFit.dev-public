// Theme toggle functionality
class ThemeManager {
    constructor() {
        this.themeToggle = document.getElementById('themeToggle');
        this.themeIcon = this.themeToggle.querySelector('.theme-icon');
        this.body = document.body;

        // Check for saved theme preference or default to dark
        this.currentTheme = localStorage.getItem('theme') || 'dark';
        this.applyTheme(this.currentTheme);

        this.bindEvents();
    }

    bindEvents() {
        this.themeToggle.addEventListener('click', () => this.toggleTheme());

        // Add keyboard support
        this.themeToggle.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.toggleTheme();
            }
        });

        // Make theme toggle focusable
        this.themeToggle.setAttribute('tabindex', '0');
        this.themeToggle.setAttribute('aria-label', 'Toggle theme');
    }

    toggleTheme() {
        this.currentTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.applyTheme(this.currentTheme);
        localStorage.setItem('theme', this.currentTheme);
    }

    applyTheme(theme) {
        if (theme === 'light') {
            this.body.classList.remove('dark-theme');
            this.body.classList.add('light-theme');
            this.themeIcon.textContent = '☀️';
            this.themeToggle.setAttribute('aria-label', 'Switch to dark theme');
        } else {
            this.body.classList.remove('light-theme');
            this.body.classList.add('dark-theme');
            this.themeIcon.textContent = '🌙';
            this.themeToggle.setAttribute('aria-label', 'Switch to light theme');
        }
    }
}

// Download functionality
class DownloadManager {
    constructor() {
        console.log('DownloadManager initializing...');
        this.downloadButtons = {
            windows: document.getElementById('downloadWindows'),
            mac: document.getElementById('downloadMac'),
            linux: document.getElementById('downloadLinux')
        };

        // Debug: Check if buttons were found
        console.log('Download buttons found:', {
            windows: !!this.downloadButtons.windows,
            mac: !!this.downloadButtons.mac,
            linux: !!this.downloadButtons.linux
        });

        // GitHub release URLs - dynamically updated from API
        this.downloadUrls = {
            windows: 'https://github.com/JozefJarosciak/GitFit.dev-public/releases/latest',
            mac: 'https://github.com/JozefJarosciak/GitFit.dev-public/releases/latest',
            linux: 'https://github.com/JozefJarosciak/GitFit.dev-public/releases/latest'
        };

        this.bindEvents();
        this.checkAvailability();
    }

    bindEvents() {
        // Windows download
        this.downloadButtons.windows.addEventListener('click', (e) => {
            e.preventDefault();
            this.downloadFile('windows');
        });

        // Add click handlers for future platforms
        this.downloadButtons.mac.addEventListener('click', (e) => {
            e.preventDefault();
            if (!e.target.classList.contains('disabled')) {
                this.downloadFile('mac');
            }
        });

        this.downloadButtons.linux.addEventListener('click', (e) => {
            e.preventDefault();
            if (!e.target.classList.contains('disabled')) {
                this.downloadFile('linux');
            }
        });
    }

    async checkAvailability() {
        // Check if releases are available
        try {
            console.log('Fetching latest release from GitHub API...');
            const response = await fetch('https://api.github.com/repos/JozefJarosciak/GitFit.dev-public/releases/latest');

            if (response.ok) {
                const release = await response.json();
                this.latestRelease = release;
                console.log('Latest release found:', release.tag_name);
                console.log('Available assets:', release.assets.map(a => a.name));

                // Find available Windows versions - improved detection
                const windowsAssets = release.assets.filter(asset => {
                    const name = asset.name.toLowerCase();
                    return name.includes('windows') ||
                           name.includes('win') ||
                           name.endsWith('.exe') ||
                           (name.includes('gitfitdev') && (name.includes('setup') || name.includes('portable') || name.includes('.zip')));
                });

                console.log('Windows assets found:', windowsAssets.map(a => a.name));

                // Categorize Windows downloads with better detection
                this.windowsDownloads = {
                    installer: windowsAssets.find(asset => {
                        const name = asset.name.toLowerCase();
                        return name.includes('setup') || name.includes('installer');
                    }),
                    portable: windowsAssets.find(asset => {
                        const name = asset.name.toLowerCase();
                        return name.includes('portable') && name.endsWith('.exe');
                    }),
                    zip: windowsAssets.find(asset => {
                        const name = asset.name.toLowerCase();
                        return name.endsWith('.zip') && (name.includes('windows') || name.includes('gitfitdev'));
                    })
                };

                console.log('Categorized downloads:', {
                    installer: this.windowsDownloads.installer?.name,
                    portable: this.windowsDownloads.portable?.name,
                    zip: this.windowsDownloads.zip?.name
                });

                // Enable downloads based on available assets
                if (windowsAssets.length > 0) {
                    this.enableWindowsDownload();
                } else {
                    console.log('No Windows assets found, keeping fallback behavior');
                }

                const macAssets = release.assets.filter(asset => {
                    const name = asset.name.toLowerCase();
                    return name.includes('macos') || name.includes('mac') || name.includes('.dmg');
                });
                if (macAssets.length > 0) {
                    this.downloadUrls.mac = macAssets[0].browser_download_url;
                    this.enableDownload('mac');
                }

                const linuxAssets = release.assets.filter(asset => {
                    const name = asset.name.toLowerCase();
                    return name.includes('linux') || name.includes('appimage');
                });
                if (linuxAssets.length > 0) {
                    this.downloadUrls.linux = linuxAssets[0].browser_download_url;
                    this.enableDownload('linux');
                }
            }
            } else {
                console.log('Failed to fetch releases:', response.status, response.statusText);
                this.enableFallbackDownloads();
            }
        } catch (error) {
            console.error('Could not check release availability:', error);
            console.error('Error details:', error.message);
            this.enableFallbackDownloads();
        }
    }

    enableFallbackDownloads() {
        console.log('Using fallback downloads - pointing to releases page');
        // Fallback to release page if API fails
        this.downloadUrls.windows = 'https://github.com/JozefJarosciak/GitFit.dev-public/releases/latest';
        this.enableDownload('windows');
        this.enableDownload('mac');
        this.enableDownload('linux');
    }

    enableWindowsDownload() {
        const button = this.downloadButtons.windows;
        button.classList.remove('disabled');

        // Update button to show dropdown options
        const icon = button.querySelector('.btn-icon');
        icon.textContent = '⬇️';

        // Replace button content with dropdown
        const availableOptions = [];
        if (this.windowsDownloads.installer) availableOptions.push('installer');
        if (this.windowsDownloads.portable) availableOptions.push('portable');
        if (this.windowsDownloads.zip) availableOptions.push('zip');

        if (availableOptions.length > 1) {
            // Create dropdown for multiple options
            button.innerHTML = `<span class="btn-icon">⬇️</span>Download for Windows ▼`;
            button.style.position = 'relative';
            this.createWindowsDropdown(button, availableOptions);
        } else if (availableOptions.length === 1) {
            // Single option available
            const option = availableOptions[0];
            button.innerHTML = `<span class="btn-icon">⬇️</span>Download for Windows (${option.charAt(0).toUpperCase() + option.slice(1)})`;
            button.onclick = (e) => {
                e.preventDefault();
                this.downloadWindowsVersion(option);
            };
        }
    }

    createWindowsDropdown(button, options) {
        // Create dropdown menu
        const dropdown = document.createElement('div');
        dropdown.className = 'windows-download-dropdown';
        dropdown.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            box-shadow: var(--shadow);
            z-index: 1000;
            display: none;
            margin-top: 5px;
        `;

        options.forEach(option => {
            const item = document.createElement('a');
            item.href = '#';
            item.className = 'dropdown-item';
            item.style.cssText = `
                display: block;
                padding: 12px 16px;
                color: var(--text-primary);
                text-decoration: none;
                transition: background 0.2s ease;
                border-radius: 6px;
                margin: 4px;
            `;

            const optionName = option.charAt(0).toUpperCase() + option.slice(1);
            const description = {
                installer: 'Setup file with automatic installation',
                portable: 'Portable executable (no installation)',
                zip: 'ZIP archive for manual setup'
            };

            item.innerHTML = `
                <div style="font-weight: 600;">${optionName}</div>
                <div style="font-size: 0.85em; color: var(--text-secondary);">${description[option]}</div>
            `;

            item.onmouseenter = () => item.style.background = 'var(--bg-secondary)';
            item.onmouseleave = () => item.style.background = '';

            item.onclick = (e) => {
                e.preventDefault();
                this.downloadWindowsVersion(option);
                dropdown.style.display = 'none';
            };

            dropdown.appendChild(item);
        });

        button.parentElement.style.position = 'relative';
        button.parentElement.appendChild(dropdown);

        // Toggle dropdown on button click
        button.onclick = (e) => {
            e.preventDefault();
            dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
        };

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!button.contains(e.target) && !dropdown.contains(e.target)) {
                dropdown.style.display = 'none';
            }
        });
    }

    downloadWindowsVersion(version) {
        const asset = this.windowsDownloads[version];
        if (asset) {
            this.downloadUrls.windows = asset.browser_download_url;
            this.downloadFile('windows');

            // Track specific version
            this.trackDownload(`windows-${version}`);
        }
    }

    enableDownload(platform) {
        const button = this.downloadButtons[platform];
        button.classList.remove('disabled');

        // Update button text and icon
        const icon = button.querySelector('.btn-icon');
        const text = button.childNodes[button.childNodes.length - 1];

        icon.textContent = '⬇️';
        text.textContent = `Download for ${platform.charAt(0).toUpperCase() + platform.slice(1)}`;
    }

    downloadFile(platform) {
        // Track download (you can add analytics here if needed)
        this.trackDownload(platform);

        // Trigger download
        const url = this.downloadUrls[platform];
        const link = document.createElement('a');
        link.href = url;
        link.download = '';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        // Show success message
        this.showDownloadFeedback(platform);
    }

    trackDownload(platform) {
        // Simple tracking without external services
        const downloads = JSON.parse(localStorage.getItem('gitfit_downloads') || '[]');
        downloads.push({
            platform,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent.substring(0, 100) // Truncated for privacy
        });

        // Keep only last 10 downloads
        if (downloads.length > 10) {
            downloads.splice(0, downloads.length - 10);
        }

        localStorage.setItem('gitfit_downloads', JSON.stringify(downloads));
    }

    showDownloadFeedback(platform) {
        const button = this.downloadButtons[platform];
        const originalContent = button.innerHTML;

        button.innerHTML = '<span class="btn-icon">✅</span>Download Started!';
        button.style.background = 'var(--accent-primary)';

        setTimeout(() => {
            button.innerHTML = originalContent;
            button.style.background = '';
        }, 3000);
    }
}

// Smooth scrolling for navigation links
class NavigationManager {
    constructor() {
        this.navLinks = document.querySelectorAll('a[href^="#"]');
        this.bindEvents();
    }

    bindEvents() {
        this.navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);

                if (targetElement) {
                    const offsetTop = targetElement.offsetTop - 80; // Account for fixed header
                    window.scrollTo({
                        top: offsetTop,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }
}

// Intersection Observer for animations
class AnimationManager {
    constructor() {
        this.observerOptions = {
            root: null,
            rootMargin: '0px',
            threshold: 0.1
        };

        this.observer = new IntersectionObserver(
            this.handleIntersection.bind(this),
            this.observerOptions
        );

        this.animateElements = document.querySelectorAll('.feature-card, .download-card');
        this.observe();
    }

    observe() {
        this.animateElements.forEach(element => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(30px)';
            element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            this.observer.observe(element);
        });
    }

    handleIntersection(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                this.observer.unobserve(entry.target);
            }
        });
    }
}

// Performance monitoring
class PerformanceMonitor {
    constructor() {
        this.startTime = performance.now();
        this.bindEvents();
    }

    bindEvents() {
        window.addEventListener('load', () => {
            const loadTime = performance.now() - this.startTime;
            console.log(`Page loaded in ${Math.round(loadTime)}ms`);
        });

        // Monitor Core Web Vitals
        if ('web-vitals' in window) {
            // This would require importing the web-vitals library
            // For now, just basic performance monitoring
        }
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize all managers
    new ThemeManager();
    new DownloadManager();
    new NavigationManager();
    new AnimationManager();
    new PerformanceMonitor();

    // Add keyboard navigation support
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
            document.body.classList.add('keyboard-navigation');
        }
    });

    document.addEventListener('mousedown', () => {
        document.body.classList.remove('keyboard-navigation');
    });

    // Console welcome message
    console.log(`
╔══════════════════════════════════════╗
║           GitFit.dev Website         ║
║                                      ║
║  Thanks for checking out the code!   ║
║  This site is built with vanilla     ║
║  HTML, CSS, and JavaScript.          ║
║                                      ║
║  Star us on GitHub! 🌟               ║
╚══════════════════════════════════════╝
    `);
});

// Export for potential future use
window.GitFitWebsite = {
    ThemeManager,
    DownloadManager,
    NavigationManager,
    AnimationManager,
    PerformanceMonitor
};