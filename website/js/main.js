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
        this.downloadButtons = {
            windows: document.getElementById('downloadWindows'),
            mac: document.getElementById('downloadMac'),
            linux: document.getElementById('downloadLinux')
        };

        // GitHub release URLs - update these when releases are available
        this.downloadUrls = {
            windows: 'https://github.com/JozefJarosciak/GitFit.dev/releases/latest/download/GitFitDev-Windows-Setup.exe',
            mac: 'https://github.com/JozefJarosciak/GitFit.dev/releases/latest/download/GitFitDev-macOS-Installer.dmg',
            linux: 'https://github.com/JozefJarosciak/GitFit.dev/releases/latest/download/GitFitDev-Linux.AppImage'
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
            const response = await fetch('https://api.github.com/repos/JozefJarosciak/GitFit.dev/releases/latest');
            if (response.ok) {
                const release = await response.json();
                const assets = release.assets.map(asset => asset.name.toLowerCase());

                // Enable downloads based on available assets
                if (assets.some(name => name.includes('windows') && name.includes('setup'))) {
                    this.enableDownload('windows');
                }
                if (assets.some(name => name.includes('macos') || name.includes('mac'))) {
                    this.enableDownload('mac');
                }
                if (assets.some(name => name.includes('linux') || name.includes('appimage'))) {
                    this.enableDownload('linux');
                }
            }
        } catch (error) {
            console.log('Could not check release availability:', error);
            // Windows is always available since it's explicitly mentioned
            this.enableDownload('windows');
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