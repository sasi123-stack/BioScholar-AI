---
description: Deploy the frontend to Firebase Hosting
---
This workflow is used to deploy the latest frontend changes to Firebase Hosting.

// turbo-all
1. Run the firebase deployment command:
```powershell
npx -y firebase-tools deploy --only hosting
```
2. Verify the output for "Deploy complete!" and the hosting URL.
