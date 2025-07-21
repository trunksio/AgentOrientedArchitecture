import asyncio
import logging
import sys
import os

# Add the shared directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from prediction_agent import PredictionAgent
from agent_runner import run_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main():
    """Main entry point for the Prediction Agent"""
    logger.info("Starting Prediction Agent...")
    
    # Create and run the agent
    agent = PredictionAgent()
    await run_agent(agent, port=8007)

if __name__ == "__main__":
    asyncio.run(main()) 