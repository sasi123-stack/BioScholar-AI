# 🦞 OpenClaw Hugging Face Deployment Guide

I've prepared everything you need to host your OpenClaw AI Agent on Hugging Face Spaces.

### 📁 Files Prepared
Go to the `openclaw-hf` folder in this project to see:
- `Dockerfile`: The instructions to build the OpenClaw container.
- `README.md`: Metadata for Hugging Face.
- `workspace/`: A copy of your local OpenClaw workspace (Soul, Tools, Identity).

---

### 🚀 Step-by-Step Instructions

#### 1. Create a New Space
1. Log in to [Hugging Face](https://huggingface.co/).
2. Click **New Space**.
3. **Space Name**: `openclaw-agent` (or any name you like).
4. **SDK**: Select **Docker** (Blank).
5. **License**: MIT (or your preference).
6. **Visibility**: I recommend **Private** if you are storing sensitive info, though we've tried to keep secrets out of the code.

#### 2. Upload the Files
You can use the Hugging Face web interface to upload the files:
1. Go to the **Files** tab in your new Space.
2. Click **Add File** -> **Upload files**.
3. Drag and drop all files from the `openclaw-hf` folder on your computer.
   *   `Dockerfile`
   *   `README.md`
   *   The entire `workspace/` folder.

#### 3. Configure Secrets (Very Important!)
OpenClaw needs API keys to talk to AI models (like OpenRouter).
1. In your Space, go to **Settings**.
2. Scroll down to **Variables and secrets**.
3. Click **New secret** and add:
   *   `OPENROUTER_API_KEY`: Your OpenRouter key.
   *   `OPENAI_API_KEY`: (Optional) If you use OpenAI.
   *   `GEMINI_API_KEY`: (Optional) If you use Gemini.

#### 4. Access Your Agent
1. Wait for the Space to finish building (it takes about 2-3 minutes).
2. Once it shows **Running**, go to the **App** tab.
3. You will see your OpenClaw Chat interface!
4. The default admin token is `admin-token-123` (unless you changed it in the Dockerfile).

---

### ⚠️ Important Notes
- **Local vs. Cloud**: Since the agent is running on Hugging Face servers, it cannot access your physical computer's files or local shell (unless you use a tunnel like Ngrok).
- **Public Spaces**: If your Space is public, anyone with the link can see the chat interface! Use a strong token in the Dockerfile or make the Space Private.
