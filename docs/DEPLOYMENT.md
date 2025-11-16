# PersonaSay Deployment Guide

This guide covers deploying PersonaSay locally with Docker or in production with Kubernetes (K8s).

## Table of Contents
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Environment Variables](#environment-variables)
- [Production Best Practices](#production-best-practices)

---

## Local Development

### Prerequisites
- Node.js 18+
- Python 3.11+
- OpenAI API Key

### Setup

#### Quick Setup with Script (Recommended)

The easiest way to set up PersonaSay locally is using the provided setup script:

1. **Clone and Run Setup**
   ```bash
   git clone https://github.com/yourusername/personasay.git
   cd personasay
   ./setup.sh
   ```

   The script will:
   - Check for required prerequisites (Python 3.11+, Node.js 18+, npm)
   - Create and configure Python virtual environment
   - Install all backend dependencies (production + dev)
   - Create `.env` file from template
   - Install all frontend dependencies
   - Set up required directories (data, logs)

2. **Configure Environment**
   ```bash
   # Edit backend/.env and add your OPENAI_API_KEY
   nano backend/.env
   # Set: OPENAI_API_KEY=sk-your-key-here
   ```

3. **Run**
   ```bash
   # Terminal 1 - Backend
   cd backend
   source venv/bin/activate
   python main.py
   
   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

4. **Access**: `http://localhost:5173`

#### Manual Setup

If you prefer manual control or the script doesn't work on your system:

1. **Clone and Install**
   ```bash
   git clone https://github.com/yourusername/personasay.git
   cd personasay
   
   # Backend
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r config/requirements.txt
   
   # Frontend
   cd ../frontend
   npm install
   ```

2. **Configure Environment**
   ```bash
   cd backend
   cp config/config.env.example config.env
   # Edit config.env and set your OPENAI_API_KEY
   ```

3. **Run**
   ```bash
   # Terminal 1 - Backend
   cd backend
   source venv/bin/activate
   python main.py
   
   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

4. **Access**: `http://localhost:5173`

---

## Docker Deployment

### Quick Start with Docker Compose

1. **Set Environment Variables**
   ```bash
   export OPENAI_API_KEY="sk-your-api-key-here"
   export DEBUG="false"
   ```

2. **Build and Run**
   ```bash
   docker compose up -d
   ```

3. **Access**: `http://localhost`

4. **View Logs**
   ```bash
   # All services
   docker compose logs -f
   
   # Backend only
   docker compose logs -f backend
   
   # Frontend only
   docker compose logs -f frontend
   ```

5. **Stop**
   ```bash
   docker compose down
   ```

> **Note**: If using Docker Compose V1 (older version), replace `docker compose` with `docker-compose`.

### Build Individual Images

**Backend:**
```bash
cd backend
docker build -t personasay/backend:1.0.0 .
docker run -d -p 8001:8001 \
  -e OPENAI_API_KEY="sk-your-api-key" \
  personasay/backend:1.0.0
```

**Frontend:**
```bash
cd frontend
docker build -t personasay/frontend:1.0.0 .
docker run -d -p 80:80 personasay/frontend:1.0.0
```

### Push to Registry

```bash
# Tag for your registry
docker tag personasay/backend:1.0.0 your-registry.com/personasay/backend:1.0.0
docker tag personasay/frontend:1.0.0 your-registry.com/personasay/frontend:1.0.0

# Push
docker push your-registry.com/personasay/backend:1.0.0
docker push your-registry.com/personasay/frontend:1.0.0
```

---

## Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (1.24+)
- kubectl configured
- Helm 3.x installed
- Docker images pushed to a registry

### Install with Helm

1. **Create Namespace**
   ```bash
   kubectl create namespace personasay
   ```

2. **Create Secret for OpenAI API Key**
   ```bash
   kubectl create secret generic personasay-secrets \
     --from-literal=OPENAI_API_KEY="sk-your-api-key-here" \
     -n personasay
   ```

3. **Install Chart**
   ```bash
   helm install personasay ./helm/personasay \
     --namespace personasay \
     --set global.env.OPENAI_API_KEY="sk-your-api-key-here" \
     --set backend.image.repository="your-registry.com/personasay/backend" \
     --set frontend.image.repository="your-registry.com/personasay/frontend"
   ```

### Custom Values File

Create `values-production.yaml`:

```yaml
global:
  env:
    OPENAI_API_KEY: "sk-your-api-key-here"
    DEBUG: "false"
    ENVIRONMENT: "production"

backend:
  replicaCount: 3
  image:
    repository: your-registry.com/personasay/backend
    tag: "1.0.0"
  resources:
    limits:
      cpu: 2000m
      memory: 2Gi
    requests:
      cpu: 500m
      memory: 512Mi
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10

frontend:
  replicaCount: 2
  image:
    repository: your-registry.com/personasay/frontend
    tag: "1.0.0"
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 5

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: personasay.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
          backend: frontend
        - path: /api
          pathType: Prefix
          backend: backend
  tls:
    - secretName: personasay-tls
      hosts:
        - personasay.yourdomain.com
```

Deploy with custom values:
```bash
helm install personasay ./helm/personasay \
  --namespace personasay \
  -f values-production.yaml
```

### Upgrade Deployment

```bash
helm upgrade personasay ./helm/personasay \
  --namespace personasay \
  -f values-production.yaml
```

### Verify Deployment

```bash
# Check pods
kubectl get pods -n personasay

# Check services
kubectl get svc -n personasay

# Check ingress
kubectl get ingress -n personasay

# View logs
kubectl logs -n personasay -l app.kubernetes.io/component=backend -f
kubectl logs -n personasay -l app.kubernetes.io/component=frontend -f
```

### Access Application

**Via Port Forward (Development):**
```bash
kubectl port-forward -n personasay svc/personasay-frontend 8080:80
# Access at http://localhost:8080
```

**Via Ingress (Production):**
Access at your configured domain: `https://personasay.yourdomain.com`

### Uninstall

```bash
helm uninstall personasay --namespace personasay
kubectl delete namespace personasay
```

---

## Environment Variables

All environment variables can be configured via Helm's `global.env` values:

### Required Variables

| Variable | Description | Default | Override Example |
|----------|-------------|---------|------------------|
| `OPENAI_API_KEY` | OpenAI API key (required) | `""` | `--set global.env.OPENAI_API_KEY="sk-..."` |

### Optional Variables

| Variable | Description | Default | Override Example |
|----------|-------------|---------|------------------|
| `PORT` | Backend server port | `8001` | `--set global.env.PORT="8001"` |
| `HOST` | Backend bind address | `0.0.0.0` | `--set global.env.HOST="0.0.0.0"` |
| `DEBUG` | Enable debug mode | `false` | `--set global.env.DEBUG="true"` |
| `DATABASE_URL` | Database connection | SQLite | `--set global.env.DATABASE_URL="postgresql://..."` |
| `REDIS_URL` | Redis cache URL | `""` | `--set global.env.REDIS_URL="redis://..."` |
| `ENVIRONMENT` | Environment name | `production` | `--set global.env.ENVIRONMENT="staging"` |

### Helm Override Examples

**Single Variable:**
```bash
helm install personasay ./helm/personasay \
  --set global.env.OPENAI_API_KEY="sk-your-key"
```

**Multiple Variables:**
```bash
helm install personasay ./helm/personasay \
  --set global.env.OPENAI_API_KEY="sk-your-key" \
  --set global.env.DEBUG="false" \
  --set global.env.ENVIRONMENT="production"
```

**Via Values File:**
```yaml
# values.yaml
global:
  env:
    OPENAI_API_KEY: "sk-your-key"
    DEBUG: "false"
    DATABASE_URL: "postgresql://user:pass@postgres:5432/personasay"
    REDIS_URL: "redis://redis:6379"
    ENVIRONMENT: "production"
```

```bash
helm install personasay ./helm/personasay -f values.yaml
```

### Kubernetes Secrets (Recommended for Production)

For sensitive data like API keys, use Kubernetes secrets:

```bash
# Create secret
kubectl create secret generic personasay-api-keys \
  --from-literal=OPENAI_API_KEY="sk-your-key" \
  -n personasay

# Update deployment to use secret
kubectl edit deployment personasay-backend -n personasay
```

Add to deployment spec:
```yaml
envFrom:
- secretRef:
    name: personasay-api-keys
```

---

## Production Best Practices

### Security

1. **Never commit secrets** to version control
   ```bash
   # Use .env files (already in .gitignore)
   echo "OPENAI_API_KEY=sk-..." > backend/config.env
   ```

2. **Use secret management** in Kubernetes
   - Kubernetes Secrets
   - External Secrets Operator
   - HashiCorp Vault
   - AWS Secrets Manager / GCP Secret Manager

3. **Enable RBAC** and network policies
   ```yaml
   # Network policy example
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: personasay-backend
   spec:
     podSelector:
       matchLabels:
         app.kubernetes.io/component: backend
     ingress:
     - from:
       - podSelector:
           matchLabels:
             app.kubernetes.io/component: frontend
   ```

4. **Use TLS/HTTPS** with cert-manager
   ```bash
   # Install cert-manager
   kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
   
   # Create ClusterIssuer
   kubectl apply -f - <<EOF
   apiVersion: cert-manager.io/v1
   kind: ClusterIssuer
   metadata:
     name: letsencrypt-prod
   spec:
     acme:
       server: https://acme-v02.api.letsencrypt.org/directory
       email: your-email@example.com
       privateKeySecretRef:
         name: letsencrypt-prod
       solvers:
       - http01:
           ingress:
             class: nginx
   EOF
   ```

### Scalability

1. **Enable autoscaling**
   ```yaml
   backend:
     autoscaling:
       enabled: true
       minReplicas: 2
       maxReplicas: 10
       targetCPUUtilizationPercentage: 70
   ```

2. **Resource limits**
   ```yaml
   backend:
     resources:
       limits:
         cpu: 2000m
         memory: 2Gi
       requests:
         cpu: 500m
         memory: 512Mi
   ```

3. **Pod disruption budgets**
   ```yaml
   apiVersion: policy/v1
   kind: PodDisruptionBudget
   metadata:
     name: personasay-backend-pdb
   spec:
     minAvailable: 1
     selector:
       matchLabels:
         app.kubernetes.io/component: backend
   ```

### Monitoring

1. **Health checks** (already configured)
   - Liveness probes: `/health`
   - Readiness probes: `/health`

2. **Prometheus metrics** (optional)
   ```bash
   helm upgrade personasay ./helm/personasay \
     --set monitoring.enabled=true \
     --set monitoring.serviceMonitor.enabled=true
   ```

3. **Logging**
   ```bash
   # View aggregated logs
   kubectl logs -n personasay -l app.kubernetes.io/name=personasay --tail=100 -f
   
   # Export to log aggregator (Loki, ELK, etc.)
   ```

### High Availability

1. **Multiple replicas**
   ```yaml
   backend:
     replicaCount: 3
   frontend:
     replicaCount: 2
   ```

2. **Anti-affinity rules**
   ```yaml
   backend:
     affinity:
       podAntiAffinity:
         preferredDuringSchedulingIgnoredDuringExecution:
         - weight: 100
           podAffinityTerm:
             labelSelector:
               matchLabels:
                 app.kubernetes.io/component: backend
             topologyKey: kubernetes.io/hostname
   ```

3. **Use managed services**
   - Managed Kubernetes (GKE, EKS, AKS)
   - Managed databases (RDS, Cloud SQL)
   - Managed caching (ElastiCache, Memorystore)

### Cost Optimization

1. **Right-size resources** based on actual usage
2. **Use spot/preemptible instances** for non-critical workloads
3. **Enable autoscaling** to scale down during low traffic
4. **Use `gpt-4o-mini`** for lower OpenAI costs (modify `working_server.py`)

---

## Troubleshooting

### Docker Issues

**Problem: Container exits immediately**
```bash
# Check logs
docker logs personasay-backend
docker logs personasay-frontend

# Common fix: Missing env variables
docker run -e OPENAI_API_KEY="sk-..." personasay/backend:1.0.0
```

### Kubernetes Issues

**Problem: Pods not starting**
```bash
# Check pod status
kubectl describe pod -n personasay <pod-name>

# Check events
kubectl get events -n personasay --sort-by='.lastTimestamp'

# Common fixes:
# 1. Image pull errors - check image repository and credentials
# 2. Missing secrets - create OPENAI_API_KEY secret
# 3. Resource constraints - increase requests/limits
```

**Problem: Cannot access application**
```bash
# Check services
kubectl get svc -n personasay

# Check ingress
kubectl describe ingress -n personasay personasay

# Test internal connectivity
kubectl run -n personasay curl-test --image=curlimages/curl -it --rm -- sh
curl http://personasay-backend:8001/health
curl http://personasay-frontend/health
```

### Performance Issues

1. **Increase resources**
   ```bash
   helm upgrade personasay ./helm/personasay \
     --set backend.resources.limits.cpu=4000m \
     --set backend.resources.limits.memory=4Gi
   ```

2. **Enable autoscaling**
   ```bash
   helm upgrade personasay ./helm/personasay \
     --set backend.autoscaling.enabled=true
   ```

3. **Check OpenAI rate limits**
   - Monitor OpenAI usage dashboard
   - Implement request queuing/throttling

---

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/personasay/issues)
- **Documentation**: [README.md](../README.md)
- **Email**: your-email@example.com

---

**Built for local development and production Kubernetes deployments**

