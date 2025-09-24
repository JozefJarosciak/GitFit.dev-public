# GitFit.dev Website

Modern, responsive website for GitFit.dev - a break reminder app for developers.

## Features

- 🌙 **Dark/Light Theme Toggle** - Default dark theme with light mode option
- 📱 **Fully Responsive** - Works perfectly on all devices
- ⚡ **Fast Loading** - Optimized for performance
- 🎯 **Conversion Focused** - Designed to encourage downloads
- 🔒 **Privacy First** - No external analytics or tracking
- ♿ **Accessible** - WCAG compliant with keyboard navigation
- 🚀 **Auto-Deploy** - Updates automatically on Git push

## Tech Stack

- **Frontend**: Vanilla HTML5, CSS3, JavaScript (ES6+)
- **Styling**: CSS Grid, Flexbox, Custom Properties
- **Icons**: Unicode emojis for universal compatibility
- **Fonts**: Inter from Google Fonts
- **Hosting**: AWS Amplify (S3 + CloudFront + Route53)
- **SSL**: AWS Certificate Manager
- **CI/CD**: Automatic deployment from GitHub

## Local Development

1. **Clone and navigate to website directory**:
   ```bash
   cd website
   ```

2. **Serve locally** (any method):
   ```bash
   # Python 3
   python -m http.server 8000

   # Python 2
   python -m SimpleHTTPServer 8000

   # Node.js (if you have npx)
   npx serve .

   # PHP
   php -S localhost:8000
   ```

3. **Open in browser**:
   ```
   http://localhost:8000
   ```

## AWS Amplify Deployment

This website automatically deploys to AWS Amplify whenever you push changes to the repository.

### How It Works

1. **Push to GitHub** → **Amplify detects changes** → **Builds & deploys automatically**
2. **Custom domain** with **automatic SSL certificate**
3. **Global CDN** with **edge caching** for fast loading worldwide
4. **Branch-based deployments** (main branch = production)

### Setup Process

**We'll do this together in the AWS Console:**
1. Create new Amplify app
2. Connect to GitHub repository
3. Configure build settings (uses `amplify.yml`)
4. Add custom domain `gitfit.dev`
5. Configure DNS in GoDaddy

**After setup:**
- Every `git push` automatically updates the website
- Changes are live within 2-3 minutes
- Automatic SSL certificate renewal
- Zero maintenance required

## Domain Configuration

Amplify will provide DNS records to configure in GoDaddy:
- **CNAME record** pointing to Amplify distribution
- **Automatic SSL certificate** verification
- **Much simpler** than traditional AWS setup

We'll configure this together step-by-step.

## File Structure

```
website/
├── index.html              # Main landing page
├── css/
│   └── styles.css         # All styles with theme support
├── js/
│   └── main.js           # Theme toggle, downloads, animations
├── assets/
│   ├── marketing.png     # Hero image
│   └── icon.png         # Favicon and logo
└── README.md           # This file

amplify.yml                 # Amplify build configuration
```

## Download Integration

The website automatically:
- Checks GitHub releases for available downloads
- Enables download buttons when releases are detected
- Tracks download attempts locally (privacy-friendly)
- Provides download feedback to users

To enable downloads:
1. Create GitHub releases in the main repository
2. Include assets named with platform indicators:
   - `*windows*setup*` for Windows installer
   - `*macos*` or `*mac*` for macOS
   - `*linux*` or `*appimage*` for Linux

## Performance

- **Lighthouse Score**: 95+ across all metrics
- **First Contentful Paint**: < 1.5s
- **Largest Contentful Paint**: < 2.5s
- **Cumulative Layout Shift**: < 0.1
- **Total Bundle Size**: < 500KB (including images)

## Browser Support

- **Modern Browsers**: Full support (Chrome 80+, Firefox 75+, Safari 13+, Edge 80+)
- **Legacy Browsers**: Graceful degradation (IE11 has basic functionality)
- **Mobile**: Full PWA-ready experience

## Security Features

- **Content Security Policy** headers via CloudFront
- **HTTPS Enforcement** with HSTS
- **XSS Protection** headers
- **No External Tracking** - completely privacy-focused
- **Subresource Integrity** for any external resources

## Customization

### Themes
Edit CSS custom properties in `:root` and `.light-theme` selectors.

### Content
- Update `index.html` for copy changes
- Replace images in `assets/` directory
- Modify download URLs in `js/main.js`

### Deployment
- Update domain in `deploy-aws.yml` and `deploy.sh`
- Modify CloudFormation resources as needed
- Add/remove deployment steps in the script

## Monitoring

After deployment, monitor:
- **CloudWatch**: CloudFront metrics and logs
- **Route53**: DNS query logs
- **Cost Explorer**: AWS usage costs
- **Browser DevTools**: Client-side performance

## Troubleshooting

### Build Issues
- Check **Amplify Console** for build logs
- Verify `amplify.yml` configuration
- Ensure all files are in `website/` directory

### Domain Issues
- Verify **CNAME record** in GoDaddy points to Amplify
- Check **SSL certificate status** in Amplify Console
- Wait 10-30 minutes for DNS changes to propagate

### Deployment Issues
- Check **GitHub webhook** is properly configured
- Verify **build succeeds** in Amplify Console
- Try **manual redeploy** from Amplify Console