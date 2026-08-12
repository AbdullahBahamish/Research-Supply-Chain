# API Specification & Reference Guide

This document provides complete, production-grade technical specifications for the **Research Supply Chain** API endpoints.

---

## 🏛️ Odoo Controller Architecture

In standard Odoo framework architecture, API controllers are housed in the **`controllers/`** folder of the module:

```
addons/research_supply_chain/
├── __init__.py          # Imports models and controllers
├── controllers/         # Official Odoo directory for REST/JSON HTTP endpoints
│   ├── __init__.py
│   └── main.py          # API route definitions (@http.route)
```

This is the official, Odoo-recommended location for exposing custom HTTP, JSON-RPC, REST, and webhook interfaces.

---

## 🔒 Authentication & Session Management

All endpoints require user authentication. Odoo utilizes **session-based cookie authentication**.

### 1. Login Endpoint
- **URL**: `/web/session/authenticate`
- **HTTP Method**: `POST`
- **Content-Type**: `application/json`

#### Request Payload
```json
{
  "jsonrpc": "2.0",
  "params": {
    "db": "ODOO_FirstDB",
    "login": "admin",
    "password": "admin"
  }
}
```

#### Successful Response (`200 OK`)
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "session_id": "8e3b1c9f204217a...",
    "uid": 2,
    "user_context": {
      "lang": "en_US",
      "tz": "UTC"
    },
    "username": "Mitchell Admin",
    "partner_id": 3
  }
}
```
*Note: The server returns a `session_id` cookie in the HTTP response headers. Postman and HTTP clients automatically store and send this cookie in subsequent API requests.*

---

## 🚀 Module REST Endpoints (`/api/v1/...`)

### 1. Get Projects
Fetches research projects with optional domain filtering and pagination limit.

- **URL**: `/api/v1/projects`
- **Method**: `POST`
- **Content-Type**: `application/json`

#### Request Payload
```json
{
  "jsonrpc": "2.0",
  "params": {
    "domain": [["project_status", "=", "in_progress"]],
    "limit": 20
  }
}
```

#### Response Payload (`200 OK`)
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "status": 200,
    "count": 2,
    "data": [
      {
        "id": 1,
        "code": "PRJ00001",
        "project_name": "AI-Driven Supply Chain Optimization",
        "project_description": "Developing machine learning algorithms...",
        "lead_researcher_id": [1, "Dr. Mitchell Admin"],
        "start_date": "2026-01-01",
        "end_date": "2026-12-31",
        "project_status": "in_progress"
      }
    ]
  }
}
```

---

### 2. Create Project
Creates a new research project record in the database.

- **URL**: `/api/v1/project/create`
- **Method**: `POST`
- **Content-Type**: `application/json`

#### Request Payload
```json
{
  "jsonrpc": "2.0",
  "params": {
    "vals": {
      "project_name": "Autonomous Drone Supply Network",
      "project_description": "Deploying quadcopters for micro-deliveries across campus units.",
      "start_date": "2026-04-01",
      "end_date": "2026-10-31",
      "project_status": "proposed"
    }
  }
}
```

#### Response Payload (`201 Created`)
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "status": 201,
    "message": "Research project created successfully",
    "project": {
      "id": 5,
      "code": "PRJ00005",
      "project_name": "Autonomous Drone Supply Network",
      "project_status": "proposed"
    }
  }
}
```

#### Error Response (`400 Bad Request`)
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "status": 400,
    "error": "Field project_name is required."
  }
}
```

---

### 3. Get Researchers
Fetches active researchers list.

- **URL**: `/api/v1/researchers`
- **Method**: `POST`
- **Content-Type**: `application/json`

#### Request Payload
```json
{
  "jsonrpc": "2.0",
  "params": {
    "limit": 50
  }
}
```

#### Response Payload (`200 OK`)
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "status": 200,
    "count": 3,
    "data": [
      {
        "id": 1,
        "name": "Dr. Alice Vance",
        "email": "alice.vance@research.example.com",
        "position": "Senior Bioinformatician",
        "expertise": "Genomics, High Performance Computing",
        "is_principal": true
      }
    ]
  }
}
```

---

### 4. Get Experiments
Fetches research experiments.

- **URL**: `/api/v1/experiments`
- **Method**: `POST`
- **Content-Type**: `application/json`

#### Request Payload
```json
{
  "jsonrpc": "2.0",
  "params": {}
}
```

#### Response Payload (`200 OK`)
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "status": 200,
    "count": 2,
    "data": [
      {
        "id": 1,
        "name": "Supply Chain Transformer Fine-Tuning Benchmark",
        "project_id": [1, "PRJ00001 AI-Driven Supply Chain Optimization"],
        "objective": "Benchmark transformer model convergence speed...",
        "methodology": "Run 5-fold cross-validation...",
        "status": "running",
        "start_date": "2026-02-01"
      }
    ]
  }
}
```

---

### 5. Get Research Papers
Fetches research papers and publications.

- **URL**: `/api/v1/papers`
- **Method**: `POST`
- **Content-Type**: `application/json`

#### Request Payload
```json
{
  "jsonrpc": "2.0",
  "params": {}
}
```

#### Response Payload (`200 OK`)
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "status": 200,
    "count": 2,
    "data": [
      {
        "id": 1,
        "paper_name": "Deep Learning Approaches for Dynamic Research Supply Chain Routing",
        "paper_author": "Jane Doe, John Smith, Dr. Alice Vance",
        "paper_status": "draft",
        "paper_doi": "10.1038/s41587-025-01998-x",
        "paper_github_url": "https://github.com/example/research-supply-chain-ai",
        "project_id": [1, "AI-Driven Supply Chain Optimization"]
      }
    ]
  }
}
```

---

## ⚙️ Native Odoo RPC Endpoint (`/web/dataset/call_kw`)

For performing direct CRUD operations on any model (`research.project`, `project.budget`, `research.requirement`, `research.resource`, etc.):

- **URL**: `/web/dataset/call_kw/<model_name>/<method_name>`
- **Method**: `POST`
- **Content-Type**: `application/json`

### Example: Generic `search_read` on Project Budgets
```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "model": "project.budget",
    "method": "search_read",
    "args": [[]],
    "kwargs": {
      "fields": ["project_id", "total_amount", "spent_amount", "remaining_amount"]
    }
  }
}
```
