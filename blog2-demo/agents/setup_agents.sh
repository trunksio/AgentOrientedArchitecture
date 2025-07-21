#!/bin/bash

# Script to set up all agent containers

# Update imports in agent files
for agent in viz-agent research-agent narrative-agent gui-agent; do
    if [ -f "$agent/${agent//-/_}.py" ]; then
        # Update imports
        sed -i.bak '1s/^/import sys\nsys.path.append("\/app\/shared")\n/' "$agent/${agent//-/_}.py"
        sed -i.bak 's/from \.base_agent/from base_agent/g' "$agent/${agent//-/_}.py"
        sed -i.bak 's/from \.\.base_agent/from base_agent/g' "$agent/${agent//-/_}.py"
        
        # Add AGENT_TYPE after class definition
        agent_type=$(echo $agent | cut -d'-' -f1)
        sed -i.bak "/^class.*BaseAgent/a\\    AGENT_TYPE = \"$agent_type\"\\n" "$agent/${agent//-/_}.py"
        
        # Remove backup files
        rm "$agent/${agent//-/_}.py.bak"
    fi
done

# Create main.py for each agent
cat > viz-agent/main.py << 'EOF'
"""Visualization Agent main entry point"""
import sys
sys.path.append('/app/shared')

from agent_runner import AgentRunner
from viz_agent import VisualizationAgent

if __name__ == "__main__":
    runner = AgentRunner(VisualizationAgent, port=8082)
    runner.run()
EOF

cat > research-agent/main.py << 'EOF'
"""Research Agent main entry point"""
import sys
sys.path.append('/app/shared')

from agent_runner import AgentRunner
from research_agent import ResearchAgent

if __name__ == "__main__":
    runner = AgentRunner(ResearchAgent, port=8083)
    runner.run()
EOF

cat > narrative-agent/main.py << 'EOF'
"""Narrative Agent main entry point"""
import sys
sys.path.append('/app/shared')

from agent_runner import AgentRunner
from narrative_agent import NarrativeAgent

if __name__ == "__main__":
    runner = AgentRunner(NarrativeAgent, port=8084)
    runner.run()
EOF

cat > gui-agent/main.py << 'EOF'
"""GUI Agent main entry point"""
import sys
sys.path.append('/app/shared')

from agent_runner import AgentRunner
from gui_agent import GUIAgent

if __name__ == "__main__":
    runner = AgentRunner(GUIAgent, port=8085)
    runner.run()
EOF

# Create Dockerfiles
for agent in viz-agent research-agent narrative-agent gui-agent; do
    port=$((8081 + $(echo "data-agent viz-agent research-agent narrative-agent gui-agent" | tr ' ' '\n' | grep -n "^$agent$" | cut -d: -f1)))
    
    cat > "$agent/Dockerfile" << EOF
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy shared requirements and install
COPY shared/requirements.txt /app/shared/requirements.txt
RUN pip install --no-cache-dir -r /app/shared/requirements.txt

# Copy agent-specific requirements and install
COPY $agent/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt || true

# Copy shared modules
COPY shared/ /app/shared/

# Copy agent files
COPY $agent/ /app/

# Expose port
EXPOSE $port

# Run the agent
CMD ["python", "main.py"]
EOF
done

echo "Agent setup complete!"