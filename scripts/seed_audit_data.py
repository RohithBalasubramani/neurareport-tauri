"""
Seed comprehensive test data for UI audit
Creates realistic test data for all pages to ensure all UI elements are testable
"""
import requests
import json
from datetime import datetime, timedelta
import random
import uuid

BASE_URL = "http://127.0.0.1:8001"

# Test data templates
SAMPLE_TEMPLATES = [
    {"name": "Q4 Financial Report", "description": "Quarterly financial summary", "industry": "Finance"},
    {"name": "Sales Dashboard", "description": "Monthly sales metrics", "industry": "Sales"},
    {"name": "Customer Analysis", "description": "Customer behavior insights", "industry": "Marketing"},
    {"name": "Inventory Report", "description": "Stock level monitoring", "industry": "Logistics"},
    {"name": "HR Performance Review", "description": "Employee performance tracking", "industry": "Human Resources"},
]

SAMPLE_CONNECTIONS = [
    {"name": "Production DB", "type": "postgresql", "host": "prod-db.example.com", "port": 5432, "database": "main"},
    {"name": "Analytics Warehouse", "type": "snowflake", "host": "analytics.snowflakecomputing.com", "database": "warehouse"},
    {"name": "CRM Database", "type": "mysql", "host": "crm-db.example.com", "port": 3306, "database": "crm"},
    {"name": "Sales DB", "type": "postgresql", "host": "sales-db.example.com", "port": 5432, "database": "sales"},
]

SAMPLE_DOCUMENTS = [
    {"name": "Q3 Financial Statement.pdf", "type": "pdf", "size": 1024000},
    {"name": "Product Catalog 2026.pdf", "type": "pdf", "size": 2048000},
    {"name": "Customer List.xlsx", "type": "excel", "size": 512000},
    {"name": "Meeting Notes.docx", "type": "word", "size": 256000},
]

SAMPLE_AGENTS = [
    {"name": "Data Analyst", "role": "analyst", "description": "Analyzes data patterns and trends"},
    {"name": "Report Writer", "role": "writer", "description": "Generates professional reports"},
    {"name": "Chart Specialist", "role": "visualizer", "description": "Creates data visualizations"},
]

def seed_templates():
    """Seed template data"""
    print("\n[1/8] Seeding Templates...")
    created = []

    for template in SAMPLE_TEMPLATES:
        try:
            # Create template via API
            response = requests.post(
                f"{BASE_URL}/templates",
                json={
                    "name": template["name"],
                    "description": template["description"],
                    "industry": template["industry"],
                    "fields": [
                        {"name": "title", "type": "text", "required": True},
                        {"name": "date", "type": "date", "required": True},
                        {"name": "value", "type": "number", "required": False}
                    ],
                    "created_at": datetime.now().isoformat()
                }
            )
            if response.status_code in [200, 201]:
                created.append(template["name"])
                print(f"  ✓ Created: {template['name']}")
            else:
                print(f"  ✗ Failed: {template['name']} - {response.status_code}")
        except Exception as e:
            print(f"  ✗ Error: {template['name']} - {str(e)}")

    print(f"  → Created {len(created)}/{len(SAMPLE_TEMPLATES)} templates")
    return created

def seed_connections():
    """Seed connection data"""
    print("\n[2/8] Seeding Connections...")
    created = []

    for conn in SAMPLE_CONNECTIONS:
        try:
            response = requests.post(
                f"{BASE_URL}/connections",
                json={
                    "name": conn["name"],
                    "type": conn["type"],
                    "host": conn["host"],
                    "port": conn.get("port"),
                    "database": conn["database"],
                    "username": "test_user",
                    "password": "test_password",
                    "ssl": True
                }
            )
            if response.status_code in [200, 201]:
                created.append(conn["name"])
                print(f"  ✓ Created: {conn['name']}")
            else:
                print(f"  ✗ Failed: {conn['name']} - {response.status_code}")
        except Exception as e:
            print(f"  ✗ Error: {conn['name']} - {str(e)}")

    print(f"  → Created {len(created)}/{len(SAMPLE_CONNECTIONS)} connections")
    return created

def seed_reports():
    """Seed report data"""
    print("\n[3/8] Seeding Reports...")
    created = []

    for i in range(10):
        try:
            report_name = f"Report {i+1}: {random.choice(['Monthly', 'Quarterly', 'Annual'])} Analysis"
            response = requests.post(
                f"{BASE_URL}/reports",
                json={
                    "name": report_name,
                    "template_id": str(uuid.uuid4()),
                    "status": random.choice(["completed", "pending", "failed"]),
                    "created_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                    "data": {"title": report_name, "generated": True}
                }
            )
            if response.status_code in [200, 201]:
                created.append(report_name)
                print(f"  ✓ Created: {report_name}")
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")

    print(f"  → Created {len(created)}/10 reports")
    return created

