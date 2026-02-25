---
description: Build a native Android APK for BioMedScholar AI
---

To convert the current BioMedScholar frontend into a native Android app that looks and functions exactly like the website, follow these steps:

### 1. Prerequisites
Ensure you have **Node.js** and **Android Studio** installed on your machine.

### 2. Initialize Native Project
Run these commands in your terminal to set up the Android bridge:
```powershell
# Install Capacitor
npm install @capacitor/core @capacitor/cli

# Add Android Platform
npx cap add android
```

### 3. Sync Web Code to Android
Every time you update your frontend, run:
```powershell
npx cap sync
```

### 4. Build and Run the APK
To open the project in Android Studio for final compilation:
```powershell
npx cap open android
```
- In Android Studio, click **Build > Build Bundle(s) / APK(s) > Build APK(s)**.
- The output `.apk` will be ready to install on your phone.

### Pro-Tip: Immediate Android "App"
You don't need a build to test it! Since I've already configured the **PWA Manifest**:
1. Open **Chrome** on your Android phone.
2. Navigate to [biomed-scholar.web.app](https://biomed-scholar.web.app).
3. Tap the **Three Dots (⋮)** and select **"Install App"**.
4. BioMedScholar will appear on your home screen as a full-screen, native-feeling app!
