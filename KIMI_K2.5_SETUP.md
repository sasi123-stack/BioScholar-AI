# 🚀 Kimi K2.5 Integration with OpenClaw

This guide explains how to use **Moonshot AI's Kimi K2.5** agent model with your OpenClaw setup for enhanced biomedical research capabilities.

## 🤖 What is Kimi K2.5?

Kimi K2.5 is an advanced **native multimodal agentic AI model** developed by Moonshot AI with the following capabilities:

- **🧠 Advanced Reasoning**: Long-thinking capabilities for complex problem-solving
- **👁️ Multimodal Understanding**: Pre-trained on ~15 trillion mixed visual and text tokens
- **🤝 Agent Swarm**: Can decompose complex tasks into parallel sub-tasks
- **💻 Visual Coding**: Generates code from visual specifications (UI designs, workflows)
- **🔬 Scientific Synthesis**: Excellent for biomedical research and evidence-based answers

## 📋 Prerequisites

1. **OpenRouter Account**: Sign up at [https://openrouter.ai](https://openrouter.ai)
2. **API Key**: Get your OpenRouter API key from [https://openrouter.ai/keys](https://openrouter.ai/keys)
3. **Credits**: Add credits to your OpenRouter account (pay-as-you-go pricing)

## ⚙️ Configuration Steps

### 1. Update Environment Variables

Edit your `.env` file and update the OpenClaw configuration:

```bash
# OpenClaw Integration with Kimi K2.5
OPENCLAW_API_KEY=sk-or-v1-YOUR_ACTUAL_OPENROUTER_API_KEY
OPENCLAW_API_BASE=https://openrouter.ai/api/v1
```

**Replace `YOUR_ACTUAL_OPENROUTER_API_KEY`** with your actual OpenRouter API key.

### 2. Verify Configuration Files

The following files have been updated to use Kimi K2.5:

✅ **`openclaw-hf/Dockerfile`** - OpenClaw gateway configured with `moonshot/kimi-k2.5`  
✅ **`src/qa_module/openclaw_generator.py`** - Python backend using Kimi K2.5  
✅ **`.env`** - Environment variables configured for OpenRouter

### 3. Test the Integration

#### Option A: Test with Python Backend

```powershell
# Start the backend API
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload

# In another terminal, test the Q&A endpoint
curl -X POST "http://localhost:8000/api/v1/qa" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the latest treatments for COVID-19?",
    "source": "pubmed",
    "top_k": 3
  }'
```

#### Option B: Test with OpenClaw Gateway

```powershell
# Navigate to openclaw-hf directory
cd openclaw-hf

# Build the Docker image
docker build -t openclaw-kimi .

# Run with your OpenRouter API key
docker run -p 7860:7860 \
  -e OPENROUTER_API_KEY=sk-or-v1-YOUR_KEY_HERE \
  openclaw-kimi
```

Then visit: **http://localhost:7860**

## 🎯 Usage Examples

### Biomedical Question Answering

```python
from src.qa_module.openclaw_generator import OpenClawGenerator

# Initialize with Kimi K2.5
generator = OpenClawGenerator()

# Ask a complex biomedical question
result = generator.generate_answer(
    question="How does mRNA vaccine technology work?",
    passages=[
        {
            "title": "mRNA Vaccine Mechanisms",
            "text": "mRNA vaccines deliver genetic instructions...",
            "source_type": "pubmed"
        }
    ]
)

print(result["answer"])
```

### Advanced Agentic Features

Kimi K2.5 excels at:

1. **Multi-step Reasoning**: Breaking down complex medical questions
2. **Cross-modal Understanding**: Analyzing research papers with figures
3. **Evidence Synthesis**: Connecting insights across multiple sources
4. **Pattern Recognition**: Identifying trends in biomedical literature

## 💰 Pricing

OpenRouter pricing for Kimi K2.5 (as of Feb 2025):

- **Input**: ~$0.50 per 1M tokens
- **Output**: ~$2.00 per 1M tokens

**Estimated costs for typical usage:**
- Simple Q&A: $0.001 - $0.005 per query
- Complex synthesis: $0.01 - $0.05 per query

## 🔧 Troubleshooting

### Issue: "OpenClaw client failed to initialize"

**Solution**: Check your API key in `.env`:
```bash
# Make sure it starts with sk-or-v1-
OPENCLAW_API_KEY=sk-or-v1-...
```

### Issue: "Model not found" or 401 Unauthorized

**Solutions**:
1. Verify your OpenRouter API key is valid
2. Check you have credits in your OpenRouter account
3. Ensure the model name is exactly: `moonshot/kimi-k2.5`

### Issue: Slow responses

**Explanation**: Kimi K2.5 uses "long-thinking" mode for complex queries, which may take 5-15 seconds. This is normal for deep reasoning tasks.

## 🚀 Deployment to Hugging Face

To deploy your Kimi K2.5-powered agent to Hugging Face Spaces:

1. **Navigate to openclaw-hf folder**:
   ```powershell
   cd openclaw-hf
   ```

2. **Create a new Space** at [https://huggingface.co/new-space](https://huggingface.co/new-space)
   - Space name: `your-username/biosense-kimi-agent`
   - SDK: Docker
   - Hardware: CPU Basic (free tier)

3. **Upload files**:
   - Drag and drop all files from `openclaw-hf/` folder
   - Or use Git:
     ```bash
     git clone https://huggingface.co/spaces/your-username/biosense-kimi-agent
     cd biosense-kimi-agent
     cp -r ../openclaw-hf/* .
     git add .
     git commit -m "Deploy Kimi K2.5 agent"
     git push
     ```

4. **Set Environment Variables** in Space Settings:
   - `OPENROUTER_API_KEY`: Your OpenRouter API key
   - Mark as "Secret" ✅

5. **Wait for build** (~5-10 minutes)

6. **Access your agent** at: `https://huggingface.co/spaces/your-username/biosense-kimi-agent`

## 🎨 Customization

### Adjust Temperature for Different Use Cases

Edit `src/qa_module/openclaw_generator.py`:

```python
# For factual medical answers (more deterministic)
temperature=0.1

# For creative synthesis (more diverse)
temperature=0.7
```

### Enable Agent Swarm Mode

For complex multi-step tasks, Kimi K2.5 can use agent swarm capabilities. Add to your system prompt:

```python
system_prompt = (
    "You are a biomedical research assistant powered by Kimi K2.5. "
    "For complex tasks, decompose them into parallel sub-tasks. "
    "Use your agent swarm capabilities to coordinate multiple specialized agents. "
    # ... rest of prompt
)
```

## 📚 Additional Resources

- **Kimi K2.5 Documentation**: [https://kimi.com](https://kimi.com)
- **OpenRouter Docs**: [https://openrouter.ai/docs](https://openrouter.ai/docs)
- **Moonshot AI Platform**: [https://moonshot.ai](https://moonshot.ai)
- **Model Card**: [https://huggingface.co/Moonshot/Kimi-K2.5](https://huggingface.co/Moonshot/Kimi-K2.5)

## 🤝 Support

If you encounter issues:

1. Check the logs: `docker logs <container_id>`
2. Verify API key permissions on OpenRouter
3. Test with a simple query first
4. Check OpenRouter status: [https://status.openrouter.ai](https://status.openrouter.ai)

---

**Made with ❤️ using Kimi K2.5, OpenClaw, and BioSense AI**
