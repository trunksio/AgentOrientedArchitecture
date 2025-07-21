'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface AgentType {
  type: string
  name: string
  description: string
  capabilities: string[]
  ready_to_deploy: boolean
  note?: string
}

interface LiveAgentManagerProps {
  onAgentAdded?: (agent: any) => void
}

export default function LiveAgentManager({ onAgentAdded }: LiveAgentManagerProps) {
  const [availableTypes, setAvailableTypes] = useState<AgentType[]>([])
  const [isDeploying, setIsDeploying] = useState(false)
  const [deploymentStatus, setDeploymentStatus] = useState<string>('')
  const [selectedType, setSelectedType] = useState<string>('')
  const [agentName, setAgentName] = useState<string>('')

  useEffect(() => {
    fetchAvailableTypes()
  }, [])

  const fetchAvailableTypes = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/agents/available-types`)
      const data = await response.json()
      setAvailableTypes(data.agent_types || [])
    } catch (error) {
      console.error('Failed to fetch available agent types:', error)
    }
  }

  const deployAgent = async () => {
    if (!selectedType || !agentName) {
      setDeploymentStatus('Please select an agent type and enter a name')
      return
    }

    setIsDeploying(true)
    setDeploymentStatus('Starting deployment...')

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/agents/deploy`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          agent_type: selectedType,
          agent_name: agentName
        })
      })

      const result = await response.json()

      if (result.success) {
        setDeploymentStatus(result.message)
        
        // Wait for deployment completion (listen for WebSocket updates)
        setTimeout(() => {
          setDeploymentStatus('Agent deployed successfully! 🎉')
          setIsDeploying(false)
          onAgentAdded?.(result.agent)
          
          // Reset form
          setSelectedType('')
          setAgentName('')
        }, 5000)
      } else {
        setDeploymentStatus(`Deployment failed: ${result.message}`)
        setIsDeploying(false)
      }
    } catch (error) {
      setDeploymentStatus(`Deployment error: ${error}`)
      setIsDeploying(false)
    }
  }

  const addExistingAgent = async () => {
    // For demo purposes, simulate adding a running agent
    const agentConfig = {
      name: "Prediction Agent",
      description: "I specialize in forecasting future trends and creating predictions",
      capabilities: ["forecasting", "trend analysis", "predictions", "scenario planning"],
      endpoint: "http://localhost:8007",
      agent_id: "prediction-agent-001"
    }

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/agents/add-live`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          agent_config: agentConfig
        })
      })

      const result = await response.json()

      if (result.success) {
        setDeploymentStatus('Agent added successfully! 🎉')
        onAgentAdded?.(result.agent)
      } else {
        setDeploymentStatus(`Failed to add agent: ${result.message}`)
      }
    } catch (error) {
      setDeploymentStatus(`Error adding agent: ${error}`)
    }
  }

  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg p-6 shadow-lg">
      <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">
        Live Agent Management
      </h3>
      
      <div className="space-y-6">
        {/* Quick Add Demo Agent */}
        <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
          <h4 className="font-semibold mb-2 text-gray-800 dark:text-gray-200">
            Quick Demo: Add Prediction Agent
          </h4>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
            Click to add a pre-configured Prediction Agent to the system
          </p>
          <button
            onClick={addExistingAgent}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Add Prediction Agent
          </button>
        </div>

        {/* Agent Type Selection */}
        <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
          <h4 className="font-semibold mb-2 text-gray-800 dark:text-gray-200">
            Deploy New Agent
          </h4>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Agent Type
              </label>
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-slate-700 text-gray-900 dark:text-white"
              >
                <option value="">Select an agent type...</option>
                {availableTypes.map((type) => (
                  <option 
                    key={type.type} 
                    value={type.type}
                    disabled={!type.ready_to_deploy}
                  >
                    {type.name} {!type.ready_to_deploy && '(Coming Soon)'}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Agent Name
              </label>
              <input
                type="text"
                value={agentName}
                onChange={(e) => setAgentName(e.target.value)}
                placeholder="Enter a unique name for the agent"
                className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-slate-700 text-gray-900 dark:text-white"
              />
            </div>

            {selectedType && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg"
              >
                {availableTypes.find(t => t.type === selectedType) && (
                  <div>
                    <p className="text-sm text-blue-800 dark:text-blue-200 font-medium mb-1">
                      {availableTypes.find(t => t.type === selectedType)?.description}
                    </p>
                    <p className="text-xs text-blue-600 dark:text-blue-300">
                      Capabilities: {availableTypes.find(t => t.type === selectedType)?.capabilities.join(', ')}
                    </p>
                  </div>
                )}
              </motion.div>
            )}

            <button
              onClick={deployAgent}
              disabled={isDeploying || !selectedType || !agentName}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white py-2 px-4 rounded-lg transition-colors"
            >
              {isDeploying ? 'Deploying...' : 'Deploy Agent'}
            </button>
          </div>
        </div>

        {/* Deployment Status */}
        <AnimatePresence>
          {deploymentStatus && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className={`p-3 rounded-lg ${
                deploymentStatus.includes('success') || deploymentStatus.includes('🎉')
                  ? 'bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-200'
                  : deploymentStatus.includes('error') || deploymentStatus.includes('failed')
                  ? 'bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-200'
                  : 'bg-blue-50 dark:bg-blue-900/20 text-blue-800 dark:text-blue-200'
              }`}
            >
              <div className="flex items-center">
                {isDeploying && (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
                )}
                <span className="text-sm font-medium">{deploymentStatus}</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
} 