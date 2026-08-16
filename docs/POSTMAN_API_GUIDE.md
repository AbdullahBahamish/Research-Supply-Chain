# Postman API Testing Guide

This guide explains how to test all API endpoints in the **Research Supply Chain** module using **Postman**.

---

## Quick Start: Import Ready-Made Postman Collection

A pre-configured Postman Collection is included directly in this repository:
- **Collection File**: [`docs/Research_Supply_Chain.postman_collection.json`](file:///d:/Center/Github_Profile/Research-Supply-Chain/docs/Research_Supply_Chain.postman_collection.json)

### How to Import into Postman:
1. Open **Postman**.
2. Click **Import** (top left button).
3. Drag & drop [`docs/Research_Supply_Chain.postman_collection.json`](file:///d:/Center/Github_Profile/Research-Supply-Chain/docs/Research_Supply_Chain.postman_collection.json) or select the file.
4. Set collection environment variables (if your server port or database name differs):
   - `base_url`: `http://localhost:8069`
   - `db_name`: `research_db`
   - `username`: `admin`
   - `password`: `admin`

---

## API Requests Catalog

### 1. Authentication (Login Request)
Run the **Authenticate / Login** request first to obtain session cookies stored automatically by Postman.

- **URL**: `POST {{base_url}}/web/session/authenticate`
- **Headers**: `Content-Type: application/json`
- **Body**:
```json
{
  "jsonrpc": "2.0",
  "params": {
    "db": "{{db_name}}",
    "login": "{{username}}",
    "password": "{{password}}"
  }
}
```

---

### 2. Module REST Endpoints

#### A. Fetch Filtered Projects (`/api/v1/projects`)
- **URL**: `POST {{base_url}}/api/v1/projects`
- **Body**:
```json
{
  "jsonrpc": "2.0",
  "params": {
    "filters": {
      "project_status": "in_progress"
    },
    "limit": 50,
    "offset": 0
  }
}
```

#### B. Create New Project (`/api/v1/project/create`)
- **URL**: `POST {{base_url}}/api/v1/project/create`
- **Body**:
```json
{
  "jsonrpc": "2.0",
  "params": {
    "vals": {
      "project_name": "Autonomous Campus Micro-Logistics",
      "project_description": "Created via Postman API integration runner.",
      "project_status": "proposed"
    }
  }
}
```

#### C. Fetch Researchers Directory (`/api/v1/researchers`)
- **URL**: `POST {{base_url}}/api/v1/researchers`
- **Body**:
```json
{
  "jsonrpc": "2.0",
  "params": {
    "limit": 50
  }
}
```

#### D. Fetch Grouped Experiments (`/api/v1/experiments`)
- **URL**: `POST {{base_url}}/api/v1/experiments`
- **Body**:
```json
{
  "jsonrpc": "2.0",
  "params": {
    "limit": 50
  }
}
```

#### E. Fetch Internal Papers (`/api/v1/papers`)
- **URL**: `POST {{base_url}}/api/v1/papers`
- **Body**:
```json
{
  "jsonrpc": "2.0",
  "params": {
    "limit": 50
  }
}
```

#### F. Fetch Published Papers Publicly (`/api/v1/papers/public`)
- **URL**: `POST {{base_url}}/api/v1/papers/public` (No authentication required)
- **Body**:
```json
{
  "jsonrpc": "2.0",
  "params": {
    "limit": 10
  }
}
```

---

### 3. Native Odoo RPC Calls (`/web/dataset/call_kw`)

You can query any model directly using standard Odoo RPC:

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
