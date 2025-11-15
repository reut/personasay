# PersonaSay Helm Chart

This Helm chart deploys PersonaSay, an AI-powered multi-persona product feedback platform, to Kubernetes.

## TL;DR

```bash
helm install personasay ./helm/personasay \
 --namespace personasay \
 --create-namespace \
 --set global.env.OPENAI_API_KEY="sk-your-api-key"
```

## Prerequisites

- Kubernetes 1.24+
- Helm 3.x
- OpenAI API Key
- Docker images pushed to accessible registry

## Installing the Chart

### Quick Install (Development)

```bash
helm install personasay ./helm/personasay \
 --namespace personasay \
 --create-namespace \
 --set global.env.OPENAI_API_KEY="sk-your-api-key" \
 -f values-development.yaml
```

### Production Install

1. **Update production values**
 
 Edit `values-production.yaml`:
 ```yaml
 global:
 env:
 OPENAI_API_KEY: "sk-your-key" # Or use K8s secret
 
 backend:
 image:
 repository: your-registry.com/personasay/backend
 tag: "1.0.0"
 
 frontend:
 image:
 repository: your-registry.com/personasay/frontend
 tag: "1.0.0"
 
 ingress:
 enabled: true
 hosts:
 - host: personasay.yourdomain.com
 ```

2. **Install**
 ```bash
 helm install personasay ./helm/personasay \
 --namespace personasay \
 --create-namespace \
 -f values-production.yaml
 ```

## Uninstalling the Chart

```bash
helm uninstall personasay --namespace personasay
```

## Configuration

### Global Environment Variables

All environment variables are exposed via `global.env` and can be overridden:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.env.OPENAI_API_KEY` | OpenAI API key (required) | `""` |
| `global.env.PORT` | Backend server port | `"8001"` |
| `global.env.HOST` | Backend bind address | `"0.0.0.0"` |
| `global.env.DEBUG` | Enable debug mode | `"false"` |
| `global.env.DATABASE_URL` | Database connection string | `"sqlite:///./personasay.db"` |
| `global.env.REDIS_URL` | Redis cache URL | `""` |
| `global.env.ENVIRONMENT` | Environment identifier | `"production"` |

### Backend Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `backend.enabled` | Enable backend deployment | `true` |
| `backend.replicaCount` | Number of replicas | `2` |
| `backend.image.repository` | Backend image repository | `personasay/backend` |
| `backend.image.tag` | Backend image tag | `"1.0.0"` |
| `backend.image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `backend.resources.limits.cpu` | CPU limit | `1000m` |
| `backend.resources.limits.memory` | Memory limit | `1Gi` |
| `backend.resources.requests.cpu` | CPU request | `250m` |
| `backend.resources.requests.memory` | Memory request | `256Mi` |
| `backend.autoscaling.enabled` | Enable HPA | `false` |
| `backend.autoscaling.minReplicas` | Minimum replicas | `2` |
| `backend.autoscaling.maxReplicas` | Maximum replicas | `10` |
| `backend.service.type` | Service type | `ClusterIP` |
| `backend.service.port` | Service port | `8001` |

### Frontend Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `frontend.enabled` | Enable frontend deployment | `true` |
| `frontend.replicaCount` | Number of replicas | `2` |
| `frontend.image.repository` | Frontend image repository | `personasay/frontend` |
| `frontend.image.tag` | Frontend image tag | `"1.0.0"` |
| `frontend.image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `frontend.resources.limits.cpu` | CPU limit | `500m` |
| `frontend.resources.limits.memory` | Memory limit | `512Mi` |
| `frontend.resources.requests.cpu` | CPU request | `100m` |
| `frontend.resources.requests.memory` | Memory request | `128Mi` |
| `frontend.autoscaling.enabled` | Enable HPA | `false` |
| `frontend.service.type` | Service type | `ClusterIP` |
| `frontend.service.port` | Service port | `80` |

### Ingress Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ingress.enabled` | Enable ingress | `false` |
| `ingress.className` | Ingress class name | `"nginx"` |
| `ingress.annotations` | Ingress annotations | See values.yaml |
| `ingress.hosts` | Ingress hosts configuration | See values.yaml |
| `ingress.tls` | TLS configuration | `[]` |

## Examples

### Override Single Variable

```bash
helm install personasay ./helm/personasay \
 --set global.env.DEBUG="true"
```

