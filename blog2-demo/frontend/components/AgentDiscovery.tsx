'use client'

import { motion } from 'framer-motion'

interface AgentDiscoveryProps {
  agents: any[]
}

export default function AgentDiscovery({ agents }: AgentDiscoveryProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6"
    >
      <h3 className="text-lg font-semibold mb-4">Agent Discovery Process</h3>
      
      <div className="space-y-3">
        {agents.map((result: any, index: number) => (
          <motion.div
            key={result.agent.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-center justify-between p-3 bg-gray-50 dark:bg-slate-700 rounded-lg"
          >
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="font-medium">{result.agent.name}</span>
                <span className="text-xs px-2 py-1 bg-aoa-primary/10 text-aoa-primary rounded">
                  {result.agent.type}
                </span>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                {result.agent.description}
              </p>
              {result.matched_capabilities.length > 0 && (
                <div className="flex gap-2 mt-2">
                  {result.matched_capabilities.map((cap: string) => (
                    <span key={cap} className="text-xs px-2 py-1 bg-gray-200 dark:bg-slate-600 rounded">
                      {cap}
                    </span>
                  ))}
                </div>
              )}
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-aoa-primary">
                {(result.relevance_score * 100).toFixed(0)}%
              </div>
              <div className="text-xs text-gray-500">relevance</div>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}