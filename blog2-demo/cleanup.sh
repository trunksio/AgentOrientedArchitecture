#!/bin/bash
# Agent Oriented Architecture: Directory Cleanup Script

echo "Cleaning up redundant documentation files..."

# Remove redundant planning documents
echo "Removing outdated planning documents..."
rm -f IMPLEMENTATION_FIX_PLAN.md
rm -f AGENT_REFACTORING_GUIDE.md
rm -f REFACTORING_ACTION_PLAN.md
rm -f FIX_SUMMARY.md
rm -f FIX_PLAN_README.md
rm -f REVISED_IMPLEMENTATION_PLAN.md
rm -f AGENT_REFACTORING_ANALYSIS.md
rm -f IMPLEMENTATION_REVIEW.md
rm -f ARCHITECTURE_VISION.md
rm -f DOCUMENT_GUIDE.md
rm -f EXECUTIVE_SUMMARY.md
rm -f CURRENT_VS_DESIRED_STATE.md
rm -f README_IMPLEMENTATION_GUIDE.md
rm -f DOCUMENT_INDEX.md

# Remove outdated status files
echo "Removing outdated status files..."
rm -f DEMO_STATUS.md
rm -f ROADMAP.md
rm -f THREE_PILLARS_EXAMPLE.md

# Remove redundant test files
echo "Removing redundant test files..."
rm -f test_agent_collaboration.py
rm -f test_agent_connectivity.py
rm -f test_autonomous_agents.py
rm -f test_backend_connectivity.py
rm -f test_distributed_agents.py
rm -f test_frontend_browser.html
rm -f test_frontend_ui.py
rm -f test_live_agent_addition.py
rm -f test_ui_improvements.py
rm -f debug_agent_communication.py
rm -f debug_agents.sh

echo "Cleanup complete!"

echo ""
echo "Remaining core files:"
ls -la *.md *.py 2>/dev/null | grep -E "(README|ARCHITECTURE|AGENT_BLUEPRINT|BLOG_PLAN|DEMO_SCENARIOS|IMPLEMENTATION_GUIDE|PROJECT_SUMMARY|TROUBLESHOOTING|demo_live_agent_addition|test_complete_flow)"

echo ""
echo "Directory is now clean and focused for blog implementation."