### Override Multiple Variables

```bash
helm install personasay ./helm/personasay \
 --set global.env.OPENAI_API_KEY="sk-key" \
 --set global.env.DEBUG="false" \
 --set backend.replicaCount=3 \
 --set frontend.replicaCount=2
```

### Use Custom Values File

```bash
# Create my-values.yaml
cat > my-values.yaml <<EOF
global:
 env:
 OPENAI_API_KEY: "sk-your-key"
 DEBUG: "false"

backend:
 replicaCount: 3
 autoscaling:
 enabled: true
 minReplicas: 3
 maxReplicas: 10

ingress:
 enabled: true
 hosts:
 - host: personasay.example.com
EOF

# Install with custom values
helm install personasay ./helm/personasay -f my-values.yaml
```

### Enable Auto-scaling

```bash
helm install personasay ./helm/personasay \
 --set backend.autoscaling.enabled=true \
 --set backend.autoscaling.minReplicas=2 \
 --set backend.autoscaling.maxReplicas=10 \
 --set frontend.autoscaling.enabled=true
```

### Use External Database

```bash
helm install personasay ./helm/personasay \
 --set global.env.DATABASE_URL="postgresql://user:pass@postgres:5432/personasay" \
 --set postgresql.enabled=true
```

### Enable Ingress with TLS

```bash
helm install personasay ./helm/personasay \
 --set ingress.enabled=true \
 --set ingress.hosts[0].host="personasay.yourdomain.com" \
 --set ingress.tls[0].secretName="personasay-tls" \
 --set ingress.tls[0].hosts[0]="personasay.yourdomain.com"
```

## Upgrading

### Upgrade with New Values

```bash
helm upgrade personasay ./helm/personasay \
 --namespace personasay \
 -f values-production.yaml
```

### Upgrade Single Value

```bash
helm upgrade personasay ./helm/personasay \
 --set backend.image.tag="1.1.0"
```

### Rollback

```bash
helm rollback personasay --namespace personasay
```

## Monitoring

### Check Deployment Status

```bash
helm status personasay --namespace personasay
```

### View Pods

```bash
kubectl get pods -n personasay
```

### View Logs

```bash
# Backend logs
kubectl logs -n personasay -l app.kubernetes.io/component=backend -f

# Frontend logs
kubectl logs -n personasay -l app.kubernetes.io/component=frontend -f
```

### Port Forward (for testing)

```bash
kubectl port-forward -n personasay svc/personasay-frontend 8080:80
# Access at http://localhost:8080
```

## Troubleshooting

### Pods Not Starting

```bash
# Describe pod for events
kubectl describe pod -n personasay <pod-name>

# Check events
kubectl get events -n personasay --sort-by='.lastTimestamp'
```

### Common Issues

**Image Pull Errors**
- Verify image repository and tag are correct
- Check image pull secrets if using private registry
- Ensure images exist in registry

**Missing API Key**
```bash
# Check if secret exists
kubectl get secrets -n personasay

# Create secret manually
kubectl create secret generic personasay-secrets \
 --from-literal=OPENAI_API_KEY="sk-key" \
 -n personasay
```

**Service Not Accessible**
```bash
# Check services
kubectl get svc -n personasay

# Check ingress
kubectl get ingress -n personasay
kubectl describe ingress personasay -n personasay
```

## Security

### Using Kubernetes Secrets (Recommended)

Instead of passing API key via values:

```bash
# Create secret
kubectl create secret generic personasay-api-key \
 --from-literal=OPENAI_API_KEY="sk-your-key" \
 -n personasay

# Update deployment to use secret
kubectl edit deployment personasay-backend -n personasay
```

Add to pod spec:
```yaml
envFrom:
- secretRef:
 name: personasay-api-key
```

### Using External Secrets Operator

```yaml
secrets:
 externalSecretsOperator:
 enabled: true
 secretStore: "aws-secrets-manager"
```

## Values Files

- `values.yaml` - Default values
- `values-development.yaml` - Development environment
- `values-production.yaml` - Production environment (recommended)

## Support

- Documentation: [../../README.md](../../README.md)
- Deployment Guide: [../../DEPLOYMENT.md](../../DEPLOYMENT.md)
- Issues: https://github.com/yourusername/personasay/issues

## License

MIT License - See [LICENSE](../../LICENSE) for details

