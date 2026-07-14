# Deployment & Infrastructure Configuration Spec

This document details the Docker, Firebase, and local development configurations required to run and deploy the Valo Heuristic Rules Engine platform.

---

## 1. Cloud Infrastructure & Deployment Stage

The application is containerized and designed to run in microservice architectures:
- **Initial Stage:** Deployed on **Firebase Cloud Run** for serverless scaling, auto-scaling to zero, and integration with Firebase Hosting.
- **Scale Stage:** Fully prepared for migration to cloud container platforms such as **AWS ECS/EKS** or **GCP GKE**.

---

## 2. Docker & Compose File Structure

The project code is separated into:
- `/apps/nextjs` (Frontend UI & BFF)
- `/apps/nocobase` (Relational data administration console)

Detailed specifications for each configuration file can be found in the repository root:
- Next.js Dockerfile: `apps/nextjs/Dockerfile`
- NocoBase Dockerfile: `apps/nocobase/Dockerfile`
- Local dev environment: `docker-compose.yml`
- Firebase rewrite config: `firebase.json`
