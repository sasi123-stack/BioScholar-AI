# 🚀 Deployment Guide

Complete guide for deploying the Biomedical Search Engine to production.

## 📋 Pre-Deployment Checklist

### System Requirements
- [ ] Python 3.9+
- [ ] Docker & Docker Compose
- [ ] 8GB+ RAM recommended
- [ ] 20GB+ disk space
- [ ] NVIDIA GPU (optional, for faster inference)

### Services Status
- [ ] Elasticsearch running and healthy
- [ ] Redis running (optional caching)
- [ ] All indices created and populated
- [ ] Minimum 1000+ documents indexed

### Configuration
- [ ] `.env` file configured with production values
- [ ] API keys and credentials secured
- [ ] CORS settings configured for production domain
- [ ] Rate limiting configured
- [ ] Logging configured for production

---

## 🔧 Production Configuration

### 1. Environment Variables

Update `.env` file for production:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
DEBUG=false

# Elasticsearch
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9201
ELASTICSEARCH_USER=elastic
ELASTICSEARCH_PASSWORD=<strong-password>

# Security
API_KEY=<generate-secure-api-key>
SECRET_KEY=<generate-secure-secret>
ALLOWED_ORIGINS=https://yourdomain.com

# Performance
MAX_CONCURRENT_REQUESTS=100
REQUEST_TIMEOUT=30
CACHE_TTL=3600
```

### 2. Docker Production Setup

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=true
      - ELASTIC_PASSWORD=${ELASTICSEARCH_PASSWORD}
      - "ES_JAVA_OPTS=-Xms4g -Xmx4g"
    volumes:
      - esdata:/usr/share/elasticsearch/data
    ports:
      - "9201:9200"
    restart: always
    deploy:
      resources:
        limits:
          memory: 6G

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis-data:/data
    ports:
      - "6380:6379"
    restart: always

  api:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - ELASTICSEARCH_HOST=elasticsearch
      - ELASTICSEARCH_PORT=9200
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    ports:
      - "8000:8000"
    depends_on:
      - elasticsearch
      - redis
    restart: always
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 4G

volumes:
  esdata:
  redis-data:
```

### 3. Dockerfile for API

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Start API
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

---

## 🚀 Deployment Steps

### Step 1: Prepare Production Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y

# Create deployment directory
mkdir -p /opt/biomedical-search
cd /opt/biomedical-search
```

### Step 2: Clone and Configure

```bash
# Clone repository
git clone <your-repo-url> .

# Copy environment file
cp .env.example .env

# Edit .env with production values
nano .env
```

### Step 3: Build and Start Services

```bash
# Start Docker services
docker-compose -f docker-compose.prod.yml up -d

# Check services are running
docker-compose ps

# View logs
docker-compose logs -f api
```

### Step 4: Index Data

```bash
# Activate environment
conda activate biomedical-search

# Run data ingestion
python scripts/ingest_full_dataset.py

# Verify indexing
python scripts/check_index_status.py
```

### Step 5: Run Integration Tests

```bash
# Install test dependencies
pip install pytest requests

# Run integration tests
pytest tests/test_integration.py -v

# Check test results
```

### Step 6: Deploy Frontend

#### Option A: Static File Server (Nginx)

```bash
# Install Nginx
sudo apt install nginx -y

