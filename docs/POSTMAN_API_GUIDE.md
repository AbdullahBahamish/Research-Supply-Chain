# Postman API Testing Guide

This guide explains how to test all **Research Supply Chain** module APIs using **Postman**.

---

## 🚀 Quick Start: Import Ready-Made Postman Collection

A pre-configured Postman Collection is included in this repository:
- **File**: [`docs/Research_Supply_Chain.postman_collection.json`](file:///d:/Center/Github_Profile/Research-Supply-Chain/docs/Research_Supply_Chain.postman_collection.json)

### How to Import into Postman:
1. Open **Postman**.
2. Click **Import** (top left button).
3. Drag & drop [`docs/Research_Supply_Chain.postman_collection.json`](file:///d:/Center/Github_Profile/Research-Supply-Chain/docs/Research_Supply_Chain.postman_collection.json) or select the file.
4. Set collection environment variables (if your port or database name differs):
   - `base_url`: `http://localhost:8069`
   - `db_name`: `ODOO_FirstDB`
   - `username`: `admin`
   - `password`: `admin`

---

## 📡 API Endpoints Overview

### 1. Authentication (Login First)
Before making requests to restricted endpoints, run the **Authenticate** request to obtain session cookies.

- **URL**: `POST http://localhost:8069/web/session/authenticate`
- **Header**: `Content-Type: application/json`
- **Body**:
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

---

### 2. Custom Module REST Endpoints

#### A. Fetch Projects
- **URL**: `POST http://localhost:8069/api/v1/projects`
- **Body**:
```json
{
  "jsonrpc": "2.0",
  "params": {
    "limit": 50
  }
}
```

#### B. Create New Project
- **URL**: `POST http://localhost:8069/api/v1/project/create`
- **Body**:
```json
{
  "jsonrpc": "2.0",
  "params": {
    "vals": {
      "project_name": "Postman Tested Research Project",
      "project_description": "Created via API call from Postman",
      "project_status": "in_progress"
    }
  }
}
```

#### C. Fetch Researchers
- **URL**: `POST http://localhost:8069/api/v1/researchers`
- **Body**:
```json
{
  "jsonrpc": "2.0",
  "params": {}
}
```

#### D. Fetch Experiments
- **URL**: `POST http://localhost:8069/api/v1/experiments`
- **Body**:
```json
{
  "jsonrpc": "2.0",
  "params": {}
}
```

#### E. Fetch Research Papers
- **URL**: `POST http://localhost:8069/api/v1/papers`
- **Body**:
```json
{
  "jsonrpc": "2.0",
  "params": {}
}
```

---

### 3. Native Odoo ORM Endpoints (`call_kw`)

You can also directly query any model in the system using Odoo's native ORM RPC endpoint:

- **URL**: `POST http://localhost:8069/web/dataset/call_kw/research.project/search_read`
- **Body**:
```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "model": "research.project",
    "method": "search_read",
    "args": [[]],
    "kwargs": {
      "fields": ["code", "project_name", "project_status", "start_date", "end_date"]
    }
  }
}
```
