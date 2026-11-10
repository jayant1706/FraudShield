# FraudShield: AWS Enterprise Production Deployment Architecture

This document specifies the target enterprise production deployment architecture for FraudShield on Amazon Web Services (AWS), designed for High Availability (99.99% uptime), PCI-DSS compliance, sub-50ms p95 latency, and automatic horizontal scalability.

---

## 1. Cloud Architecture Overview

```
                        [ Internet Users & Client Applications ]
                                           │
                                    [ Route 53 DNS ]
                                           │
                      ┌────────────────────┴────────────────────┐
                      ▼                                         ▼
         [ CloudFront CDN + AWS WAF ]              [ Application Load Balancer ]
                      │                                 (Public Subnets Multi-AZ)
                      ▼                                         │
           [ S3 Static Hosting ]                                │
          (React SPA Dashboard)                                 ▼
                                                   [ Private App Subnets ]
                                           ┌────────────────────────────────┐
                                           │   Amazon ECS Fargate Cluster   │
                                           │   ┌────────────────────────┐   │
                                           │   │ FastAPI Inference API  │   │
                                           │   │   (Auto-scaled 4-32)   │   │
                                           │   └───────────┬────────────┘   │
                                           │               │                │
                                           │   ┌───────────▼────────────┐   │
                                           │   │ Celery Async Workers   │   │
                                           │   │   (Retrain & Drift)    │   │
                                           │   └───────────┬────────────┘   │
                                           └───────────────┼────────────────┘
                                                           │
                                                [ Private Data Subnets ]
                                           ┌───────────────┴────────────────┐
                                           │                                │
                                           ▼                                ▼
                                  [ Amazon RDS Postgres ]       [ ElastiCache Redis ]
                                   (Multi-AZ Active/Standby)      (Multi-AZ Cluster)
```

---

## 2. Infrastructure Layer Breakdown

### A. Edge & Dashboard Delivery
- **Amazon CloudFront**: Global content delivery network caching static assets (JavaScript, CSS, fonts) with TLS 1.3 termination and HTTP/2 + HTTP/3 support.
- **Amazon S3**: Bucket hosting Vite production assets with private origin access identity (OAI) blocking direct public web access.
- **AWS WAF (Web Application Firewall)**:
  - AWS Managed Rules Common Rule Set (CRS).
  - SQLi and Cross-Site Scripting (XSS) filters.
  - Rate-based rule limiting individual IP addresses to 2,000 requests per 5 minutes.
  - Bot Control rule set to block credential stuffing and automated scrapers.

### B. Ingress & Compute (ECS Fargate)
- **Application Load Balancer (ALB)**:
  - Deployed across 3 Availability Zones (AZs) in public subnets.
  - Health checks on `/health` (interval 15s, healthy threshold 2, timeout 5s).
  - Path-based routing: `/api/*` routed to FastAPI Target Group, `/metrics` restricted to internal security group.
- **Amazon ECS on AWS Fargate**:
  - Serverless container orchestration eliminating EC2 host maintenance.
  - **Inference Task Definition**: 2 vCPU, 4 GB RAM per task. Configured with target-tracking scaling policy maintaining ALB target response time $<45$ms and task CPU utilization $<70\%$.
  - **Celery Worker Task Definition**: 4 vCPU, 8 GB RAM per task for XGBoost model retraining and high-throughput batch scoring. Auto-scales based on AWS CloudWatch custom metric for Redis queue depth.

### C. Persistent Storage & In-Memory Caching
- **Amazon RDS for PostgreSQL (Multi-AZ)**:
  - Primary instance in AZ-a with synchronous replication to standby in AZ-b.
  - Automatic sub-60s failover without manual DBA intervention.
  - Storage: Provisioned IOPS SSD (io2) with automatic storage scaling up to 16 TiB.
  - Encryption at rest via AWS Key Management Service (KMS).
- **Amazon ElastiCache for Redis (Cluster Mode)**:
  - Multi-AZ replication group with Redis 7.x.
  - Acts as Celery message broker and result store.
  - In-memory feature cache for customer velocity tracking and rate-limiting counters.

---

## 3. Security, IAM & PCI-DSS Compliance

1. **Zero Cardholder Data (PAN) Ingestion**:
   - The platform strictly processes payment metadata, tokenized external transaction IDs, amounts, and mathematical latent vectors ($V_1-V_{28}$).
   - Primary Account Numbers (PAN), CVVs, and magnetic stripe data never enter the VPC.
2. **Secrets & Credential Management**:
   - Zero hardcoded environment credentials.
   - Database credentials, JWT signing keys, and external API keys are managed by **AWS Secrets Manager** with automatic 30-day rotation.
   - ECS Task Execution Role grants read-only access to specific Secret ARNs.
3. **Network Isolation**:
   - Zero public IP addresses assigned to ECS tasks or RDS databases.
   - Outbound internet access from ECS tasks (for Python dependencies and OS security updates) routes exclusively through AWS NAT Gateways.
   - Security groups enforce least-privilege: RDS port 5432 is strictly accessible only from the ECS Task Security Group.

---

## 4. Observability & SRE Runbook

- **Amazon Managed Service for Prometheus (AMP)**:
  - Scrapes metrics from `/metrics` endpoints across active ECS task replicas.
  - Retention: 13 months for audit trails and seasonality analysis.
- **Amazon Managed Grafana (AMG)**:
  - Single pane of glass visualizing transaction throughput, model inference latency, fraud detection volume, and drift alarms.
- **CloudWatch Alarms & Alert Routing**:
  - `P99InferenceLatencyHigh`: Triggers if p99 latency $> 100$ms for 3 consecutive minutes $\to$ PagerDuty High Severity.
  - `ModelDriftDetected`: Triggers when Celery drift task flags dataset drift $\to$ Slack `#fraud-ml-ops` channel.
  - `HighRiskSpikeAlarm`: Triggers if high-risk transaction ratio exceeds $5\%$ of total volume over a 15-minute sliding window.

---

## 5. Terraform Infrastructure-as-Code Blueprint

```hcl
# ECS Task Definition Example for FraudShield Backend
resource "aws_ecs_task_definition" "fraudshield_backend" {
  family                   = "fraudshield-backend-prod"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "2048"
  memory                   = "4096"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "fraudshield-api"
      image     = "${aws_ecr_repository.backend.repository_url}:v1.0.0"
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
        }
      ]
      secrets = [
        {
          name      = "SECRET_KEY"
          valueFrom = "${aws_secretsmanager_secret.fraudshield_jwt.arn}"
        },
        {
          name      = "SYNC_DATABASE_URL"
          valueFrom = "${aws_secretsmanager_secret.fraudshield_db.arn}"
        }
      ]
      environment = [
        { name = "ENVIRONMENT", value = "production" },
        { name = "DEBUG", value = "false" },
        { name = "REDIS_URL", value = "redis://${aws_elasticache_replication_group.redis.primary_endpoint_address}:6379/0" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/fraudshield-backend-prod"
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "api"
        }
      }
    }
  ])
}
```

