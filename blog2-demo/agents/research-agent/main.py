"""Research Agent main entry point"""
import sys
sys.path.append('/app/shared')

import asyncio
from agent_runner import AgentRunner
from research_agent import ResearchAgent

if __name__ == "__main__":
    runner = AgentRunner(ResearchAgent)
    asyncio.run(runner.run())
