
# 🛡️ AI Phishing Detection Engine

An end-to-end Machine Learning system that detects and classifies suspicious domains into:

* ✅ **Legitimate**
* ⚠️ **Suspected**
* 🚨 **Phishing**

The system combines ML-based classification, domain intelligence, and a monitoring engine to detect evolving phishing attacks in real time.

---

## 🚀 Key Features

* 3-Class Random Forest Classifier
* Typosquatting Detection (Levenshtein Similarity)
* URL & Lexical Feature Engineering
* WHOIS & DNS Intelligence (mocked, API-ready)
* Automated Structured JSON Report Generation
* Monitoring Engine for Suspected Domains
* Dockerized Flask Backend API
* React-ready frontend support

---

## 🧠 How It Works

```
User Input (URL + Genuine Domain)
        ↓
Feature Engineering
        ↓
Random Forest Model
        ↓
Classification (0 / 1 / 2)
        ↓
Full Detection Report
        ↓
If Suspected → Monitoring Engine
```

---

## 🏗️ Architecture Components

### 1️⃣ Feature Engineering

Extracts:

* Levenshtein similarity (typosquatting detection)
* URL length & structure features
* Special character counts
* Subdomain analysis
* Domain age (WHOIS-based)

Implemented in: `feature_engineer.py`

---

### 2️⃣ ML Model

* Algorithm: **RandomForestClassifier**
* OneHot Encoding for CSE names
* GridSearchCV tuning
* Precision Macro optimization
* Stratified train/test split

Training script: `generate_model.py`
Model artifact:

```
model/final_phishing_model_pipeline.joblib
```

---

### 3️⃣ Backend API (Flask)

Main file: `app.py`

#### 🔹 POST `/api/classify`

**Request**

```json
{
  "url": "http://airtel-suspected.in/login",
  "cse_domain": "airtel.in",
  "cse_name": "Airtel"
}
```

**Response**

```json
{
  "prediction_id": 2,
  "label": "Phishing",
  "report_data": { ... structured intelligence report ... }
}
```

#### 🔹 GET `/api/status`

Health check endpoint.

---

### 4️⃣ Monitoring Engine

If a domain is classified as **Suspected (1)**:

* Added to monitoring queue
* Periodic dynamic content checks
* Reclassified to Phishing if malicious behavior detected
* Urgent alert generated

Implements adaptive security logic.

---

## 🐳 Deployment

### Step 1 – Generate Model

```bash
python generate_model.py
```

### Step 2 – Build Docker Image

```bash
docker build -t ai-phishing-engine .
```

### Step 3 – Run Container

```bash
docker run -p 5000:5000 ai-phishing-engine
```

Server runs at:

```
http://localhost:5000
```

---

## 📦 Tech Stack

* Python
* Scikit-Learn
* Flask
* Pandas / NumPy
* Docker
* GridSearchCV
* OneHotEncoder

---

## 🔐 Security Approach

✔ Multi-layer detection (lexical + network)
✔ Confidence-based scoring
✔ Structured intelligence reporting
✔ Monitoring for evolving phishing attacks
✔ Containerized backend for deployment security

---

## 📈 What This Project Demonstrates

* Applied Machine Learning in Cybersecurity
* Feature Engineering for Domain Analysis
* Backend API Development
* Model Pipeline Engineering
* Adaptive Monitoring Logic
* Production-style Deployment with Docker

---

## 👨‍💻 Author

**Prateek Pathak**
AI/ML Engineer

