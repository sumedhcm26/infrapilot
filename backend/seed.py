"""
Seed Script - Populate the database with demo data
===================================================
Run this after starting the backend to get a realistic dashboard:

    cd backend
    python seed.py

This creates:
- 3 environments (dev, staging, production)
- 5 sample services
- 6 sample deployments
- 2 sample incidents
"""

import asyncio
import httpx


BASE_URL = "http://localhost:8000"


async def seed():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as client:

        print("🌱 Seeding InfraPilot with demo data...")

        # ----------------------------------------
        # Environments
        # ----------------------------------------
        print("\n📦 Creating environments...")
        envs = [
            {"name": "dev", "display_name": "Development", "color": "#42a5f5", "description": "Local and feature branch testing"},
            {"name": "staging", "display_name": "Staging", "color": "#ffca28", "description": "Pre-production validation"},
            {"name": "production", "display_name": "Production", "color": "#ce93d8", "description": "Live customer traffic"},
        ]
        for env in envs:
            r = await client.post("/api/v1/environments/", json=env)
            if r.status_code == 201:
                print(f"  ✅ Created environment: {env['display_name']}")
            else:
                print(f"  ⚠️  {env['name']}: {r.json()}")

        # ----------------------------------------
        # Services
        # ----------------------------------------
        print("\n🔗 Registering services...")
        services = [
            {"name": "Payment API", "url": "https://httpbin.org/status/200", "environment": "production", "description": "Stripe payment processing service"},
            {"name": "User Service", "url": "https://httpbin.org/status/200", "environment": "production", "description": "Authentication and user management"},
            {"name": "Notification Service", "url": "https://httpbin.org/status/200", "environment": "staging", "description": "Email/SMS/push notifications"},
            {"name": "Analytics Worker", "url": "https://httpbin.org/delay/1", "environment": "production", "description": "Event tracking and analytics pipeline"},
            {"name": "Admin Dashboard", "url": "https://httpbin.org/status/503", "environment": "staging", "description": "Internal admin interface"},
        ]
        service_ids = {}
        for svc in services:
            r = await client.post("/api/v1/services/", json=svc)
            if r.status_code == 201:
                data = r.json()
                service_ids[svc["name"]] = data["id"]
                print(f"  ✅ Registered: {svc['name']}")
            else:
                print(f"  ⚠️  {svc['name']}: {r.json()}")

        # ----------------------------------------
        # Trigger health checks
        # ----------------------------------------
        print("\n🏥 Running initial health checks...")
        for name, svc_id in service_ids.items():
            r = await client.post(f"/api/v1/services/{svc_id}/check")
            if r.status_code == 200:
                data = r.json()
                status = "✅ UP" if data["is_healthy"] else "🔴 DOWN"
                print(f"  {status} {name} — {data.get('last_response_time_ms', '?')}ms")

        # ----------------------------------------
        # Deployments
        # ----------------------------------------
        print("\n🚀 Recording deployments...")
        payment_id = service_ids.get("Payment API", "unknown")
        user_id = service_ids.get("User Service", "unknown")
        notif_id = service_ids.get("Notification Service", "unknown")

        deployments = [
            {"service_id": payment_id, "service_name": "Payment API", "version": "v2.4.1", "environment": "production", "triggered_by": "GitHub Actions", "branch": "main", "commit_sha": "a3f8b21", "notes": "Added retry logic for failed charges"},
            {"service_id": user_id, "service_name": "User Service", "version": "v1.9.0", "environment": "production", "triggered_by": "GitHub Actions", "branch": "main", "commit_sha": "f7c3d94"},
            {"service_id": notif_id, "service_name": "Notification Service", "version": "v3.1.0", "environment": "staging", "triggered_by": "Alice Chen", "branch": "feat/sms-support"},
            {"service_id": payment_id, "service_name": "Payment API", "version": "v2.3.8", "environment": "production", "triggered_by": "GitHub Actions", "branch": "hotfix/timeout"},
        ]

        deployment_ids = []
        for dep in deployments:
            r = await client.post("/api/v1/deployments/", json=dep)
            if r.status_code == 201:
                dep_id = r.json()["id"]
                deployment_ids.append(dep_id)
                print(f"  ✅ Recorded: {dep['service_name']} {dep['version']} → {dep['environment']}")

        # Mark most as successful
        for dep_id in deployment_ids[:-1]:
            await client.patch(f"/api/v1/deployments/{dep_id}", json={"status": "success"})

        # Mark last as failed (for dashboard variety)
        if deployment_ids:
            await client.patch(f"/api/v1/deployments/{deployment_ids[-1]}", json={"status": "failed"})

        # ----------------------------------------
        # Incidents
        # ----------------------------------------
        print("\n⚠️  Creating incidents...")
        incidents = [
            {
                "service_id": service_ids.get("Admin Dashboard", "unknown"),
                "service_name": "Admin Dashboard",
                "title": "Admin Dashboard returning HTTP 503",
                "description": "Service health check failed — nginx upstream returning 503. Likely a memory issue in the staging pod.",
                "severity": "high",
                "trigger_status_code": 503,
            },
        ]
        for inc in incidents:
            r = await client.post("/api/v1/incidents/", json=inc)
            if r.status_code == 201:
                print(f"  🔴 Created incident: {inc['title']}")

        print("\n✅ Seeding complete! Visit http://localhost:5173 to see the dashboard.")
        print("   API docs: http://localhost:8000/docs")


if __name__ == "__main__":
    asyncio.run(seed())
