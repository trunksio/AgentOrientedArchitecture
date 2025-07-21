'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface AgentConfig {
  id: string
  name: string
  llm_provider: 'anthropic' | 'openai' | 'none'
  llm_model: string
  api_key?: string
  temperature: number
  enabled: boolean
}

interface AgentConfigurationProps {
  agents?: any[]
  onRefresh?: () => void
}

export default function AgentConfiguration({ agents: propAgents, onRefresh }: AgentConfigurationProps = {}) {
  const [agents, setAgents] = useState<any[]>(propAgents || [])
  const [agentConfigs, setAgentConfigs] = useState<AgentConfig[]>([])
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)
  const [isSaving, setIsSaving] = useState(false)
  const [saveStatus, setSaveStatus] = useState<{ type: 'success' | 'error', message: string } | null>(null)

  useEffect(() => {
    if (!propAgents) {
      fetchAgents()
    }
  }, [propAgents])

  const fetchAgents = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/registry/agents`)
      const data = await response.json()
      setAgents(data)
    } catch (error) {
      console.error('Failed to fetch agents:', error)
    }
  }

  useEffect(() => {
    // Initialize agent configurations
    const configs: AgentConfig[] = agents.map(agent => ({
      id: agent.id,
      name: agent.name,
      llm_provider: 'anthropic',
      llm_model: 'claude-3-7-sonnet-20250219',
      temperature: 0.7,
      enabled: true
    }))
    setAgentConfigs(configs)
  }, [agents])

  const handleConfigChange = (agentId: string, field: keyof AgentConfig, value: any) => {
    setAgentConfigs(prev => prev.map(config => 
      config.id === agentId ? { ...config, [field]: value } : config
    ))
  }

  const handleSaveConfig = async (agentId: string) => {
    setIsSaving(true)
    setSaveStatus(null)
    
    const config = agentConfigs.find(c => c.id === agentId)
    if (!config) return

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/agents/${agentId}/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          llm_config: {
            provider: config.llm_provider,
            model: config.llm_model,
            api_key: config.api_key,
            temperature: config.temperature
          },
          enabled: config.enabled
        })
      })

      if (response.ok) {
        setSaveStatus({ type: 'success', message: 'Configuration saved successfully' })
        onRefresh && onRefresh()
      } else {
        throw new Error('Failed to save configuration')
      }
    } catch (error) {
      setSaveStatus({ type: 'error', message: 'Failed to save configuration' })
    } finally {
      setIsSaving(false)
      setTimeout(() => setSaveStatus(null), 3000)
    }
  }

  const llmProviders = [
    { value: 'anthropic', label: 'Anthropic (Claude)', models: ['claude-3-7-sonnet-20250219', 'claude-3-opus-20240229', 'claude-3-sonnet-20240229'] },
    { value: 'openai', label: 'OpenAI (GPT)', models: ['gpt-4-turbo-preview', 'gpt-4', 'gpt-3.5-turbo'] },
    { value: 'none', label: 'No LLM', models: [] }
  ]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Agent Configuration</h2>
        <p className="text-gray-600 dark:text-gray-300">
          Configure LLM settings for each agent. API keys are stored securely and never exposed.
        </p>
      </div>

      {/* Agent List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {agentConfigs.map(agent => (
          <motion.div
            key={agent.id}
            whileHover={{ scale: 1.02 }}
            onClick={() => setSelectedAgent(agent.id)}
            className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
              selectedAgent === agent.id
                ? 'border-aoa-primary bg-aoa-primary/5 dark:bg-aoa-primary/10'
                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold text-gray-900 dark:text-white">{agent.name}</h3>
              <div className={`w-3 h-3 rounded-full ${agent.enabled ? 'bg-green-500' : 'bg-gray-400'}`} />
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {agent.llm_provider === 'none' ? 'No LLM' : `${agent.llm_provider} - ${agent.llm_model}`}
            </p>
          </motion.div>
        ))}
      </div>

      {/* Configuration Panel */}
      <AnimatePresence mode="wait">
        {selectedAgent && (
          <motion.div
            key={selectedAgent}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="bg-gray-50 dark:bg-slate-900 rounded-xl p-6 border border-gray-200 dark:border-gray-700"
          >
            {(() => {
              const config = agentConfigs.find(c => c.id === selectedAgent)
              if (!config) return null

              return (
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Configure {config.name}
                  </h3>

                  {/* Enable/Disable Toggle */}
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Agent Enabled
                    </label>
                    <button
                      onClick={() => handleConfigChange(config.id, 'enabled', !config.enabled)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        config.enabled ? 'bg-aoa-primary' : 'bg-gray-300 dark:bg-gray-600'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          config.enabled ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>

                  {/* LLM Provider */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      LLM Provider
                    </label>
                    <select
                      value={config.llm_provider}
                      onChange={(e) => handleConfigChange(config.id, 'llm_provider', e.target.value)}
                      className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-aoa-primary focus:border-transparent"
                    >
                      {llmProviders.map(provider => (
                        <option key={provider.value} value={provider.value}>
                          {provider.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* LLM Model */}
                  {config.llm_provider !== 'none' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Model
                      </label>
                      <select
                        value={config.llm_model}
                        onChange={(e) => handleConfigChange(config.id, 'llm_model', e.target.value)}
                        className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-aoa-primary focus:border-transparent"
                      >
                        {llmProviders
                          .find(p => p.value === config.llm_provider)
                          ?.models.map(model => (
                            <option key={model} value={model}>
                              {model}
                            </option>
                          ))}
                      </select>
                    </div>
                  )}

                  {/* API Key */}
                  {config.llm_provider !== 'none' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        API Key
                      </label>
                      <input
                        type="password"
                        value={config.api_key || ''}
                        onChange={(e) => handleConfigChange(config.id, 'api_key', e.target.value)}
                        placeholder={`Enter ${config.llm_provider === 'anthropic' ? 'Anthropic' : 'OpenAI'} API key`}
                        className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-aoa-primary focus:border-transparent"
                      />
                      <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                        API keys are encrypted and stored securely. Never shared or exposed.
                      </p>
                    </div>
                  )}

                  {/* Temperature */}
                  {config.llm_provider !== 'none' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Temperature: {config.temperature}
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.1"
                        value={config.temperature}
                        onChange={(e) => handleConfigChange(config.id, 'temperature', parseFloat(e.target.value))}
                        className="w-full"
                      />
                      <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                        <span>Precise</span>
                        <span>Creative</span>
                      </div>
                    </div>
                  )}

                  {/* Save Button */}
                  <div className="flex items-center justify-between pt-4">
                    <button
                      onClick={() => handleSaveConfig(config.id)}
                      disabled={isSaving}
                      className="px-6 py-2 bg-aoa-primary text-white rounded-lg hover:bg-aoa-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      {isSaving ? 'Saving...' : 'Save Configuration'}
                    </button>

                    {saveStatus && (
                      <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 20 }}
                        className={`text-sm ${
                          saveStatus.type === 'success' ? 'text-green-600' : 'text-red-600'
                        }`}
                      >
                        {saveStatus.message}
                      </motion.div>
                    )}
                  </div>
                </div>
              )
            })()}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Global Settings */}
      <div className="mt-8 p-6 bg-amber-50 dark:bg-amber-900/20 rounded-xl border border-amber-200 dark:border-amber-800">
        <div className="flex items-start space-x-3">
          <svg className="w-5 h-5 text-amber-600 dark:text-amber-400 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h4 className="text-sm font-medium text-amber-800 dark:text-amber-200">Note on API Keys</h4>
            <p className="text-sm text-amber-700 dark:text-amber-300 mt-1">
              API keys are stored encrypted on the backend and are never exposed to the frontend. 
              Each agent can use different LLM providers and models independently.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
} 