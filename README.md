# End-to-End Data Pipeline with Dataform

This repository contains an **end-to-end data pipeline** built on **Google Cloud Platform (GCP)**.  

The pipeline follows the **Bronze → Silver → Gold** architecture and consists of three main components:

1. **Ingestion** – A **Cloud Function** loads raw data from **Google Cloud Storage (GCS)** into **BigQuery (Bronze layer)**.
2. **Transformation** – **Dataform** transforms data through multiple layers:
   - **Bronze** → Raw ingested tables.
   - **Silver** → Cleaned and aggregated tables.
   - **Gold** → Final analytics/industry-ready tables.
3. **Orchestration** – The pipeline is automated with **Cloud Scheduler** and executed using **Cloud Workflows**.

---

## 📂 Project Structure

```
├── cloud_function/
│   └── main.py          # Cloud Function code to load data from GCS → BigQuery
│
├── workflow/
│   └── workflow.yaml        # Cloud Workflow definition
│                        # 1. Calls Cloud Function for ingestion
│                        # 2. Compiles & runs Dataform pipeline
│
│── definitions/     # SQLX scripts for transformations
│   ├── bronze.sqlx  # Bronze layer (raw ingestion + leveling)
│   ├── silver.sqlx  # Silver layer (aggregations, avg salary)
│   └── gold.sqlx    # Gold layer (final analytics with stability metric)
│── workflow_settings.yaml    # Dataform project config
│
└── README.md            # Project documentation
```

---

## ⚙️ Workflow Overview

1. **Cloud Scheduler** triggers the workflow on schedule.
2. **Cloud Workflows** executes:
   - Step 1: Call Cloud Function → Load CSV from GCS to BigQuery Bronze table.
   - Step 2: Trigger Dataform → Transform Bronze → Silver → Gold.
   - Step 3: Return Dataform execution response.
3. **Final Tables in BigQuery**:
   - `bronze.salary_raw`
   - `silver.salary_silver`
   - `gold.salary_gold`

---

## 🚀 Deployment Steps

### 1. Deploy Cloud Function
```bash
gcloud functions deploy hello_http   --runtime python311   --trigger-http   --allow-unauthenticated   --region europe-west1
```

### 2. Deploy Dataform Repository
- Push your SQLX scripts and `workflow_settings.yaml` into a **Dataform Git repo**.
- Link the repo in **BigQuery Dataform**.

### 3. Deploy Workflow
```bash
gcloud workflows deploy my-dataform-workflow   --source=workflow/workflow.yaml   --location=africa-south1
```

### 4. Create Cloud Scheduler Job
```bash
gcloud scheduler jobs create http run-dataform-pipeline   --schedule="0 4 * * *" \   # Run daily at 4 AM
  --uri="https://workflowexecutions.googleapis.com/v1/projects/PROJECT_ID/locations/africa-south1/workflows/my-dataform-workflow/executions"   --http-method=POST   --oauth-service-account-email=YOUR_SERVICE_ACCOUNT
```

---

## 🛠️ Tech Stack

- **Cloud Storage** → Store raw CSVs.  
- **Cloud Functions** → Load CSV to BigQuery Bronze.  
- **BigQuery** → Data Warehouse.  
- **Dataform** → Transform data across Bronze/Silver/Gold layers.  
- **Cloud Workflows** → Orchestration.  
- **Cloud Scheduler** → Trigger workflow execution.  

---

## 📊 Example Transformation

### Bronze (Raw + Level Tagging)
```sql
SELECT *,
  CASE 
    WHEN YearsExperience BETWEEN 0 AND 2 THEN 'LEVEL1'
    WHEN YearsExperience BETWEEN 2 AND 4 THEN 'LEVEL2'
    WHEN YearsExperience BETWEEN 4 AND 6 THEN 'LEVEL3'
    WHEN YearsExperience BETWEEN 6 AND 8 THEN 'LEVEL4'
    ELSE 'LEVEL5'
  END AS LEVEL
FROM `project.bronze.salary`
```

### Silver (Aggregations)
```sql
SELECT 
  LEVEL, 
  COUNT(*) AS EMPLOYEE_COUNT, 
  CAST(ROUND(AVG(SALARY) / 1000) AS STRING) || 'K' AS AVG_SALARY,
  CAST(ROUND(SUM(SALARY) / 1000) AS STRING) || 'K' AS TOTAL_LEVEL_SALARY
FROM ${ref("salary_raw")}
GROUP BY LEVEL
```

### Gold (Stability Metric)
```sql
SELECT
  *, 
  ABS(CAST(SUBSTR(TOTAL_LEVEL_SALARY, 1, length(TOTAL_LEVEL_SALARY) - 1) AS INT64) 
      - CAST(SUBSTR(AVG_SALARY, 1, length(AVG_SALARY) - 1) AS INT64) * EMPLOYEE_COUNT) AS STABILITY
FROM ${ref("salary_silver")}
ORDER BY STABILITY
LIMIT 3
```

---

## ✅ Outcome
This pipeline:
- Automates ingestion from **GCS → BigQuery**.
- Applies **Bronze-Silver-Gold transformations** via Dataform.
- Orchestrates execution using **Workflows + Scheduler**.
- Produces **industry-ready analytics tables** in BigQuery.

---
