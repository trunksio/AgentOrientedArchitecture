#!/usr/bin/env python3
"""Test the complete agent orchestration flow with UI display"""
import asyncio
import httpx
import json
from datetime import datetime

async def test_complete_flow():
    """Test the complete flow from query to UI display"""
    print("🧪 COMPLETE AGENT ORCHESTRATION TEST")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    backend_url = "http://localhost:8000"
    queries = [
        "show renewable energy data",
        "analyze energy trends with visualizations",
        "compare renewable energy by country"
    ]
    
    for query in queries:
        print(f"\n📝 Testing Query: '{query}'")
        print("-" * 40)
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                # 1. Check agents are registered
                agents_resp = await client.get(f"{backend_url}/api/registry/agents")
                agents = agents_resp.json()
                print(f"✓ Agents registered: {len(agents)}")
                
                # 2. Send orchestration request
                print("📮 Sending orchestration request...")
                start_time = datetime.now()
                
                orch_resp = await client.post(
                    f"{backend_url}/api/orchestrate",
                    json={"query": query, "context": {}}
                )
                
                elapsed = (datetime.now() - start_time).total_seconds()
                result = orch_resp.json()
                
                if orch_resp.status_code == 200 and not result.get("error"):
                    print(f"✅ Success! Orchestration completed in {elapsed:.1f} seconds")
                    
                    # 3. Analyze results
                    if result.get("results"):
                        agents_executed = result["results"].get("agents_executed", [])
                        print(f"   Agents used: {', '.join(agents_executed)}")
                        
                        # Check outputs
                        outputs = result["results"].get("outputs", {})
                        for agent_id, output in outputs.items():
                            if output:
                                print(f"   ✓ {agent_id} returned data")
                    
                    # 4. Check UI components
                    if result.get("ui_spec"):
                        components = result["ui_spec"].get("components", [])
                        print(f"   UI Components: {len(components)}")
                        
                        component_types = {}
                        for comp in components:
                            comp_type = comp.get("type", "unknown")
                            component_types[comp_type] = component_types.get(comp_type, 0) + 1
                        
                        for comp_type, count in component_types.items():
                            print(f"     - {comp_type}: {count}")
                    
                    # 5. Verify displayable content
                    has_data_table = any(c.get("type") == "data_table" for c in components)
                    has_chart = any(c.get("type") == "chart" for c in components)
                    has_narrative = any(c.get("type") == "narrative" for c in components)
                    
                    print(f"\n   Frontend Display Ready:")
                    print(f"     Data Table: {'✅' if has_data_table else '❌'}")
                    print(f"     Charts: {'✅' if has_chart else '❌'}")
                    print(f"     Narrative: {'✅' if has_narrative else '❌'}")
                    
                else:
                    print(f"❌ Error: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ Exception: {type(e).__name__}: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 TEST COMPLETE!")
    print("\nTo see the results in the browser:")
    print("1. Open http://localhost:3000")
    print("2. Enter one of the test queries")
    print("3. Click 'Analyze' and wait for results")
    print("\nThe UI will display:")
    print("- Summary of agents used")
    print("- Data tables with renewable energy data")
    print("- Chart visualizations (placeholder)")
    print("- Narrative analysis text")

if __name__ == "__main__":
    asyncio.run(test_complete_flow())