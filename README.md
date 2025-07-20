# Lnex 🧠⚙️

**Lnex** is a robust, fully containerized AI-driven backend system based on a **microservices architecture**. Each service runs independently and handles specific domains like authentication, learning, AI inference, payments, and communication. The services are coordinated via Docker Compose with a PostgreSQL-backed persistence layer and centralized health checks.

---

## 🌐 Overview

Lnex is designed for **modularity**, **scalability**, and **dev/prod environment separation**. Each service:
- Has its own Dockerfile and environment configuration
- Includes a dedicated PostgreSQL instance
- Implements health checks
- Can be deployed independently or orchestrated together

---

## 📂 Directory Structure

Lnex/
├── Auth-Service/
├── Ai-Service/
├── Communication-Service/
├── Learn-Service/
├── Media-Service/
├── Payment-Service/
├── Micro-Service/ # Service registry and manager
└── configs/
├── docker-compose.yaml # Main orchestrator
├── .env # Global env vars
└── nginx/
├── Dockerfile
├── nginx.conf
└── .dockerignore


---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/lnex.git
cd lnex/configs


2. Configure .env Files
Ensure all environment files exist in the correct paths. The docker-compose.yaml references service-specific and database-specific .env files.

Example (Micro-Service DB env):

../Micro-Service/micro_service/config/ENV/development/db.env

Each service includes:

main.env

Environment-specific files like config/ENV/development/{db, api, secret_keys, api_keys, services}.env

3. Start All Services

docker-compose up --build

You can rebuild only specific services:

docker-compose up --build lnex_auth lnex_learn

🛰️ Services and Ports
Service	Port	Description
lnex_micro	8000	Microservice registry & manager
lnex_auth	8000	User authentication & JWT handling
lnex_learn	8000	Learning platform backend
lnex_payment	8000	Payment processing & billing
lnex_communication	8000	Messaging, emails, notifications
PostgreSQL (each DB)	1111+	Separate DBs per service

All services expose port 8000 internally, and DB ports are mapped from 1111 to 3333.

🐳 Docker Volumes
Shared across services:

lnex_static_volume: Holds static files

lnex_media_volume: Holds media uploads

Service DB data:

lnex_<service>_db_data: Persistent PostgreSQL storage

🛠️ Development
To work on a single service:

bash
Copy
Edit
cd ../Auth-Service
docker build -t lnex-auth-service:v_1.0 .
docker run -p 8000:8000 --env-file auth_service/main.env lnex-auth-service:v_1.0
To check service health:

bash
Copy
Edit
curl http://localhost:8000/health
🧪 Health Checks
Each service defines a health endpoint used in Compose:

yaml
Copy
Edit
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
This ensures proper startup sequencing and auto-restart on failure.

📌 Future Enhancements
 Add AI-Service & Media-Service Compose blocks

 Integrate CI/CD (GitHub Actions)

 Add centralized logging (ELK or Prometheus/Grafana)

 Service discovery (Consul/etcd)

 Kubernetes Helm charts

🤝 Contribution Guidelines
Fork the repository

Create a feature branch (git checkout -b feature/service-x)

Add your changes

Test via Docker Compose

Submit a pull request

🛡️ License
Licensed under the MIT License © 2025 [Your Name or Organization]

📫 Contact
GitHub: your-username

Email: [iradukundafils1@gmail.com]

yaml
Copy
Edit

---

### ✅ What's Next?

Would you like:
- Individual `README.md` templates for each service (like `Auth-Service`, `Learn-Service`, etc.)?
- NGINX configuration included in this doc?
- Markdown badges (CI/CD, Docker, License, etc.) added to the top?

Just say the word!









Ask ChatGPT

