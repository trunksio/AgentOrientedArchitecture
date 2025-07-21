'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import DynamicComponent from './DynamicComponent'
import AgentDiscovery from './AgentDiscovery'
import { AnimatePresence } from 'framer-motion'

// Timeout helper function
async function fetchWithTimeout(url: string, options: RequestInit & { timeout?: number } = {}) {
  const { timeout = 60000 } = options; // 60 seconds default timeout
  
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal
    });
    clearTimeout(id);
    return response;
  } catch (error) {
    clearTimeout(id);
    throw error;
  }
}

interface GUIAgentProps {
  generatedComponents: any[]
  setGeneratedComponents: (components: any[]) => void
  discoveredAgents: any[]
  setDiscoveredAgents: (agents: any[]) => void
  currentQuery: string
  setCurrentQuery: (query: string) => void
}

export default function GUIAgent({
  generatedComponents,
  setGeneratedComponents,
  discoveredAgents,
  setDiscoveredAgents,
  currentQuery,
  setCurrentQuery
}: GUIAgentProps) {
  const [query, setQuery] = useState(currentQuery)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const exampleQueries = [
    "Help me understand the renewable energy landscape",
    "Why is solar growing faster than wind?",
    "Show me renewable energy trends with visualizations",
    "Compare renewable adoption across countries"
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setIsProcessing(true)
    setGeneratedComponents([])
    setError(null)
    setCurrentQuery(query)
    
    try {
      // Discover relevant agents
      const discoveryResponse = await fetchWithTimeout(`${process.env.NEXT_PUBLIC_API_URL}/api/registry/discover`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          intent: query,
          max_results: 5
        }),
        timeout: 30000 // 30 seconds for discovery
      })
      const agents = await discoveryResponse.json()
      setDiscoveredAgents(agents)

      // Call the orchestration endpoint with extended timeout
      const orchestrationResponse = await fetchWithTimeout(`${process.env.NEXT_PUBLIC_API_URL}/api/orchestrate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query: query,
          context: {
            discovered_agents: agents.map((a: any) => a.agent.id)
          }
        }),
        timeout: 120000 // 2 minutes for orchestration
      })
      
      if (!orchestrationResponse.ok) {
        throw new Error(`Orchestration failed: ${orchestrationResponse.statusText}`)
      }
      
      const result = await orchestrationResponse.json()
      
      // Process results
      if (result.results) {
        const components = []
        
        // Check if we have outputs
        if (result.results.outputs) {
          for (const [agentId, output] of Object.entries(result.results.outputs)) {
            // Skip empty outputs
            if (!output) continue
            
            components.push({
              type: 'agent_result',
              agent: agentId,
              data: output
            })
          }
        }
        
        // Check if we have a ui_spec
        if (result.results.ui_spec?.components) {
          result.results.ui_spec.components.forEach((comp: any) => {
            components.push(comp)
          })
        }
        
        // If no structured components but we have results, show them
        if (components.length === 0 && result.results) {
          components.push({
            type: 'message',
            data: {
              title: 'Query Results',
              content: JSON.stringify(result.results, null, 2)
            }
          })
        }
        
        setGeneratedComponents(components)
      } else if (result.error) {
        throw new Error(result.error)
      } else {
        // If we got a response but no results, show what we got
        const components = [{
          type: 'message',
          data: {
            title: 'Response',
            content: JSON.stringify(result, null, 2)
          }
        }]
        setGeneratedComponents(components)
      }
      
    } catch (error: any) {
      console.error('Error processing query:', error)
      if (error.name === 'AbortError') {
        setError('Request timed out. The agents are taking longer than expected. Please try a simpler query or try again.')
      } else {
        setError(error.message || 'Failed to process query')
      }
    } finally {
      setIsProcessing(false)
    }
  }

  const handleExampleClick = (example: string) => {
    setQuery(example)
  }

  return (
    <div className="max-w-4xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          Ask the Agents
        </h2>
        <p className="text-gray-600 dark:text-gray-300">
          Watch as AI agents discover each other, collaborate, and build a custom interface for your query.
        </p>
      </motion.div>

      {/* Query Form */}
      <motion.form 
        onSubmit={handleSubmit} 
        className="mb-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
      >
        <div className="relative">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask anything about renewable energy..."
            className="w-full p-4 pr-32 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-aoa-primary focus:border-transparent resize-none"
            rows={3}
            disabled={isProcessing}
          />
          <button
            type="submit"
            disabled={isProcessing || !query.trim()}
            className="absolute bottom-4 right-4 px-6 py-2 bg-gradient-to-r from-aoa-primary to-aoa-accent text-white font-medium rounded-lg hover:shadow-lg transform transition-all hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
          >
            {isProcessing ? (
              <span className="flex items-center space-x-2">
                <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                <span>Processing...</span>
              </span>
            ) : (
              'Send Query'
            )}
          </button>
        </div>
      </motion.form>

      {/* Example Queries */}
      <motion.div 
        className="mb-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Try these examples:</p>
        <div className="flex flex-wrap gap-2">
          {exampleQueries.map((example, idx) => (
            <button
              key={idx}
              onClick={() => handleExampleClick(example)}
              className="px-3 py-1 text-sm bg-gray-100 dark:bg-slate-700 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-slate-600 transition-colors"
            >
              {example}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Error Display */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"
        >
          <div className="flex items-start space-x-3">
            <svg className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h3 className="text-sm font-medium text-red-800 dark:text-red-200">Error</h3>
              <p className="text-sm text-red-700 dark:text-red-300 mt-1">{error}</p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Processing Indicator */}
      {isProcessing && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mb-8 p-6 bg-blue-50 dark:bg-blue-900/20 rounded-xl"
        >
          <div className="flex items-center space-x-4">
            <div className="relative">
              <div className="w-12 h-12 border-4 border-blue-200 dark:border-blue-800 rounded-full animate-pulse" />
              <div className="absolute inset-0 w-12 h-12 border-4 border-t-blue-600 dark:border-t-blue-400 rounded-full animate-spin" />
            </div>
            <div>
              <p className="text-blue-900 dark:text-blue-100 font-medium">Agents are working on your query...</p>
              <p className="text-blue-700 dark:text-blue-300 text-sm">This may take up to 2 minutes for complex queries</p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Agent Discovery Display */}
      {discoveredAgents.length > 0 && !isProcessing && (
        <motion.div 
          className="mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <AgentDiscovery agents={discoveredAgents} />
        </motion.div>
      )}

      {/* Generated Components */}
      <AnimatePresence>
        {generatedComponents.length > 0 && (
          <motion.div 
            className="space-y-6"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Generated Results
            </h3>
            {generatedComponents.map((component, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <DynamicComponent component={component} />
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}