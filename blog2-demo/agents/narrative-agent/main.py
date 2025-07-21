"""Narrative Agent main entry point"""
import sys
sys.path.append('/app/shared')

import asyncio
from agent_runner import AgentRunner
from narrative_agent import NarrativeAgent

if __name__ == "__main__":
    runner = AgentRunner(NarrativeAgent)
    asyncio.run(runner.run())
