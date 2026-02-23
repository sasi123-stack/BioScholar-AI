# Firebase Hosting Setup Guide

## 🔥 Deploy BioMedScholar AI to Firebase Hosting

### Prerequisites
- ✅ Firebase CLI installed (done!)
- ✅ Google account
- ✅ Firebase project created (you have `biomed-scholar` project)
- ✅ Frontend files ready

### Step-by-Step Setup

## **Step 1: Login to Firebase**

Run this command in your terminal:

```bash
firebase login
```

This will:
1. Open a browser window
2. Ask you to sign in with your Google account
3. Grant Firebase CLI permission to deploy
4. Return you to the terminal with authentication complete

**Note**: Use the Google account that owns the `biomed-scholar` Firebase project.

---

## **Step 2: Verify Project Setup**

```bash
cd /workspaces/BioScholar-AI/biomed-modern-frontend
firebase projects:list
```

You should see `biomed-scholar` in the list.

---

## **Step 3: Initialize Firebase Hosting**

```bash
firebase init hosting
```

When prompted:

```
? What do you want to use as your public directory?
→ . (current directory - contains index.html)

? Configure as a single-page app (rewrite all URLs to /index.html)?
→ y (Yes - for proper routing)

? Set up automatic builds and deploys with GitHub?
→ n (No - we'll deploy manually)

? File index.html already exists. Overwrite?
→ n (No - keep our version)
```

This creates:
- `.firebaserc` - Firebase project configuration
- `firebase.json` - Hosting configuration

---

## **Step 4: Deploy to Firebase Hosting**

```bash
firebase deploy --project=biomed-scholar
```

The CLI will:
1. Upload all files to Firebase Hosting
2. Generate a public URL
3. Show deployment status

Output example:
```
Deploying hosting files to: biomed-scholar.web.app

✔ hosted (12.1 kB in 15 files)

✔ Deploy complete!

Project Console: https://console.firebase.google.com/project/biomed-scholar
Hosting URL: https://biomed-scholar.web.app
```

---

## **Step 5: Verify Deployment**

Your site is now live! Visit:

```
https://biomed-scholar.web.app
```

---

## 📋 Generated Files

### firebase.json
```json
{
  "hosting": {
    "public": ".",
    "ignore": ["firebase.json", "**/node_modules/**"],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
}
```

### .firebaserc
```json
{
  "projects": {
    "default": "biomed-scholar"
  }
}
```

---

## 🚀 Automated Deployment Script

I've created `deploy.sh` to automate everything:

```bash
chmod +x deploy.sh
./deploy.sh
```

This will:
1. Check Firebase CLI installation
2. Prompt you to login
3. Initialize hosting
4. Deploy automatically
5. Show your live URL

---

## 📱 Testing Your Deployment

After deployment, verify:

### Feature Checklist
- [ ] Home page loads
- [ ] Dark mode toggle works
- [ ] Search input focuses with Ctrl+K
- [ ] Reading list sidebar opens with B key
- [ ] Filters panel works
- [ ] Modals open and close
- [ ] LST runs fine on mobile (test at https://biomed-scholar.web.app on phone)

### Performance Check
```bash
firebase hosting:disable  # Temporarily disable
firebase hosting:enable   # Re-enable
```

---

## 🔄 Continuous Deployment

### Manual Updates
After making changes:

```bash
firebase deploy --project=biomed-scholar
```

### Automated with GitHub (Optional)
1. Connect your GitHub repo in Firebase Console
2. Enable automatic deployments on push
3. Every push to main branch deploys automatically

---

## 📊 Monitor Your Deployment

### In Firebase Console
```
https://console.firebase.google.com/project/biomed-scholar
```

You can:
- View traffic analytics
- Check performance
- Set up custom domains
- Manage SSL certificates
- View deployment history

### Command Line
```bash
# View hosting status
firebase hosting:list

# View recent deployments
firebase hosting:log

# Delete a version
firebase hosting:delete-release <release_id>
```

---

## 🌐 Custom Domain Setup (Optional)

To link a custom domain like `biomedscholar.ai`:

1. Go to Firebase Console → Hosting
2. Click "Connect domain"
3. Enter your domain
4. Add DNS records provided by Firebase
5. Wait for verification (can take up to 24 hours)

---

## 🔐 Security headers

Your `firebase.json` already includes:

```json
{
  "hosting": {
    "headers": [
      {
        "source": "**",
        "headers": [
          { "key": "X-Content-Type-Options", "value": "nosniff" },
          { "key": "X-Frame-Options", "value": "SAMEORIGIN" },
          { "key": "X-XSS-Protection", "value": "1; mode=block" }
        ]
      }
    ]
  }
}
```

---

## 🆘 Troubleshooting

### "Not authenticated" error
```bash
firebase logout
firebase login
```

### "Cannot find firebase.json"
Make sure you're in the correct directory:
```bash
cd /workspaces/BioScholar-AI/biomed-modern-frontend
firebase init hosting
```

### Changes not showing
Firebase caches files. Force refresh:
```
Ctrl + Shift + R (Windows/Linux)
Cmd + Shift + R (macOS)
```

Or clear cache and deploy again:
```bash
firebase deploy --force
```

### 404 on refresh
Make sure `firebase.json` has the rewrite rule for SPA:
```json
"rewrites": [{"source": "**", "destination": "/index.html"}]
```

---

## 📈 Environment Variables

If you need environment variables (API keys, etc.):

### Method 1: .env file (not hosted)
Create `.env` file locally:
```
API_BASE_URL=https://your-api.com
FIREBASE_KEY=xxxxx
```

Reference in JavaScript:
```javascript
const API = process.env.API_BASE_URL;
```

**Note**: This requires a build process. For static hosting, hardcode in config or load from server.

### Method 2: Firebase Config
Use Firebase config file:
```javascript
import { initializeApp } from 'firebase/app';

const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "biomed-scholar.firebaseapp.com",
  projectId: "biomed-scholar"
};

initializeApp(firebaseConfig);
```

---

## 🎉 Post-Deployment

### Share Your Site
```
https://biomed-scholar.web.app
```

### Monitor Performance
- Check Firebase Console analytics
- Monitor page load speed
- Track user engagement
- View error reports

### Keep Updated
1. Make changes locally
2. Test in browser
3. Run: `firebase deploy --project=biomed-scholar`
4. Verify changes on live site

---

## 📞 Next Steps

1. ✅ Install Firebase CLI (done!)
2. 🔐 Run `firebase login`
3. 🚀 Run `firebase deploy`
4. 🌐 Visit `https://biomed-scholar.web.app`
5. ✨ Share your deployed site!

---

**Your modern BioMedScholar AI frontend is ready for the world! 🚀**
