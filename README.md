# smolink
# 🔗 Smolink

> A production-inspired distributed URL shortener built from first principles.

**Smolink** is an ongoing backend engineering project that documents the journey of building a scalable URL shortening service from scratch. Rather than being a tutorial clone, the goal is to understand and implement the concepts behind modern backend systems—including API design, authentication, caching, deployment, observability, and distributed architectures.

The project is being developed incrementally, with each milestone introducing a new engineering concept and integrating it into the existing system.

---

## 🎯 Objectives

Smolink is designed to serve as a comprehensive learning project covering:

- Backend Engineering
- REST API Design
- Database Design
- Authentication & Authorization
- Caching Strategies
- Containerization
- CI/CD
- Cloud Deployment
- Observability
- Distributed Systems
- Production Best Practices

---

## 🛠 Planned Tech Stack

### Backend
- Python
- FastAPI
- Pydantic
- SQLAlchemy

### Database
- PostgreSQL

### Caching
- Redis

### Authentication
- JWT

### DevOps
- Docker
- Docker Compose
- Nginx
- GitHub Actions

### Monitoring
- Prometheus
- Grafana

### Cloud
- Oracle Cloud (Ubuntu VM)

### Future
- Kafka
- Horizontal Scaling
- Load Balancing
- Kubernetes (Experimental)

---

# Roadmap

## Phase 1
- [ ] Project initialization
- [ ] FastAPI setup
- [ ] API structure
- [ ] Health endpoint

## Phase 2
- [ ] URL shortening API
- [ ] Redirect endpoint
- [ ] URL validation
- [ ] Short code generation

## Phase 3
- [ ] PostgreSQL integration
- [ ] SQLAlchemy
- [ ] Database migrations

## Phase 4
- [ ] User registration
- [ ] JWT authentication
- [ ] Protected routes

## Phase 5
- [ ] Redis caching
- [ ] Cache-aside pattern
- [ ] Cache invalidation

## Phase 6
- [ ] Rate limiting
- [ ] Click analytics
- [ ] Background tasks

## Phase 7
- [ ] Docker
- [ ] Docker Compose
- [ ] Production configuration

## Phase 8
- [ ] CI/CD
- [ ] Automated testing
- [ ] GitHub Actions

## Phase 9
- [ ] Cloud deployment
- [ ] Nginx reverse proxy
- [ ] HTTPS

## Phase 10
- [ ] Kafka
- [ ] Analytics pipeline
- [ ] Monitoring
- [ ] Prometheus
- [ ] Grafana

## Phase 11
- [ ] Multiple FastAPI instances
- [ ] Load balancing
- [ ] Horizontal scaling

---

# Target Architecture

```text
                 Internet
                      │
                 Nginx
                      │
              Load Balancer
                      │
      ┌───────────────┴───────────────┐
      │                               │
  FastAPI Instance              FastAPI Instance
      │                               │
      └───────────────┬───────────────┘
                      │
                   Redis
                      │
                PostgreSQL
                      │
                    Kafka
                      │
             Analytics Worker
                      │
         Prometheus + Grafana
```

---

# Project Philosophy

This repository is intentionally built **incrementally**.

Instead of implementing every technology upfront, each feature is introduced only after understanding the underlying engineering concepts. Every major milestone is reflected in the commit history, allowing the repository to document the evolution from a simple REST API to a production-inspired distributed system.

---

# Current Status

🚧 **Under Active Development**

The project has recently been started. Features, architecture, and documentation will evolve alongside implementation.

---

# Learning Goals

Through Smolink, I aim to gain hands-on experience with:

- Designing clean REST APIs
- Building scalable backend services
- Database modeling
- Authentication systems
- Redis caching
- Dockerized applications
- CI/CD pipelines
- Linux server administration
- Cloud deployment
- Monitoring and observability
- Distributed system fundamentals

---

## License

MIT License