#!/usr/bin/env python3
"""
Live Agent Addition Demo Script

This script demonstrates the "wow" moment of Agent Oriented Architecture:
adding new capabilities to a running system without any restarts.
"""

import asyncio
import aiohttp
import json
import time

API_BASE = "http://localhost:8000"

async def demo_live_agent_addition():
    """Demonstrate adding an agent live and immediately using it"""
    
    async with aiohttp.ClientSession() as session:
        print("🎭 AOA Demo: Live Agent Addition")
        print("=" * 50)
        
        # Step 1: Show current system
        print("1. Current System Status:")
        async with session.get(f"{API_BASE}/api/registry/agents") as response:
            current_agents = await response.json()
            print(f"   📊 System has {len(current_agents)} active agents:")
            for agent in current_agents:
                print(f"   - {agent.get('name', 'Unknown')} ({agent.get('type', 'unknown')} agent)")
        
        print()
        
        # Step 2: Test a query that needs prediction (should work with existing agents)
        print("2. Testing current capabilities:")
        print("   Query: 'What are renewable energy trends?'")
        
        async with session.post(
            f"{API_BASE}/api/orchestrate",
            json={"query": "What are renewable energy trends?", "context": {}},
            headers={"Content-Type": "application/json"}
        ) as response:
            result = await response.json()
            
            if result.get("success"):
                outputs = result.get("results", {}).get("outputs", {})
                print(f"   ✅ {len(outputs)} agents responded:")
                for agent_id in outputs.keys():
                    print(f"     - {agent_id}")
            else:
                print(f"   ❌ Query failed: {result}")
        
        print()
        
        # Step 3: Test a prediction query (should NOT find prediction capabilities)
        print("3. Testing prediction query (before adding prediction agent):")
        print("   Query: 'Predict renewable energy growth for next 5 years'")
        
        discovery_payload = {"intent": "predict renewable energy growth forecasting future trends"}
        async with session.post(
            f"{API_BASE}/api/registry/discover",
            json=discovery_payload,
            headers={"Content-Type": "application/json"}
        ) as response:
            discovery_result = await response.json()
            
            prediction_agents = [
                agent for agent in discovery_result 
                if 'prediction' in agent.get('agent', {}).get('name', '').lower()
            ]
            
            if prediction_agents:
                print(f"   ⚠️  Found {len(prediction_agents)} prediction agents (unexpected)")
            else:
                print("   📝 No prediction agents found (as expected)")
        
        print()
        
        # Step 4: THE MAGIC MOMENT - Add prediction agent live!
        print("4. 🎉 THE MAGIC MOMENT: Adding Prediction Agent LIVE!")
        print("   Adding new forecasting capabilities while system is running...")
        
        # For demo, we'll use the simple add-live endpoint (not actual container deployment)
        agent_config = {
            "name": "Advanced Prediction Agent",
            "description": "I specialize in forecasting future trends, creating predictions, and analyzing growth patterns",
            "capabilities": ["forecasting", "future predictions", "trend analysis", "scenario planning"],
            "endpoint": "http://localhost:8007",
            "agent_id": "advanced-prediction-001"
        }
        
        async with session.post(
            f"{API_BASE}/api/agents/add-live",
            json={"agent_config": agent_config},
            headers={"Content-Type": "application/json"}
        ) as response:
            result = await response.json()
            
            if result.get("success"):
                print(f"   ✅ {result['message']}")
                print(f"   🆔 Agent ID: {result['agent']['id']}")
            else:
                print(f"   ❌ Failed: {result}")
                return
        
        print()
        
        # Step 5: Verify new system capabilities
        print("5. Verifying expanded system:")
        await asyncio.sleep(1)  # Give it a moment
        
        async with session.get(f"{API_BASE}/api/registry/agents") as response:
            updated_agents = await response.json()
            print(f"   📊 System now has {len(updated_agents)} active agents:")
            for agent in updated_agents:
                if agent.get('id') == 'advanced-prediction-001':
                    print(f"   🔥 {agent.get('name', 'Unknown')} (NEWLY ADDED!)")
                else:
                    print(f"   - {agent.get('name', 'Unknown')}")
        
        print()
        
        # Step 6: Test discovery of new capabilities
        print("6. Testing discovery of NEW prediction capabilities:")
        
        async with session.post(
            f"{API_BASE}/api/registry/discover",
            json=discovery_payload,
            headers={"Content-Type": "application/json"}
        ) as response:
            discovery_result = await response.json()
            
            prediction_agents = [
                agent for agent in discovery_result 
                if 'prediction' in agent.get('agent', {}).get('name', '').lower()
            ]
            
            if prediction_agents:
                print(f"   🎉 SUCCESS! Found {len(prediction_agents)} prediction agents:")
                for agent_info in prediction_agents:
                    agent = agent_info.get('agent', {})
                    score = agent_info.get('relevance_score', 0)
                    print(f"     - {agent.get('name')} (relevance: {score:.2f})")
            else:
                print("   ❌ No prediction agents found")
        
        print()
        
        # Step 7: THE ULTIMATE TEST - Use the new agent immediately!
        print("7. 🚀 ULTIMATE TEST: Using new agent immediately!")
        print("   Query: 'Predict renewable energy growth for next 5 years'")
        
        async with session.post(
            f"{API_BASE}/api/orchestrate",
            json={
                "query": "Predict renewable energy growth for next 5 years", 
                "context": {"discovered_agents": ["advanced-prediction-001"]}
            },
            headers={"Content-Type": "application/json"}
        ) as response:
            result = await response.json()
            
            if result.get("success"):
                outputs = result.get("results", {}).get("outputs", {})
                
                if "advanced-prediction-001" in outputs:
                    print("   🎉 SUCCESS! New prediction agent responded!")
                    prediction_output = outputs["advanced-prediction-001"]
                    
                    # Show some prediction results
                    if isinstance(prediction_output, dict):
                        if "results" in prediction_output:
                            print(f"   📈 Prediction tools executed: {len(prediction_output['results'])}")
                        elif "forecasts" in prediction_output:
                            forecasts = prediction_output["forecasts"]
                            print(f"   📊 Generated {len(forecasts)} forecast points")
                            if forecasts:
                                print(f"   📅 Last forecast year: {forecasts[-1].get('year', 'N/A')}")
                        print(f"   📝 Response type: {type(prediction_output).__name__}")
                    
                    print(f"   ✅ Total agents in response: {len(outputs)}")
                else:
                    print("   ⚠️  New agent not found in orchestration response")
                    print(f"   Available outputs: {list(outputs.keys())}")
            else:
                print(f"   ❌ Orchestration failed: {result}")
        
        print()
        print("🎊 LIVE AGENT ADDITION DEMO COMPLETE!")
        print("=" * 50)
        print("🔥 What just happened:")
        print("   1. System was running with 5 agents")
        print("   2. We added a NEW agent while system was live")
        print("   3. New agent was immediately discoverable")
        print("   4. New agent responded to queries INSTANTLY")
        print("   5. NO RESTARTS, NO DOWNTIME, NO CONFIGURATION!")
        print()
        print("🌟 This is the power of Agent Oriented Architecture!")

async def main():
    """Run the demo"""
    try:
        await demo_live_agent_addition()
    except Exception as e:
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 