def seed_jobs():
    """Seed job data"""
    print("\n[4/8] Seeding Jobs...")
    created = []

    statuses = ["running", "completed", "failed", "pending", "queued"]
    for i in range(15):
        try:
            job_name = f"Job-{i+1}-{random.choice(['ETL', 'Transform', 'Export'])}"
            response = requests.post(
                f"{BASE_URL}/jobs",
                json={
                    "name": job_name,
                    "status": random.choice(statuses),
                    "progress": random.randint(0, 100),
                    "started_at": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
                    "type": random.choice(["report_generation", "data_import", "export"])
                }
            )
            if response.status_code in [200, 201]:
                created.append(job_name)
                print(f"  ✓ Created: {job_name}")
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")

    print(f"  → Created {len(created)}/15 jobs")
    return created

def seed_schedules():
    """Seed schedule data"""
    print("\n[5/8] Seeding Schedules...")
    created = []

    for i in range(8):
        try:
            schedule_name = f"Schedule {i+1}: {random.choice(['Daily', 'Weekly', 'Monthly'])} Run"
            response = requests.post(
                f"{BASE_URL}/schedules",
                json={
                    "name": schedule_name,
                    "cron": random.choice(["0 9 * * *", "0 0 * * 0", "0 0 1 * *"]),
                    "enabled": random.choice([True, False]),
                    "next_run": (datetime.now() + timedelta(days=1)).isoformat()
                }
            )
            if response.status_code in [200, 201]:
                created.append(schedule_name)
                print(f"  ✓ Created: {schedule_name}")
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")

    print(f"  → Created {len(created)}/8 schedules")
    return created

def seed_documents():
    """Seed document data"""
    print("\n[6/8] Seeding Documents...")
    created = []

    for doc in SAMPLE_DOCUMENTS:
        try:
            response = requests.post(
                f"{BASE_URL}/documents",
                json={
                    "name": doc["name"],
                    "type": doc["type"],
                    "size": doc["size"],
                    "uploaded_at": datetime.now().isoformat(),
                    "status": "processed"
                }
            )
            if response.status_code in [200, 201]:
                created.append(doc["name"])
                print(f"  ✓ Created: {doc['name']}")
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")

    print(f"  → Created {len(created)}/{len(SAMPLE_DOCUMENTS)} documents")
    return created

def seed_agents():
    """Seed agent data"""
    print("\n[7/8] Seeding AI Agents...")
    created = []

    for agent in SAMPLE_AGENTS:
        try:
            response = requests.post(
                f"{BASE_URL}/agents",
                json={
                    "name": agent["name"],
                    "role": agent["role"],
                    "description": agent["description"],
                    "status": random.choice(["active", "idle"]),
                    "capabilities": ["analysis", "reporting", "visualization"]
                }
            )
            if response.status_code in [200, 201]:
                created.append(agent["name"])
                print(f"  ✓ Created: {agent['name']}")
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")

    print(f"  → Created {len(created)}/{len(SAMPLE_AGENTS)} agents")
    return created

def seed_knowledge():
    """Seed knowledge base data"""
    print("\n[8/8] Seeding Knowledge Base...")
    created = []

    topics = ["SQL Best Practices", "Report Design Guide", "Data Governance", "API Documentation", "User Manual"]
    for topic in topics:
        try:
            response = requests.post(
                f"{BASE_URL}/knowledge",
                json={
                    "title": topic,
                    "content": f"Comprehensive guide for {topic}...",
                    "category": random.choice(["technical", "business", "reference"]),
                    "tags": ["documentation", "guide"],
                    "created_at": datetime.now().isoformat()
                }
            )
            if response.status_code in [200, 201]:
                created.append(topic)
                print(f"  ✓ Created: {topic}")
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")

    print(f"  → Created {len(created)}/{len(topics)} knowledge articles")
    return created

def main():
    """Main seeding function"""
    print("=" * 70)
    print("  SEEDING COMPREHENSIVE TEST DATA FOR UI AUDIT")
    print("=" * 70)
    print(f"\nTarget: {BASE_URL}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Check backend health
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("[OK] Backend is healthy and reachable")
        else:
            print("[ERROR] Backend returned non-200 status")
            return
    except Exception as e:
        print(f"[ERROR] Cannot reach backend: {str(e)}")
        print("  Make sure backend is running on port 8001")
        return

    # Seed all data
    results = {
        "templates": seed_templates(),
        "connections": seed_connections(),
        "reports": seed_reports(),
        "jobs": seed_jobs(),
        "schedules": seed_schedules(),
        "documents": seed_documents(),
        "agents": seed_agents(),
        "knowledge": seed_knowledge(),
    }

    # Summary
    total_created = sum(len(v) for v in results.values())
    print("\n" + "=" * 70)
    print("  SEEDING COMPLETE")
    print("=" * 70)
    print(f"\nTotal items created: {total_created}")
    for category, items in results.items():
        print(f"  {category.capitalize()}: {len(items)}")

    print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n✓ Ready for audit with full test data!\n")

if __name__ == "__main__":
    main()
