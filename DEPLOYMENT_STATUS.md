# CORTEX-CI Platform Status & Operations Guide

**Last Updated:** December 23, 2025

---

## Platform Overview

**CORTEX-CI** is a Government-grade Constraint Intelligence Platform for AI/ML governance, sanctions monitoring, and risk management.

---

## Live Deployment

### URLs
| Service | URL | Status |
|---------|-----|--------|
| **Frontend** | https://cortex.alexandratechlab.com | ✅ Live |
| **API** | https://cortex.alexandratechlab.com/api | ✅ Live |
| **API Health** | https://cortex.alexandratechlab.com/api/health | ✅ Healthy |

### Login Credentials
```
Email:    admin@cortex.io
Password: Admin123!
```

---

## Infrastructure

### Dokploy Deployment
- **Project:** cortex-ci
- **Compose ID:** 0QaRLk1tWGlKwj-6y5zty
- **App Name:** compose-input-solid-state-array-q9m3z5
- **Status:** ✅ Running (composeStatus: done)
- **Auto Deploy:** Enabled (triggers on push to main)

### Running Containers
| Container | Status | Port |
|-----------|--------|------|
| frontend | Up | 80 |
| backend | Up (healthy) | 8000 |
| db (PostgreSQL 16) | Up (healthy) | 5432 |
| redis | Up (healthy) | 6379 |

### Domains Configured (via Traefik)
- `cortex.alexandratechlab.com` → frontend:80
- `cortex.alexandratechlab.com/api/*` → backend:8000 (with path stripping)

---

## GitHub Repository

- **URL:** https://github.com/maanisingh/cortex-ci.git
- **Branch:** main
- **Latest Commit:** 73aa978 - "Add Traefik labels for Dokploy routing"

---

## Database Content

| Entity Type | Count |
|-------------|-------|
| Entities | 64 |
| Constraints | 50 |
| Users | 1 (admin) |

Sample entities include:
- AI/ML Models (Credit Scoring, Fraud Detection, etc.)
- Data Systems (CDP, Feature Store, Data Lake)
- Teams (ML Engineering, AI Ethics Committee)
- Vendors (OpenAI, AWS SageMaker, Anthropic)

---

## API Endpoints

### Authentication
```bash
# Login
curl -X POST https://cortex.alexandratechlab.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@cortex.io","password":"Admin123!"}'
```

### Authenticated Requests
```bash
# Set token from login response
TOKEN="<access_token>"

# Get entities
curl https://cortex.alexandratechlab.com/api/v1/entities \
  -H "Authorization: Bearer $TOKEN"

# Get constraints
curl https://cortex.alexandratechlab.com/api/v1/constraints \
  -H "Authorization: Bearer $TOKEN"

# Get scenarios
curl https://cortex.alexandratechlab.com/api/v1/scenarios \
  -H "Authorization: Bearer $TOKEN"
```

---

## Dokploy Access

### API Key
```
fqmDOfkeSKrhEEBkoLcrIeozmDufqsVqyNJXRtPoYtDKuJADodhLXlKrMJBIkWKC
```

### API Examples
```bash
# Get all projects
curl http://localhost:4000/api/project.all \
  -H "x-api-key: fqmDOfkeSKrhEEBkoLcrIeozmDufqsVqyNJXRtPoYtDKuJADodhLXlKrMJBIkWKC"

# Get compose details
curl "http://localhost:4000/api/compose.one?composeId=0QaRLk1tWGlKwj-6y5zty" \
  -H "x-api-key: fqmDOfkeSKrhEEBkoLcrIeozmDufqsVqyNJXRtPoYtDKuJADodhLXlKrMJBIkWKC"
```

---

## Environment Variables (Dokploy)

```env
POSTGRES_PASSWORD=CortexCI_Secure_2024!
SECRET_KEY=x7K9mP2qR5tW8yB3nF6jL1vC4hA0sE2uN9dG7kI5oQ3mZ8xY
```

---

## Local Project Files

```
/root/cortex-ci/
├── backend/
│   ├── app/              # FastAPI application
│   ├── alembic/          # Database migrations
│   ├── Dockerfile
│   ├── requirements.txt
│   └── populate_data.py  # Demo data script
├── frontend/
│   ├── src/              # React/Vite application
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── docker-compose.dokploy.yml  # Dokploy deployment config
└── .env.example
```

---

## Next Steps / TODO

1. **Dashboard Stats Endpoint** - Returns 404, needs to be implemented or fixed
2. **OpenAPI Docs** - `/api/docs` returns 404, may need to enable Swagger UI
3. **Additional Users** - Currently only 1 admin user exists
4. **Populate More Data** - Run `populate_data.py` to add more demo entities
5. **Monitor Logs** - Check for any runtime errors

---

## Useful Commands

```bash
# Check container status
docker ps --filter "name=q9m3z5"

# View backend logs
docker logs compose-input-solid-state-array-q9m3z5-backend-1 --tail 50

# View frontend logs
docker logs compose-input-solid-state-array-q9m3z5-frontend-1 --tail 50

# Access database
docker exec -it compose-input-solid-state-array-q9m3z5-db-1 psql -U cortex -d cortex_ci

# Redeploy via Dokploy API
curl -X POST "http://localhost:4000/api/compose.deploy" \
  -H "x-api-key: fqmDOfkeSKrhEEBkoLcrIeozmDufqsVqyNJXRtPoYtDKuJADodhLXlKrMJBIkWKC" \
  -H "Content-Type: application/json" \
  -d '{"composeId":"0QaRLk1tWGlKwj-6y5zty"}'
```

---

## Quick Health Check

```bash
curl -s https://cortex.alexandratechlab.com/api/health
# Expected: {"status":"healthy","app":"CORTEX-CI","version":"1.0.0"}
```
