# Production Flask App with Monitoring

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)]()
[![Tests](https://img.shields.io/badge/tests-30%2F30%20passing-brightgreen.svg)]()
[![Security](https://img.shields.io/badge/security-scanned-green.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()

> A real Flask app with Docker, monitoring, backups, and CI/CD. Built to show production-ready development practices.

🌟 **[LIVE DEMO](https://flaskappforcicd.netlify.app/)**

## What This Is

I built this to demonstrate how I approach production applications. It's a Flask web app that includes everything you'd need for a real deployment:

- **Docker containers** for consistent deployment anywhere
- **Prometheus monitoring** to track performance and health
- **Automated backups** so you never lose data
- **GitHub Actions CI/CD** for automated testing and deployment
- **Security scanning** built into the pipeline
- **Beautiful web interface** that actually explains what's running

## Quick Start

```bash
# Clone and run
git clone https://github.com/your-username/zero-to-prod-infra.git
cd zero-to-prod-infra
docker compose up

# Open your browser
open http://localhost:8000
```

That's it. The app will start, Prometheus will begin monitoring, and you can see everything running through the web interface.

## What You'll See

### Live Demo Features
- Professional web interface showcasing the project
- Architecture overview with clean design
- Technical stack explanation
- Quick start guide for developers
- Personal story about why I built this

### When Running Locally
- Real-time system monitoring and metrics
- Interactive Flask application
- Prometheus dashboard with live data
- Automated backup system in action

## The Stack

**Backend:** Python Flask with Gunicorn  
**Frontend:** Bootstrap with live JavaScript updates  
**Monitoring:** Prometheus with custom metrics  
**Deployment:** Docker with multi-stage builds  
**Testing:** Python unittest with 30+ test cases  
**CI/CD:** GitHub Actions with security scanning  
**Backup:** Automated system with rotation  

## Real-World Applications

This pattern works for:
- **Startups** building their first production app
- **Internal tools** at companies (dashboards, admin panels)
- **API services** that need monitoring and reliability
- **Microservices** in larger architectures

## Project Structure

```
├── app/                    # Flask application
│   ├── app.py             # Main app with metrics
│   └── templates/         # Web interface
├── backup/                 # Automated backup system
├── prometheus/            # Monitoring configuration
├── .github/workflows/     # CI/CD pipeline
├── Dockerfile             # Container build
└── docker-compose.yml     # Service orchestration
```

## Testing

```bash
# Run the test suite
python3 test_infrastructure.py

# Or run the interactive demo
python3 final-demo.py
```

All tests pass. The test suite validates every component from the Flask endpoints to the backup system.

## Why I Built This

When applying for development roles, I wanted to show more than just code samples. This demonstrates:

1. **Production thinking** - health checks, monitoring, backups
2. **DevOps skills** - containerization, CI/CD, infrastructure as code
3. **Security awareness** - container hardening, vulnerability scanning
4. **User experience** - clear documentation, interactive interface

It runs entirely locally with no external dependencies or costs.

## Deployment Ready

The app is designed to deploy anywhere:
- **Local development** with Docker Compose
- **Cloud platforms** like AWS, GCP, Azure
- **Kubernetes** clusters
- **Traditional servers** with systemd

All configuration is environment-based, so moving between environments is straightforward.

## Contributing

Found a bug or want to add a feature? Pull requests welcome. The code is structured to be readable and extensible.

## License

MIT License - feel free to use this as a starting point for your own projects.

---

*Built to demonstrate production-ready development practices. Not just another tutorial project.*
