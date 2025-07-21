'use client'

import { motion } from 'framer-motion'

interface AgentStatusProps {
  agents: any[]
  isConnected: boolean
  onRefresh: () => void
}

export default function AgentStatus({ agents, isConnected, onRefresh }: AgentStatusProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">System Status</h3>
        <button
          onClick={onRefresh}
          className="text-sm text-aoa-primary hover:text-blue-600"
        >
          Refresh
        </button>
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600 dark:text-gray-300">Backend</span>
          <span className={`flex items-center gap-2 text-sm ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-600' : 'bg-red-600'}`} />
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>

        <div className="border-t pt-3">
          <h4 className="text-sm font-medium mb-2">Registered Agents ({agents.length})</h4>
          <div className="space-y-2">
            {agents.length === 0 ? (
              <p className="text-xs text-gray-500">No agents registered yet</p>
            ) : (
              agents.map((agent: any) => (
                <div key={agent.id} className="text-xs space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{agent.name}</span>
                    <span className="text-gray-500">{agent.type}</span>
                  </div>
                  <p className="text-gray-600 dark:text-gray-400">{agent.description}</p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </motion.div>
  )
}