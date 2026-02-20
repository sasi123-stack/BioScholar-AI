# Biomedical Search Engine - Setup Guide

## Environment Setup with Conda

### Step 1: Create Conda Environment

Open PowerShell and navigate to the project directory, then run:

```powershell
# Create conda environment from YAML file
conda env create -f environment.yml

# This creates an environment named 'biomedical-search' with Python 3.9 and all dependencies
```

### Step 2: Activate the Environment

```powershell
conda activate biomedical-search
```

### Step 3: Install Additional Python Packages

```powershell
# Install packages from requirements.txt
pip install -r requirements.txt
```

### Step 4: Run Setup Script

```powershell
# Run the setup script to create necessary directories and download models
python scripts\setup.py
```

### Step 5: Configure Environment Variables

```powershell
# Copy the example .env file
Copy-Item .env.example .env

# Edit .env file with your actual credentials and API keys
notepad .env
```

Update the following in `.env`:
- `PUBMED_API_KEY`: Get from NCBI (https://www.ncbi.nlm.nih.gov/account/)
- `PUBMED_EMAIL`: Your email for PubMed API
- `ELASTICSEARCH_PASSWORD`: Set a secure password
- `SECRET_KEY`: Generate a secure random key

### Step 6: Start Docker Services (Elasticsearch, Redis, PostgreSQL)

```powershell
# Navigate to docker directory
cd docker

# Start all services
docker-compose up -d

# Check services are running
docker-compose ps

# Go back to project root
cd ..
```

### Step 7: Verify Installation

```powershell
# Test Python imports
python -c "import torch; import transformers; print('PyTorch:', torch.__version__); print('Transformers:', transformers.__version__)"

# Test Elasticsearch connection
python -c "from elasticsearch import Elasticsearch; es = Elasticsearch(['http://localhost:9200']); print('Elasticsearch:', es.info()['version']['number'])"
```

## Quick Commands Reference

```powershell
# Activate environment
conda activate biomedical-search

# Deactivate environment
conda deactivate

# Update environment from YAML
conda env update -f environment.yml --prune

# List installed packages
conda list

# Export environment
conda env export > environment.yml

# Remove environment
conda env remove -n biomedical-search
```

## Troubleshooting

### CUDA/GPU Issues
If you don't have a CUDA-capable GPU, edit `environment.yml` and remove the `cudatoolkit` line, then recreate the environment.

### Elasticsearch Connection
Make sure Docker Desktop is running and Elasticsearch container is up:
```powershell
docker ps | Select-String elasticsearch
```

### Port Already in Use
If ports 9200, 6379, or 5432 are already in use, modify `docker/docker-compose.yml` to use different ports.

## Next Steps
After setup, proceed to Task 2: Data Acquisition Pipeline
