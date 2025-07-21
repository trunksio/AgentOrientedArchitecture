"""Data Agent main entry point"""
import sys
sys.path.append('/app/shared')

import asyncio
from agent_runner import AgentRunner
from data_agent import DataAgent

if __name__ == "__main__":
    runner = AgentRunner(DataAgent)
    asyncio.run(runner.run())