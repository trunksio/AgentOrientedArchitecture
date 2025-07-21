"""GUI Agent main entry point"""
import sys
sys.path.append('/app/shared')

import asyncio
from agent_runner import AgentRunner
from gui_agent import GUIAgent

if __name__ == "__main__":
    runner = AgentRunner(GUIAgent)
    asyncio.run(runner.run())