# Copy frontend files
sudo cp -r frontend/* /var/www/html/biomedical-search/

# Configure Nginx
sudo nano /etc/nginx/sites-available/biomedical-search
```

Nginx configuration:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Frontend
    location / {
        root /var/www/html/biomedical-search;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # API Proxy
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/biomedical-search /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

#### Option B: Serve with Python (Development/Testing)

```bash
cd frontend
python -m http.server 8080
```

### Step 7: Setup SSL (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is configured automatically
```

---

## 📊 Monitoring & Maintenance

### Health Check Endpoint

```bash
# Check API health
curl http://localhost:8000/api/v1/health

# Expected response:
{
  "status": "healthy",
  "services": {
    "elasticsearch": "connected"
  }
}
```

### System Monitoring

```bash
# View API logs
docker-compose logs -f api

# View Elasticsearch logs
docker-compose logs -f elasticsearch

# Check resource usage
docker stats

# Monitor Elasticsearch cluster health
curl -X GET "localhost:9201/_cluster/health?pretty"
```

### Backup Strategy

```bash
# Backup Elasticsearch data
docker-compose exec elasticsearch /usr/share/elasticsearch/bin/elasticsearch-snapshot

# Backup configuration
tar -czf config-backup.tar.gz .env configs/

# Backup processed data
tar -czf data-backup.tar.gz data/processed/
```

---

## 🔒 Security Best Practices

### 1. Secure Elasticsearch
- Enable authentication (xpack.security)
- Use strong passwords
- Restrict network access
- Enable SSL/TLS

### 2. API Security
- Implement rate limiting
- Add API key authentication
- Validate all inputs
- Enable CORS only for trusted domains
- Use HTTPS only

### 3. Server Security
- Keep system updated
- Configure firewall (UFW/iptables)
- Use SSH keys (disable password auth)
- Regular security audits

### 4. Monitoring
- Setup log aggregation (ELK Stack)
- Configure alerts for errors
- Monitor disk space
- Track API response times

---

## 🔧 Performance Optimization

### 1. Elasticsearch Tuning

```yaml
# In elasticsearch.yml
indices.memory.index_buffer_size: 30%
thread_pool.search.queue_size: 2000
index.refresh_interval: 30s
```

### 2. API Optimization

```python
# Use connection pooling
# Enable response caching
# Batch embedding generation
# Async operations where possible
```

### 3. Model Optimization

- Use quantized models for faster inference
- GPU acceleration if available
- Batch processing for embeddings
- Cache frequently used embeddings

### 4. Load Balancing

- Multiple API worker processes
- Nginx load balancing
- Redis caching layer
- CDN for frontend assets

---

## 🐛 Troubleshooting

### API Not Starting

```bash
# Check logs
docker-compose logs api

# Common issues:
# - Port already in use
# - Elasticsearch not ready
# - Missing dependencies
```

### Search Not Working

```bash
# Check Elasticsearch
curl localhost:9201/_cat/indices?v

# Verify indices exist
# Check document counts
# Review API logs for errors
```

### Slow Response Times

```bash
# Check Elasticsearch performance
curl localhost:9201/_nodes/stats?pretty

# Monitor CPU/Memory usage
docker stats

# Review query complexity
# Consider caching
```

### Out of Memory

```bash
# Increase Docker memory limits
# Reduce worker processes
# Optimize Elasticsearch heap size
# Clear old logs
```

---

## 📈 Scaling Strategy

### Horizontal Scaling

1. **Multiple API instances**
   - Load balancer (Nginx/HAProxy)
   - Shared Elasticsearch cluster
   - Redis session store

2. **Elasticsearch Cluster**
   - Multi-node setup
   - Sharding strategy
   - Replica configuration

3. **Caching Layer**
   - Redis for search results
   - CDN for static assets
   - Browser caching headers

### Vertical Scaling

1. **Increase Resources**
   - More RAM for Elasticsearch
   - Faster CPUs
   - SSD storage
   - GPU for inference

---

## 🎯 Production Checklist

Before going live:

- [ ] Run full integration test suite
- [ ] Load test with expected traffic
- [ ] Verify backup procedures
- [ ] Test disaster recovery
- [ ] Setup monitoring and alerts
- [ ] Configure log aggregation
- [ ] Security audit completed
- [ ] SSL certificates installed
- [ ] Domain DNS configured
- [ ] Documentation updated
- [ ] User acceptance testing passed

---

## 📞 Support & Maintenance

### Regular Maintenance Tasks

**Daily:**
- Check system health
- Monitor error logs
- Verify backup completion

**Weekly:**
- Review performance metrics
- Update dependencies (security patches)
- Optimize slow queries

**Monthly:**
- Full system backup
- Security audit
- Capacity planning review
- Update documentation

### Incident Response

1. **Monitor alerts** - Setup automated alerts
2. **Log analysis** - Centralized logging
3. **Quick rollback** - Keep previous versions
4. **Status page** - Communicate with users
5. **Post-mortem** - Document and improve

---

## 📚 Additional Resources

- [Elasticsearch Production Checklist](https://www.elastic.co/guide/en/elasticsearch/reference/current/setup.html)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [Nginx Optimization](https://www.nginx.com/blog/tuning-nginx/)

---

**Deployment completed successfully! 🎉**

Monitor the system and iterate based on real-world usage patterns.
