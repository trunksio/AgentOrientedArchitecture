#!/usr/bin/env python3
"""Test script to verify agent auto-registration functionality"""
import asyncio
import httpx
import time
import sys

async def check_agent_health(agent_url: str, agent_name: str):
    """Check agent health endpoint for registration status"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{agent_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                reg_status = health_data.get("registration_status", "unknown")
                reg_attempts = health_data.get("registration_attempts", 0)
                reg_error = health_data.get("registration_error", None)
                
                print(f"\n{agent_name}:")
                print(f"  Status: {health_data.get('status')}")
                print(f"  Registration: {reg_status}")
                print(f"  Attempts: {reg_attempts}")
                if reg_error:
                    print(f"  Error: {reg_error}")
                
                return reg_status == "registered"
            else:
                print(f"\n{agent_name}: Health check failed with status {response.status_code}")
                return False
    except Exception as e:
        print(f"\n{agent_name}: Cannot reach agent - {type(e).__name__}: {e}")
        return False

async def check_registry(backend_url: str):
    """Check which agents are registered in the A2A registry"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{backend_url}/api/registry/agents")
            if response.status_code == 200:
                agents = response.json()
                print(f"\nRegistered agents in A2A Registry: {len(agents)}")
                for agent in agents:
                    print(f"  - {agent['id']} ({agent['name']})")
                return agents
            else:
                print(f"Registry check failed with status {response.status_code}")
                return []
    except Exception as e:
        print(f"Cannot reach registry - {type(e).__name__}: {e}")
        return []

async def main():
    """Main test function"""
    print("Testing Agent Auto-Registration")
    print("=" * 50)
    
    # Define agent endpoints
    agents = [
        ("http://localhost:8081", "Data Agent"),
        ("http://localhost:8082", "Visualization Agent"),
        ("http://localhost:8083", "Research Agent"),
        ("http://localhost:8084", "Narrative Agent"),
        ("http://localhost:8085", "GUI Agent"),
    ]
    
    backend_url = "http://localhost:8000"
    
    # Check backend health first
    print("\nChecking backend health...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{backend_url}/health")
            if response.status_code == 200:
                print("Backend is healthy")
            else:
                print(f"Backend health check failed: {response.status_code}")
                return
    except Exception as e:
        print(f"Backend is not reachable: {e}")
        print("\nMake sure to run: docker compose up")
        return
    
    # Check agent health and registration status
    print("\nChecking agent registration status...")
    all_registered = True
    
    for agent_url, agent_name in agents:
        registered = await check_agent_health(agent_url, agent_name)
        if not registered:
            all_registered = False
    
    # Check registry
    print("\n" + "=" * 50)
    registered_agents = await check_registry(backend_url)
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    if all_registered and len(registered_agents) >= 5:
        print("✅ All agents successfully auto-registered!")
    else:
        print("❌ Some agents failed to auto-register")
        print("\nTroubleshooting:")
        print("1. Check docker compose logs for errors")
        print("2. Ensure all services are running: docker compose ps")
        print("3. Check agent logs: docker compose logs <agent-name>")

if __name__ == "__main__":
    asyncio.run(main())