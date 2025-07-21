#!/usr/bin/env python3
"""Test script for standard agent interfaces"""
import asyncio
import httpx
import json
from typing import Dict, Any, List
import sys

# Standard endpoints to test
STANDARD_ENDPOINTS = [
    "/agent-card",
    "/health", 
    "/mcp/tools",
    "/mcp/execute/{tool_name}"
]

async def test_agent_endpoints(base_url: str, agent_id: str) -> Dict[str, Any]:
    """Test standard endpoints for a single agent"""
    results = {
        "agent_id": agent_id,
        "base_url": base_url,
        "endpoints": {}
    }
    
    async with httpx.AsyncClient() as client:
        # Test /agent-card endpoint
        try:
            response = await client.get(f"{base_url}/agent-card")
            results["endpoints"]["/agent-card"] = {
                "status": response.status_code,
                "success": response.status_code == 200,
                "data": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            results["endpoints"]["/agent-card"] = {
                "status": None,
                "success": False,
                "error": str(e)
            }
        
        # Test /health endpoint
        try:
            response = await client.get(f"{base_url}/health")
            results["endpoints"]["/health"] = {
                "status": response.status_code,
                "success": response.status_code == 200,
                "data": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            results["endpoints"]["/health"] = {
                "status": None,
                "success": False,
                "error": str(e)
            }
        
        # Test /mcp/tools endpoint
        try:
            response = await client.get(f"{base_url}/mcp/tools")
            results["endpoints"]["/mcp/tools"] = {
                "status": response.status_code,
                "success": response.status_code == 200,
                "data": response.json() if response.status_code == 200 else None
            }
            
            # If we got tools, test executing one
            if response.status_code == 200:
                tools_data = response.json()
                if tools_data.get("tools") and len(tools_data["tools"]) > 0:
                    first_tool = tools_data["tools"][0]
                    tool_name = first_tool["name"]
                    
                    # Test /mcp/execute/{tool_name}
                    try:
                        exec_response = await client.post(
                            f"{base_url}/mcp/execute/{tool_name}",
                            json={"parameters": {}}
                        )
                        results["endpoints"][f"/mcp/execute/{tool_name}"] = {
                            "status": exec_response.status_code,
                            "success": exec_response.status_code == 200,
                            "data": exec_response.json() if exec_response.status_code == 200 else None
                        }
                    except Exception as e:
                        results["endpoints"][f"/mcp/execute/{tool_name}"] = {
                            "status": None,
                            "success": False,
                            "error": str(e)
                        }
        except Exception as e:
            results["endpoints"]["/mcp/tools"] = {
                "status": None,
                "success": False,
                "error": str(e)
            }
    
    return results

async def test_backend_agents(backend_url: str = "http://localhost:8000") -> List[Dict[str, Any]]:
    """Test standard endpoints for backend agents"""
    results = []
    
    async with httpx.AsyncClient() as client:
        # Get list of agents
        try:
            response = await client.get(f"{backend_url}/api/agents/list")
            if response.status_code == 200:
                agents_data = response.json()
                backend_agents = [
                    agent for agent in agents_data.get("agents", [])
                    if agent.get("type") == "backend"
                ]
                
                for agent in backend_agents:
                    agent_id = agent["agent_id"]
                    print(f"Testing backend agent: {agent_id}")
                    
                    agent_results = await test_agent_endpoints(
                        f"{backend_url}/api/agents/{agent_id}",
                        agent_id
                    )
                    results.append(agent_results)
        except Exception as e:
            print(f"Error getting agent list: {e}")
    
    return results

async def test_containerized_agents(backend_url: str = "http://localhost:8000") -> List[Dict[str, Any]]:
    """Test standard endpoints for containerized agents"""
    results = []
    
    async with httpx.AsyncClient() as client:
        # Get list of agents
        try:
            response = await client.get(f"{backend_url}/api/agents/list")
            if response.status_code == 200:
                agents_data = response.json()
                containerized_agents = [
                    agent for agent in agents_data.get("agents", [])
                    if agent.get("type") != "backend" and agent.get("endpoint")
                ]
                
                for agent in containerized_agents:
                    agent_id = agent["agent_id"]
                    endpoint = agent["endpoint"]
                    print(f"Testing containerized agent: {agent_id} at {endpoint}")
                    
                    agent_results = await test_agent_endpoints(endpoint, agent_id)
                    results.append(agent_results)
        except Exception as e:
            print(f"Error getting agent list: {e}")
    
    return results

def print_results(results: List[Dict[str, Any]], agent_type: str):
    """Pretty print test results"""
    print(f"\n{'='*60}")
    print(f"{agent_type} Agent Test Results")
    print(f"{'='*60}")
    
    for agent_result in results:
        print(f"\nAgent: {agent_result['agent_id']}")
        print(f"URL: {agent_result['base_url']}")
        print(f"{'  '*10}")
        
        all_success = True
        for endpoint, result in agent_result['endpoints'].items():
            status = "✓" if result['success'] else "✗"
            all_success = all_success and result['success']
            print(f"  {status} {endpoint}: ", end="")
            
            if result['success']:
                print(f"OK (status: {result['status']})")
                if endpoint == "/agent-card" and result.get('data'):
                    data = result['data']
                    print(f"    - Name: {data.get('name')}")
                    print(f"    - Tools: {len(data.get('tools', []))}")
                elif endpoint == "/health" and result.get('data'):
                    data = result['data']
                    print(f"    - Status: {data.get('status')}")
                    print(f"    - Uptime: {data.get('uptime_seconds', 0)}s")
            else:
                print(f"FAILED")
                if 'error' in result:
                    print(f"    - Error: {result['error']}")
                elif result.get('status'):
                    print(f"    - Status: {result['status']}")
        
        print(f"\n  Overall: {'PASSED' if all_success else 'FAILED'}")

async def main():
    """Run all tests"""
    backend_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print(f"Testing standard agent interfaces...")
    print(f"Backend URL: {backend_url}")
    
    # Test backend agents
    backend_results = await test_backend_agents(backend_url)
    if backend_results:
        print_results(backend_results, "Backend")
    else:
        print("\nNo backend agents found to test")
    
    # Test containerized agents
    containerized_results = await test_containerized_agents(backend_url)
    if containerized_results:
        print_results(containerized_results, "Containerized")
    else:
        print("\nNo containerized agents found to test")
    
    # Summary
    total_agents = len(backend_results) + len(containerized_results)
    if total_agents > 0:
        all_passed = all(
            all(ep['success'] for ep in r['endpoints'].values())
            for r in backend_results + containerized_results
        )
        
        print(f"\n{'='*60}")
        print(f"Summary: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
        print(f"Total agents tested: {total_agents}")
        print(f"{'='*60}")
    else:
        print("\nNo agents available for testing")

if __name__ == "__main__":
    asyncio.run(main())