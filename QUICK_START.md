# Quick Start Guide - Banking Docs-as-Code

## Prerequisites
- Docker Desktop or Docker Engine + Docker Compose
- Git
- Python 3.11+ (for local development)
- 8GB+ RAM recommended

## 🚀 Getting Started (5 Minutes)

### 1. Clone and Configure
```bash
git clone https://github.com/Chunkys0up7/DocsRework.git
cd DocsRework

# Copy environment template
cp .env.example .env
```

### 2. Start All Services
```bash
docker-compose up -d
```

This starts:
- ✅ FastAPI Backend (port 8000)
- ✅ Neo4j Knowledge Graph (ports 7474, 7687)
- ✅ Redis Cache (port 6379)
- ✅ RabbitMQ (ports 5672, 15672)
- ✅ Prometheus (port 9091)
- ✅ Grafana (port 3000)

### 3. Verify Services
```bash
# Check API health
curl http://localhost:8000/health

# Check all services
docker-compose ps
```

### 4. Access Web Interfaces

| Service | URL | Credentials |
|---------|-----|-------------|
| API Documentation | http://localhost:8000/api/docs | - |
| Neo4j Browser | http://localhost:7474 | neo4j / banking_secure_password |
| RabbitMQ Management | http://localhost:15672 | guest / guest |
| Grafana Dashboards | http://localhost:3000 | admin / admin |
| Prometheus | http://localhost:9091 | - |

## 📂 Understanding the Structure

```
DocsAsCode/
├── atoms/              # ⚛️ Atomic operations
├── molecules/          # 🧬 Multi-step procedures
├── workflows/          # 🔄 Business processes
├── risks/              # ⚠️ Risk definitions
├── controls/           # 🛡️ Control mechanisms
├── regulations/        # 📜 Regulatory requirements
├── schemas/            # 📋 JSON Schema definitions
├── .github/workflows/  # 🔧 CI/CD pipelines
└── src/                # 💻 Python backend code
```

## 🎯 Common Tasks

### Create a New Atom
```bash
# Copy template
cp atoms/verify-customer-identity.atom.yml atoms/my-new-atom.atom.yml

# Edit the file following the pattern:
# id: atom:my-new-atom:v1.0.0
# version: 1.0.0
# ... (see schema)

# Validate locally
python scripts/validate_against_schema.py \
  --schema schemas/atom-schema.json \
  --file atoms/my-new-atom.atom.yml
```

### Create a Pull Request
```bash
# Create feature branch
git checkout -b feature/new-kyc-atom

# Make changes
# ... edit files ...

# Commit and push
git add .
git commit -m "Add new KYC verification atom"
git push origin feature/new-kyc-atom

# Create PR on GitHub
# CI/CD will automatically:
# ✓ Validate YAML syntax
# ✓ Check schema compliance
# ✓ Validate references
# ✓ Run tests
# ✓ Analyze risks
# ✓ Check compliance
```

### Query the Knowledge Graph
```bash
# Access Neo4j Browser: http://localhost:7474

# Example queries:

# 1. Get all atoms
MATCH (a:Atom) RETURN a LIMIT 10

# 2. Find workflows with high risk
MATCH (w:Workflow)-[:HAS_RISK]->(r:Risk)
WHERE r.residualRisk.score >= 10
RETURN w.name, collect(r.name) as high_risks

# 3. Get control effectiveness
MATCH (c:Control)
RETURN c.name, c.effectiveness.rating
ORDER BY c.effectiveness.rating DESC

# 4. Find compliance gaps
MATCH (reg:Regulation)
WHERE NOT (reg)<-[:ADDRESSES]-(:Control)
RETURN reg.name as uncovered_regulation
```

### Run Tests Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# Run specific test type
pytest tests/atoms/ -v        # Unit tests
pytest tests/molecules/ -v    # Integration tests
pytest tests/workflows/ -v    # E2E tests

# Check coverage
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

## 🔧 Development Workflow

### 1. Make Changes
```bash
git checkout -b feature/my-feature
# Edit files...
```

### 2. Test Locally
```bash
# Validate schemas
python scripts/validate_against_schema.py \
  --schema schemas/atom-schema.json \
  --files "atoms/**/*.atom.yml"

# Run tests
pytest tests/ -v
```

### 3. Commit with Semantic Versioning
When making changes to atoms/molecules/workflows:
- **MAJOR** version (v1.0.0 → v2.0.0): Breaking changes
- **MINOR** version (v1.0.0 → v1.1.0): New features, backwards compatible
- **PATCH** version (v1.0.0 → v1.0.1): Bug fixes

