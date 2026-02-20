# PubMed API Quick Setup Guide

## 1. Get Your PubMed API Key (Free)

### Step-by-Step:
1. **Visit NCBI Account**: https://www.ncbi.nlm.nih.gov/account/
2. **Sign in or Create Account**:
   - Click "Sign in to NCBI" (top right)
   - Create new account or login with existing credentials
   
3. **Navigate to API Key Settings**:
   - After login, go to: https://www.ncbi.nlm.nih.gov/account/settings/
   - Or: Click your username → Account Settings
   
4. **Create API Key**:
   - Scroll to "API Key Management" section
   - Click "Create an API Key" button
   - Your key will be generated instantly
   - **Copy the key** - it looks like: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8`

5. **Save Your Key**:
   - Store it securely
   - You'll add it to your `.env` file

## 2. Update Your `.env` File

Open `c:\Users\sriva\Documents\kash_proj\.env` and update:

```env
# PubMed API Configuration
PUBMED_API_KEY=your_actual_api_key_here
PUBMED_EMAIL=your_email@example.com
PUBMED_RATE_LIMIT=10
```

**Important Notes:**
- `PUBMED_API_KEY`: Paste your API key from NCBI
- `PUBMED_EMAIL`: Use the email registered with NCBI (required by NCBI policy)
- `PUBMED_RATE_LIMIT`: With API key = 10 requests/sec, without = 3 requests/sec

## 3. PubMed API Basics

### API Endpoints:
- **Base URL**: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`
- **Search**: `esearch.fcgi` - Find article IDs
- **Fetch**: `efetch.fcgi` - Get article details
- **Summary**: `esummary.fcgi` - Get article summaries

### Example Usage:

#### Search for Articles:
```
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?
  db=pubmed
  &term=diabetes+treatment
  &retmax=20
  &retmode=json
  &api_key=YOUR_API_KEY
```

#### Fetch Article Details:
```
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?
  db=pubmed
  &id=12345678,23456789
  &retmode=xml
  &api_key=YOUR_API_KEY
```

## 4. Rate Limits

| Status | Rate Limit |
|--------|------------|
| **With API Key** | 10 requests/second |
| **Without API Key** | 3 requests/second |

## 5. Test Your Setup

After updating `.env`, test with:

```powershell
# Activate environment
conda activate biomedical-search

# Test script
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('PUBMED_API_KEY')
email = os.getenv('PUBMED_EMAIL')

print('PubMed API Key:', api_key[:10] + '...' if api_key else 'NOT SET')
print('Email:', email if email else 'NOT SET')
"
```

## 6. Quick Python Example

```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_KEY = os.getenv('PUBMED_API_KEY')
EMAIL = os.getenv('PUBMED_EMAIL')
BASE_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'

# Search for articles
def search_pubmed(query, max_results=10):
    url = f"{BASE_URL}esearch.fcgi"
    params = {
        'db': 'pubmed',
        'term': query,
        'retmax': max_results,
        'retmode': 'json',
        'api_key': API_KEY,
        'email': EMAIL
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    # Get list of PubMed IDs
    ids = data['esearchresult']['idlist']
    return ids

# Fetch article details
def fetch_articles(pmids):
    url = f"{BASE_URL}efetch.fcgi"
    params = {
        'db': 'pubmed',
        'id': ','.join(pmids),
        'retmode': 'xml',
        'api_key': API_KEY,
        'email': EMAIL
    }
    
    response = requests.get(url, params=params)
    return response.text

# Usage
if __name__ == '__main__':
    # Search
    ids = search_pubmed('COVID-19 treatment', max_results=5)
    print(f"Found {len(ids)} articles:", ids)
    
    # Fetch details
    if ids:
        xml_data = fetch_articles(ids[:3])
        print("Article data retrieved successfully!")
```

## 7. Resources

- **Official Documentation**: https://www.ncbi.nlm.nih.gov/books/NBK25501/
- **E-utilities Help**: https://www.ncbi.nlm.nih.gov/books/NBK25499/
- **API Key Info**: https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/

## Common Issues

### ❌ "API rate limit exceeded"
- Add API key to all requests
- Implement rate limiting (use `time.sleep()`)
- Use batch requests when possible

### ❌ "Email parameter required"
- Always include email in requests
- NCBI uses it to contact you if there are problems

### ❌ "Invalid API key"
- Check key is copied correctly (no spaces)
- Verify key is active in NCBI account settings
