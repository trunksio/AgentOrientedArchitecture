import asyncio
import sys
import os

# Add parent directory to path to import shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.standard_agent_runner import StandardAgentRunner
from research_agent import ResearchAgent

async def main():
    runner = StandardAgentRunner(ResearchAgent)
    await runner.run()

if __name__ == "__main__":
    asyncio.run(main())
