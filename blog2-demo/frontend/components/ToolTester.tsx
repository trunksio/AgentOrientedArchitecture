'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

interface Tool {
  name: string
  description: string
  agent: string
  agent_id: string
  parameters: Array<{
    name: string
    type: string
    description: string
    required: boolean
    enum?: string[]
  }>
  returns: any
  examples: any[]
}

export default function ToolTester() {
  const [tools, setTools] = useState<Tool[]>([])
  const [selectedTool, setSelectedTool] = useState<Tool | null>(null)
  const [parameters, setParameters] = useState<Record<string, any>>({})
  const [isExecuting, setIsExecuting] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchTools()
  }, [])

  const fetchTools = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/mcp/tools`)
      const data = await response.json()
      setTools(data)
    } catch (error) {
      console.error('Failed to fetch tools:', error)
    }
  }

  const handleToolSelect = (tool: Tool) => {
    setSelectedTool(tool)
    setResult(null)
    setError(null)
    
    // Initialize parameters with defaults
    const defaultParams: Record<string, any> = {}
    tool.parameters.forEach(param => {
      if (param.enum && param.enum.length > 0) {
        defaultParams[param.name] = param.enum[0]
      } else if (param.type === 'number') {
        defaultParams[param.name] = 0
      } else if (param.type === 'boolean') {
        defaultParams[param.name] = false
      } else if (param.type === 'array') {
        defaultParams[param.name] = []
      } else if (param.type === 'object') {
        defaultParams[param.name] = {}
      } else {
        defaultParams[param.name] = ''
      }
    })
    setParameters(defaultParams)
  }

  const handleParameterChange = (paramName: string, value: any) => {
    setParameters(prev => ({
      ...prev,
      [paramName]: value
    }))
  }

  const executeTool = async () => {
    if (!selectedTool) return

    setIsExecuting(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/mcp/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool: selectedTool.name,
          parameters: parameters
        })
      })

      const data = await response.json()
      
      if (data.success) {
        setResult(data.result)
      } else {
        setError(data.error || 'Tool execution failed')
      }
    } catch (error) {
      setError('Failed to execute tool: ' + error)
    } finally {
      setIsExecuting(false)
    }
  }

  const renderParameterInput = (param: any) => {
    const value = parameters[param.name]

    if (param.enum) {
      return (
        <select
          value={value}
          onChange={(e) => handleParameterChange(param.name, e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-aoa-primary focus:border-transparent dark:bg-slate-700 dark:border-slate-600"
        >
          {param.enum.map((option: string) => (
            <option key={option} value={option}>{option}</option>
          ))}
        </select>
      )
    }

    if (param.type === 'boolean') {
      return (
        <input
          type="checkbox"
          checked={value}
          onChange={(e) => handleParameterChange(param.name, e.target.checked)}
          className="h-4 w-4 text-aoa-primary focus:ring-aoa-primary border-gray-300 rounded"
        />
      )
    }

    if (param.type === 'number') {
      return (
        <input
          type="number"
          value={value}
          onChange={(e) => handleParameterChange(param.name, parseFloat(e.target.value) || 0)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-aoa-primary focus:border-transparent dark:bg-slate-700 dark:border-slate-600"
        />
      )
    }

    if (param.type === 'object' || param.type === 'array') {
      return (
        <textarea
          value={JSON.stringify(value, null, 2)}
          onChange={(e) => {
            try {
              handleParameterChange(param.name, JSON.parse(e.target.value))
            } catch {
              // Invalid JSON, keep as string
            }
          }}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-aoa-primary focus:border-transparent dark:bg-slate-700 dark:border-slate-600 font-mono text-sm"
          placeholder="Enter valid JSON"
        />
      )
    }

    return (
      <input
        type="text"
        value={value}
        onChange={(e) => handleParameterChange(param.name, e.target.value)}
        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-aoa-primary focus:border-transparent dark:bg-slate-700 dark:border-slate-600"
      />
    )
  }

  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-semibold mb-6">MCP Tool Tester</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Tool Selection */}
        <div>
          <h3 className="text-lg font-medium mb-3">Available Tools</h3>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {tools.map((tool) => (
              <motion.div
                key={`${tool.agent_id}-${tool.name}`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleToolSelect(tool)}
                className={`p-3 rounded-lg cursor-pointer transition-colors ${
                  selectedTool?.name === tool.name && selectedTool?.agent_id === tool.agent_id
                    ? 'bg-aoa-primary/10 border-2 border-aoa-primary'
                    : 'bg-gray-50 dark:bg-slate-700 hover:bg-gray-100 dark:hover:bg-slate-600'
                }`}
              >
                <div className="font-medium">{tool.name}</div>
                <div className="text-sm text-gray-600 dark:text-gray-300">{tool.description}</div>
                <div className="text-xs text-gray-500 mt-1">Agent: {tool.agent}</div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Tool Configuration and Execution */}
        <div>
          {selectedTool ? (
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Configure & Execute</h3>
              
              {/* Parameters */}
              <div className="space-y-3">
                {selectedTool.parameters.map((param) => (
                  <div key={param.name}>
                    <label className="block text-sm font-medium mb-1">
                      {param.name}
                      {param.required && <span className="text-red-500 ml-1">*</span>}
                    </label>
                    <p className="text-xs text-gray-500 mb-1">{param.description}</p>
                    {renderParameterInput(param)}
                  </div>
                ))}
              </div>

              {/* Examples */}
              {selectedTool.examples.length > 0 && (
                <div className="bg-gray-50 dark:bg-slate-700 rounded p-3">
                  <h4 className="text-sm font-medium mb-2">Examples</h4>
                  {selectedTool.examples.map((example, idx) => (
                    <div key={idx} className="text-xs text-gray-600 dark:text-gray-300 mb-1">
                      <button
                        onClick={() => setParameters(example.parameters || {})}
                        className="text-aoa-primary hover:underline"
                      >
                        {example.description || `Example ${idx + 1}`}
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {/* Execute Button */}
              <button
                onClick={executeTool}
                disabled={isExecuting}
                className="w-full px-4 py-2 bg-aoa-primary text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isExecuting ? 'Executing...' : 'Execute Tool'}
              </button>

              {/* Result/Error Display */}
              {error && (
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-red-800 dark:text-red-200 mb-1">Error</h4>
                  <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
                </div>
              )}

              {result && (
                <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-green-800 dark:text-green-200 mb-1">Result</h4>
                  <pre className="text-xs text-green-700 dark:text-green-300 overflow-x-auto">
                    {JSON.stringify(result, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              Select a tool to configure and execute
            </div>
          )}
        </div>
      </div>
    </div>
  )
}