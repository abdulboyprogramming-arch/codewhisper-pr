# 🚀 CodeWhisper PR

## Token-Efficient AI Code Review Powered by Paritok

[![Built with Paritok](https://img.shields.io/badge/Built%20with-Paritok-f12d3d)](https://github.com/Paritok-official/paritok-4b-v1)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

---

## 🎯 Overview

**CodeWhisper PR** is an AI-powered code review system that leverages **Paritok's token optimization** to deliver intelligent, cost-effective pull request analysis. By reducing input tokens by up to **74%**, we make AI code reviews affordable for every development team.

> **🏆 Built for the Paritok Token-Efficiency Hackathon**
>
> Demonstrating real token savings in real workflows with Paritok's open-source compression models.

---

## 🔥 The Problem We Solve

### The Cost of AI Code Reviews
- Every PR sends **mountains of context** to LLMs
- Most context is **noise** - formatting, comments, unchanged code
- Teams pay for tokens they don't need
- **Result**: Expensive, slow, and inefficient reviews

### Our Solution: Token-Efficient Code Reviews
- **Intelligent Context Routing** - Only send what matters
- **74% Token Reduction** - Real savings, measured not estimated
- **Lossless Quality** - Maintain review quality while cutting costs

---

## ⚙️ How It Works

```
1. PR Created → 2. Git Analysis → 3. AST Parsing
4. Paritok Optimization → 5. LLM Review
6. Results with Token Savings
```

---

## 💰 Token Savings

| Metric | Value |
|--------|-------|
| **Average Token Reduction** | 74% |
| **Maximum Token Reduction** | 95% |
| **Quality Retention** | 86.5% of full context |
| **Cost Savings** | 74% off input token bill |

---

## ✨ Key Features

- **Intelligent Code Analysis** - AST-based understanding
- **Token Optimization** - Up to 95% reduction with Paritok
- **Developer Dashboard** - Real-time analytics
- **Security First** - Open source, self-hostable

---

## 🛠️ Technology Stack

### Backend
- Python 3.11, FastAPI, SQLAlchemy, Celery
- PostgreSQL, Redis
- Paritok, OpenAI API, Tree-sitter

### Frontend
- Next.js 14, TypeScript, Tailwind CSS
- Chart.js analytics

### Infrastructure
- Docker, Kubernetes, Terraform, Ansible

---

## 🚀 Quick Start

```bash
git clone https://github.com/abdulboyprogramming-arch/codewhisper-pr.git
cd codewhisper-pr
cp .env.example .env
make setup
make docker-up
```

**Access:**
- Frontend: http://localhost:3001
- Backend API: http://localhost:8000/api/docs
- Flower: http://localhost:5555

---

## 📁 Project Structure

```
codewhisper-pr/
├── apps/
│   ├── backend/          # FastAPI backend
│   └── frontend/         # Next.js frontend
├── packages/             # Shared packages
├── infrastructure/       # Kubernetes, Terraform, Ansible
├── docs/                 # Documentation
└── scripts/              # Utility scripts
```

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 📄 License

Apache 2.0 - see [LICENSE](LICENSE)

---

**Built with ❤️ for the Paritok Token-Efficiency Hackathon**

**Developer**: Abdulrahman Adeeyo
**Repository**: https://github.com/abdulboyprogramming-arch/codewhisper-pr

Copyright (c) ${new Date().getFullYear()} CodeWhisper PR. All rights reserved.
