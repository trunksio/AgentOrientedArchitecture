"""Visualization Agent main entry point"""
import sys
sys.path.append('/app/shared')

import asyncio
from agent_runner import AgentRunner
from viz_agent import VisualizationAgent

if __name__ == "__main__":
    runner = AgentRunner(VisualizationAgent)
    asyncio.run(runner.run())