### 4. Submit PR
```bash
git add .
git commit -m "Descriptive commit message"
git push origin feature/my-feature
# Create PR on GitHub
```

### 5. CI/CD Runs Automatically
- ✅ Schema validation
- ✅ Semantic rules
- ✅ Test execution
- ✅ Risk analysis
- ✅ Compliance checks

### 6. After Approval → Auto-Deploy to KG
Once merged to `main`, deployment workflow:
1. Creates backup of current KG state
2. Deploys changes incrementally
3. Validates KG consistency
4. Runs smoke tests
5. Rolls back on failure

## 📊 Monitoring

### View Metrics
```bash
# Prometheus metrics
curl http://localhost:9090/metrics

# API metrics
curl http://localhost:8000/metrics
```

### Grafana Dashboards
1. Go to http://localhost:3000
2. Login: admin / admin
3. Navigate to Dashboards
4. View pre-configured dashboards for:
   - API performance
   - Neo4j metrics
   - Risk scores
   - Compliance status

## 🐛 Troubleshooting

### Services Won't Start
```bash
# Check logs
docker-compose logs -f

# Restart specific service
docker-compose restart app

# Rebuild after code changes
docker-compose up -d --build
```

### Neo4j Connection Issues
```bash
# Verify Neo4j is running
docker-compose ps neo4j

# Check Neo4j logs
docker-compose logs neo4j

# Test connection
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'banking_secure_password')); driver.verify_connectivity(); print('✅ Connected')"
```

### API Errors
```bash
# View API logs
docker-compose logs -f app

# Restart API
docker-compose restart app

# Check API health
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

## 🔐 Security Notes

### Before Production
1. ⚠️ Change all default passwords in `.env`
2. ⚠️ Generate new SECRET_KEY and JWT_SECRET_KEY
3. ⚠️ Configure proper CORS origins
4. ⚠️ Set up TLS/SSL certificates
5. ⚠️ Enable authentication (ENABLE_AUTH=true)
6. ⚠️ Configure proper RBAC rules
7. ⚠️ Set up secrets management (e.g., HashiCorp Vault)
8. ⚠️ Enable audit logging

### Secrets Management
```bash
# NEVER commit these files:
.env
credentials.json
*.pem
*.key
secrets/

# They're in .gitignore already
```

## 📚 Learning Resources

### Essential Reading
1. [README.md](README.md) - Project overview
2. [docs/ONTOLOGY.md](docs/ONTOLOGY.md) - Understand the knowledge model
3. [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) - Current status
4. [schemas/](schemas/) - Review JSON schemas for data models

### Example Files
- [atoms/verify-customer-identity.atom.yml](atoms/verify-customer-identity.atom.yml)
- [molecules/customer-onboarding.molecule.yml](molecules/customer-onboarding.molecule.yml)
- [workflows/retail-account-opening.workflow.yml](workflows/retail-account-opening.workflow.yml)

## 🆘 Need Help?

### Common Questions

**Q: How do I add a new risk?**
```bash
cp risks/identity-fraud.risk.yml risks/my-risk.risk.yml
# Edit following risk-schema.json
```

**Q: How do I link a control to a risk?**
```yaml
# In your risk YAML:
controls:
  - controlRef: control:my-control:v1.0.0
    effectiveness: 85
    mitigationType: preventive
```

**Q: How do I create a molecule from atoms?**
```yaml
# In molecule YAML:
atoms:
  - stepId: step-1
    atomRef: atom:my-atom:v1.0.0
  - stepId: step-2
    atomRef: atom:another-atom:v1.0.0

flow:
  startStep: step-1
  transitions:
    - from: step-1
      to: step-2
    - from: step-2
      to: END
```

**Q: How are risks calculated?**
```
Inherent Risk = Likelihood (1-5) × Impact (1-5)
Residual Risk = Inherent Risk × (1 - ControlEffectiveness%)

Risk Levels:
- 1-4:   Low
- 5-9:   Medium
- 10-16: High
- 17-25: Critical
```

## 🎓 Next Steps

1. ✅ Read the [ONTOLOGY.md](docs/ONTOLOGY.md)
2. ✅ Explore example YAML files
3. ✅ Start Neo4j and run sample queries
4. ✅ Create your first atom
5. ✅ Submit a pull request
6. ✅ Watch CI/CD validation run

## 📞 Support

For issues and questions:
- Check [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) for current status
- Review GitHub Issues
- Contact Platform Engineering team

---

**Happy coding! 🚀**
