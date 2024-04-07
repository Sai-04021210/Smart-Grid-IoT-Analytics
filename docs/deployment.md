# Smart Grid IoT Analytics - Deployment Guide

## Overview

This guide covers the deployment of the Smart Grid IoT Analytics platform using Docker Compose for development and production environments.

## Prerequisites

- Docker 26.x or later
- Docker Compose 2.x or later
- Git
- 8GB+ RAM recommended
- 20GB+ disk space

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Smart-Grid-IoT-Analytics
```

### 2. Environment Configuration

Copy the environment template:

```bash
cp .env.example .env
```

Edit `.env` file with your configuration:

```bash
# Database Configuration
POSTGRES_PASSWORD=your_secure_password
OPENWEATHER_API_KEY=your_api_key

# Security
JWT_SECRET_KEY=your_jwt_secret_key
NODE_RED_CREDENTIAL_SECRET=your_node_red_secret
```

### 3. Start Services

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Access Applications

- **Web Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Node-RED Dashboard**: http://localhost:1880
- **PostgreSQL**: localhost:5432
- **MQTT Broker**: localhost:1883

## Service Architecture

### Core Services

1. **PostgreSQL Database** (Port 5432)
   - Primary data storage
   - TimescaleDB for time-series optimization
   - Automated backups

2. **MQTT Broker** (Ports 1883, 9001)
   - Eclipse Mosquitto
   - WebSocket support for web clients
   - Message persistence

3. **Redis Cache** (Port 6379)
   - Session management
   - API response caching
   - Real-time data buffering

4. **FastAPI Backend** (Port 8000)
   - REST API endpoints
   - ML model serving
   - Real-time data processing

5. **React Frontend** (Port 3000)
   - Web dashboard
   - Real-time visualizations
   - User interface

6. **Node-RED** (Port 1880)
   - IoT data flows
   - Dashboard creation
   - Device integration

### Optional Services

7. **ML Training Service**
   - Model retraining
   - Batch processing
   - Scheduled tasks

## Production Deployment

### 1. Security Configuration

Update production settings:

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  postgres:
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  mqtt-broker:
    volumes:
      - ./mqtt-broker/mosquitto.prod.conf:/mosquitto/config/mosquitto.conf
    restart: unless-stopped

  backend:
    environment:
      - DEBUG=false
      - ENVIRONMENT=production
    restart: unless-stopped
```

### 2. SSL/TLS Configuration

Configure HTTPS with Let's Encrypt:

```yaml
  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - frontend
      - backend
```

### 3. Database Backup

Automated backup script:

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

docker exec smartgrid_postgres pg_dump -U smartgrid_user smartgrid > \
  ${BACKUP_DIR}/smartgrid_${DATE}.sql

# Keep only last 7 days
find ${BACKUP_DIR} -name "smartgrid_*.sql" -mtime +7 -delete
```

### 4. Monitoring Setup

Add monitoring services:

```yaml
  prometheus:
    image: prom/prometheus:v2.45.0
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:10.0.0
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
```

## Scaling Configuration

### Horizontal Scaling

Scale backend services:

```bash
# Scale backend instances
docker-compose up -d --scale backend=3

# Load balancer configuration
docker-compose -f docker-compose.yml -f docker-compose.scale.yml up -d
```

### Database Optimization

PostgreSQL tuning for production:

```sql
-- postgresql.conf optimizations
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
```

## Health Checks

### Service Health Monitoring

```bash
# Check all services
docker-compose ps

# Individual service health
curl http://localhost:8000/health
curl http://localhost:3000
curl http://localhost:1880

# Database connection
docker exec smartgrid_postgres pg_isready -U smartgrid_user
```

### Automated Health Checks

```yaml
# Health check configuration
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check port usage
   netstat -tulpn | grep :8000
   
   # Change ports in docker-compose.yml
   ports:
     - "8001:8000"  # Use different external port
   ```

2. **Database Connection Issues**
   ```bash
   # Check database logs
   docker-compose logs postgres
   
   # Test connection
   docker exec -it smartgrid_postgres psql -U smartgrid_user -d smartgrid
   ```

3. **MQTT Connection Problems**
   ```bash
   # Check MQTT broker logs
   docker-compose logs mqtt-broker
   
   # Test MQTT connection
   mosquitto_pub -h localhost -t test -m "hello"
   mosquitto_sub -h localhost -t test
   ```

4. **Memory Issues**
   ```bash
   # Check memory usage
   docker stats
   
   # Increase memory limits
   deploy:
     resources:
       limits:
         memory: 2G
   ```

### Log Management

```bash
# View logs for all services
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend

# Log rotation configuration
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## Performance Optimization

### Database Performance

1. **Indexing Strategy**
   ```sql
   -- Create indexes for time-series queries
   CREATE INDEX CONCURRENTLY idx_energy_readings_timestamp_meter 
   ON energy_readings(timestamp, meter_id);
   
   -- Partition large tables
   CREATE TABLE energy_readings_2024_04 PARTITION OF energy_readings
   FOR VALUES FROM ('2024-04-01') TO ('2024-05-01');
   ```

2. **Connection Pooling**
   ```python
   # SQLAlchemy configuration
   engine = create_engine(
       DATABASE_URL,
       pool_size=20,
       max_overflow=30,
       pool_pre_ping=True
   )
   ```

### API Performance

1. **Caching Strategy**
   ```python
   # Redis caching
   @cache(expire=300)  # 5 minutes
   def get_energy_summary():
       return calculate_summary()
   ```

2. **Rate Limiting**
   ```python
   # API rate limiting
   @limiter.limit("100/hour")
   def api_endpoint():
       return response
   ```

## Backup and Recovery

### Database Backup

```bash
# Full backup
docker exec smartgrid_postgres pg_dump -U smartgrid_user smartgrid > backup.sql

# Restore
docker exec -i smartgrid_postgres psql -U smartgrid_user smartgrid < backup.sql
```

### Configuration Backup

```bash
# Backup configuration files
tar -czf config_backup.tar.gz \
  .env \
  docker-compose.yml \
  mqtt-broker/ \
  nginx/ \
  node-red/
```

## Security Best Practices

1. **Environment Variables**
   - Never commit `.env` files
   - Use strong passwords
   - Rotate secrets regularly

2. **Network Security**
   - Use internal networks
   - Limit exposed ports
   - Enable firewall rules

3. **Container Security**
   - Use non-root users
   - Regular image updates
   - Security scanning

4. **API Security**
   - Enable authentication
   - Use HTTPS in production
   - Implement rate limiting

## Maintenance

### Regular Tasks

1. **Weekly**
   - Check service health
   - Review logs for errors
   - Monitor disk usage

2. **Monthly**
   - Update container images
   - Database maintenance
   - Security updates

3. **Quarterly**
   - Performance review
   - Capacity planning
   - Disaster recovery testing

### Update Procedure

```bash
# Update images
docker-compose pull

# Restart services
docker-compose down
docker-compose up -d

# Verify deployment
docker-compose ps
curl http://localhost:8000/health
```
