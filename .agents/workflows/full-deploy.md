---
description: Deploy BioMedScholar AI updates to Firebase, GitHub, and Hugging Face
---

Follow these steps to ensure all platforms are synchronized after updating the application or the Help & Guide section:

1. **Deploy to Firebase Hosting (Production Frontend)**
// turbo
```powershell
cd "d:\MTech 2nd Year\BioMedScholar AI\frontend"
firebase deploy --only hosting
```

2. **Deploy to GitHub**
// turbo
```powershell
cd "d:\MTech 2nd Year\BioMedScholar AI"
git add .
git commit -m "docs: update help guide and research AI documentation"
git push origin main
```

3. **Deploy to Hugging Face Space (Frontend/Bot)**
// turbo
```powershell
cd "d:\MTech 2nd Year\BioMedScholar AI"
git push bot-space main
```

4. **Deploy to Hugging Face API Space (Backend)**
// turbo
```powershell
cd "d:\MTech 2nd Year\BioMedScholar AI"
git push hf main
```
