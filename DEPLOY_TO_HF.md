# How to Deploy Maverick AI to Hugging Face Spaces

1. **Create a New Space**: 
   - Go to [huggingface.co/new-space](https://huggingface.co/new-space)
   - Name it: `maverick-telegram-bot`
   - SDK: **Docker**
   - Choose: **Blank** template

2. **Upload Files**:
   - Upload the contents of the `telegram-bot-hf/` folder:
     - `Dockerfile`
     - `requirements.txt`
     - `app.py`

3. **Set Secrets (CRITICAL)**:
   - Go to your Space's **Settings** tab.
   - Click **New Secret** for each of these:
     - **Name**: `TELEGRAM_BOT_TOKEN`, **Value**: `YOUR_TOKEN_HERE`
     - **Name**: `GROQ_API_KEY`, **Value**: `YOUR_GROQ_KEY_HERE`

4. **Wait for Build**:
   - Once the secrets are saved, the Space will rebuild.
   - When the logs say "Application started" and the status turns to **Running**, your bot is live 24/7!
