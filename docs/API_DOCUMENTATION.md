# API Specification & Reference Guide

This document provides production-grade technical specifications for all REST and JSON-RPC API endpoints in the **Research Supply Chain** module.

---

## Controller Architecture & Security Model

API controllers are implemented in [`addons/research_supply_chain/controllers/main.py`](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/controllers/main.py). 

```
addons/research_supply_chain/
├── __init__.py          # Imports models and controllers
├── controllers/         # Official Odoo HTTP/JSON endpoint directory
│   ├── __init__.py
│   └── main.py          # API routes (@http.route) & input sanitizers
```

### Security Guardrails & Sanitization
- **Strict Parameter Allow-lists**: Unsafe raw domain injection probes are blocked using `PROJECT_SEARCH_FIELDS` (`{"project_status", "code", "lead_researcher_id", "visibility", "tag_ids"}`).
- **Mass-Assignment Protection**: Input payloads on creation are filtered via `PROJECT_CREATE_FIELDS` (`{"project_name", "project_description", "lead_researcher_id", "start_date", "end_date", "project_status", "visibility", "tag_ids"}`).
- **Privacy Field Filtering**: Directory endpoints (such as `/api/v1/researchers`) restrict sensitive field exposures (e.g. user email addresses are excluded from public directory lists).

---

## Session Authentication

Authenticated endpoints require an active Odoo session cookie obtained via the standard authentication route:

- **URL**: `/web/session/authenticate`
- **Method**: `POST`
- **Content-Type**: `application/json`

### Request Payload
```json
{
  "jsonrpc": "2.0",
  "params": {
    "db": "research_db",
    "login": "admin",
    "password": "admin"
  }
}
```

### Response Payload (`200 OK`)
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "session_id": "8e3b1c9f204217a...",
    "uid": 2,
    "user_context": { "lang": "en_US", "tz": "UTC" },
    "username": "Mitchell Admin",
    "partner_id": 3
  }
}
```

---

## Module REST / JSON-RPC Endpoints (`/api/v1/...`)

### 1. Get Projects
Fetches active research projects with whitelisted equality filtering and pagination.

- **URL**: `/api/v1/projects`
- **Method**: `POST`
- **Auth**: User (`auth='user'`)
- **Content-Type**: `application/json`

#### Request Payload
```json
{
  "jsonrpc": "2.0",
  "params": {
    "filters": {
      "project_status": "in_progress"
    },
    "limit": 20,
    "offset": 0
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
    "count": 1,
    "offset": 0,
    "limit": 20,
    "data": [
      {
        "id": 1,
        "code": "PRJ00001",
        "project_name": "Ai-Driven Supply Chain Optimization",
        "lead_researcher": "Dr. Alice Vance",
        "status": "in_progress",
        "start_date": "2026-01-01",
        "end_date": "2026-12-31"
      }
    ]
  }
}
```

---

### 2. Create Project
Safely creates a new research project record.

- **URL**: `/api/v1/project/create`
- **Method**: `POST`
- **Auth**: User (`auth='user'`)
- **Content-Type**: `application/json`

#### Request Payload
```json
{
  "jsonrpc": "2.0",
  "params": {
    "vals": {
      "project_name": "Autonomous Drone Micro-Deliveries",
      "project_description": "Deploying autonomous quadcopters for campus logistics.",
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
      "project_name": "Autonomous Drone Micro-Deliveries",
      "project_status": "proposed"
    }
  }
}
```

---

### 3. Get Researchers Directory
Fetches active researcher profiles (privacy-scoped, email excluded).

- **URL**: `/api/v1/researchers`
- **Method**: `POST`
- **Auth**: User (`auth='user'`)
- **Content-Type**: `application/json`

#### Request Payload
```json
{
  "jsonrpc": "2.0",
  "params": {
    "limit": 50,
    "offset": 0
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
    "offset": 0,
    "limit": 50,
    "data": [
      {
        "id": 1,
        "name": "Dr. Alice Vance",
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
Fetches research experiments grouped by execution status.

- **URL**: `/api/v1/experiments`
- **Method**: `POST`
- **Auth**: User (`auth='user'`)
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
    "count": 1,
    "grouped_by_status": {
      "running": [
        {
          "id": 1,
          "name": "Transformer Benchmark Run 1",
          "project_id": [1, "PRJ00001 AI-Driven Supply Chain Optimization"],
          "objective": "Benchmark transformer convergence speed.",
          "methodology": "Run 5-fold cross-validation.",
          "status": "running",
          "start_date": "2026-02-01"
        }
      ]
    },
    "data": [...]
  }
}
```

---

### 5. Get Papers
Fetches internal academic publications and pre-prints.

- **URL**: `/api/v1/papers`
- **Method**: `POST`
- **Auth**: User (`auth='user'`)
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
    "count": 1,
    "data": [
      {
        "id": 1,
        "paper_name": "Deep Learning for Dynamic Supply Routing",
        "paper_author": "Dr. Alice Vance, Mitchell Admin",
        "paper_status": "draft",
        "paper_doi": "10.1038/s41587-025-01998-x",
        "paper_github_url": "https://github.com/example/research-supply-chain",
        "project_id": [1, "AI-Driven Supply Chain Optimization"]
      }
    ]
  }
}
```

---

### 6. Public Papers Endpoint
Public endpoint for external citation of published research papers.

- **URL**: `/api/v1/papers/public`
- **Method**: `POST` / `GET`
- **Auth**: Public (`auth='public'`)
- **Content-Type**: `application/json`

#### Request Payload
```json
{
  "jsonrpc": "2.0",
  "params": {
    "limit": 10
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
    "count": 1,
    "data": [
      {
        "id": 2,
        "paper_name": "Scalable Micro-Logistics Networks",
        "paper_author": "Dr. Alice Vance",
        "paper_doi": "10.1016/j.artint.2025.10399",
        "paper_publication_date": "2026-03-15",
        "paper_github_url": "https://github.com/example/drone-routing"
      }
    ]
  }
}
```
