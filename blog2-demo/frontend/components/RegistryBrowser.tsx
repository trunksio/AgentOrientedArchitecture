'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface Agent {
  id: string
  name: string
  type: string
  description: string
  capabilities: Array<{
    name: string
    description: string
    output_type: string
    examples: string[]
  }>
  registered_at: string
  metadata?: any
}

export default function RegistryBrowser() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchAgents()
  }, [])

  const fetchAgents = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/registry/agents`)
      const data = await response.json()
      setAgents(data)
    } catch (error) {
      console.error('Failed to fetch agents:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const filteredAgents = agents.filter(agent => 
    agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    agent.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    agent.type.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-semibold mb-4">A2A Registry Browser</h2>
        
        <input
          type="text"
          placeholder="Search agents..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-aoa-primary focus:border-transparent dark:bg-slate-700 dark:border-slate-600"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {isLoading ? (
            <div className="text-center py-8 text-gray-500">Loading agents...</div>
          ) : filteredAgents.length === 0 ? (
            <div className="text-center py-8 text-gray-500">No agents found</div>
          ) : (
            filteredAgents.map((agent) => (
              <motion.div
                key={agent.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setSelectedAgent(agent)}
                className={`p-4 rounded-lg cursor-pointer transition-colors ${
                  selectedAgent?.id === agent.id
                    ? 'bg-aoa-primary/10 border-2 border-aoa-primary'
                    : 'bg-gray-50 dark:bg-slate-700 hover:bg-gray-100 dark:hover:bg-slate-600'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold">{agent.name}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                      {agent.description}
                    </p>
                  </div>
                  <span className="text-xs px-2 py-1 bg-aoa-secondary/20 text-aoa-secondary rounded">
                    {agent.type}
                  </span>
                </div>
              </motion.div>
            ))
          )}
        </div>

        <AnimatePresence mode="wait">
          {selectedAgent && (
            <motion.div
              key={selectedAgent.id}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="bg-gray-50 dark:bg-slate-700 rounded-lg p-6"
            >
              <h3 className="text-xl font-semibold mb-4">{selectedAgent.name}</h3>
              
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400">Type</h4>
                  <p className="text-sm">{selectedAgent.type}</p>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400">Description</h4>
                  <p className="text-sm">{selectedAgent.description}</p>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                    Capabilities ({selectedAgent.capabilities.length})
                  </h4>
                  <div className="space-y-3">
                    {selectedAgent.capabilities.map((cap, index) => (
                      <div key={index} className="bg-white dark:bg-slate-800 rounded p-3">
                        <h5 className="font-medium text-sm">{cap.name}</h5>
                        <p className="text-xs text-gray-600 dark:text-gray-300 mt-1">
                          {cap.description}
                        </p>
                        <div className="flex items-center gap-2 mt-2">
                          <span className="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded">
                            {cap.output_type}
                          </span>
                        </div>
                        {cap.examples.length > 0 && (
                          <div className="mt-2">
                            <p className="text-xs text-gray-500 dark:text-gray-400">Examples:</p>
                            <ul className="text-xs text-gray-600 dark:text-gray-300 mt-1 list-disc list-inside">
                              {cap.examples.slice(0, 2).map((ex, i) => (
                                <li key={i}>{ex}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {selectedAgent.metadata?.keywords && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Keywords</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedAgent.metadata.keywords.map((keyword: string, i: number) => (
                        <span key={i} className="text-xs px-2 py-1 bg-gray-200 dark:bg-slate-600 rounded">
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}