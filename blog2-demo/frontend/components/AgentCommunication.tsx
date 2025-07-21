'use client'

import { useEffect, useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface Message {
  id: string
  timestamp: string
  from_agent: string
  to_agent: string
  action: string
  status: 'sent' | 'processing' | 'completed' | 'error'
  payload?: any
  result?: any
}

export default function AgentCommunication() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    // Connect to WebSocket for real-time updates
    // Use the correct WebSocket URL for Docker environment
    const wsUrl = typeof window !== 'undefined' && window.location.hostname === 'localhost' 
      ? 'ws://localhost:8000/ws' 
      : `ws://${window.location.hostname}:8000/ws`
    const ws = new WebSocket(wsUrl)
    
    ws.onopen = () => {
      console.log('WebSocket connected to:', 'ws://localhost:8000/ws')
      setIsConnected(true)
      // Send a test message
      ws.send(JSON.stringify({ type: 'ping', timestamp: new Date().toISOString() }))
    }
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        if (data.type === 'agent_message') {
          const newMessage: Message = {
            id: data.id || `msg-${Date.now()}`,
            timestamp: new Date().toISOString(),
            from_agent: data.from_agent,
            to_agent: data.to_agent,
            action: data.action,
            status: data.status || 'sent',
            payload: data.payload,
            result: data.result
          }
          
          setMessages(prev => [...prev, newMessage])
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      console.error('Failed to connect to WebSocket at ws://localhost:8000/ws')
      setIsConnected(false)
    }
    
    ws.onclose = () => {
      console.log('WebSocket disconnected')
      setIsConnected(false)
    }
    
    wsRef.current = ws
    
    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close()
      }
    }
  }, [])

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const getAgentColor = (agent: string) => {
    const colors: { [key: string]: string } = {
      'gui-agent': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
      'data-agent': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      'viz-agent': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      'research-agent': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      'narrative-agent': 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200',
      'api': 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
    }
    
    for (const [key, color] of Object.entries(colors)) {
      if (agent.includes(key)) return color
    }
    return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'sent':
        return '📤'
      case 'processing':
        return '⏳'
      case 'completed':
        return '✅'
      case 'error':
        return '❌'
      default:
        return '📨'
    }
  }

  const clearMessages = () => {
    setMessages([])
  }

  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center space-x-3">
          <h3 className="text-xl font-semibold">Agent Communication</h3>
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-sm text-gray-500">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        <button
          onClick={clearMessages}
          className="text-sm px-3 py-1 bg-gray-200 dark:bg-slate-700 rounded hover:bg-gray-300 dark:hover:bg-slate-600 transition-colors"
        >
          Clear
        </button>
      </div>

      <div className="h-96 overflow-y-auto border dark:border-slate-700 rounded-lg p-4 space-y-2">
        <AnimatePresence>
          {messages.length === 0 ? (
            <div className="text-center text-gray-500 py-8">
              No messages yet. Submit a query to see agent communication.
            </div>
          ) : (
            messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="border dark:border-slate-700 rounded-lg p-3 text-sm"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getAgentColor(message.from_agent)}`}>
                        {message.from_agent}
                      </span>
                      <span className="text-gray-400">→</span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getAgentColor(message.to_agent)}`}>
                        {message.to_agent}
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-2 text-xs text-gray-600 dark:text-gray-400">
                      <span>{getStatusIcon(message.status)}</span>
                      <span className="font-medium">{message.action}</span>
                      <span>•</span>
                      <span>{new Date(message.timestamp).toLocaleTimeString()}</span>
                    </div>

                    {message.payload && (
                      <details className="mt-2">
                        <summary className="cursor-pointer text-xs text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
                          Payload
                        </summary>
                        <pre className="mt-1 text-xs bg-gray-100 dark:bg-slate-900 p-2 rounded overflow-x-auto">
                          {JSON.stringify(message.payload, null, 2)}
                        </pre>
                      </details>
                    )}

                    {message.result && message.status === 'completed' && (
                      <details className="mt-2">
                        <summary className="cursor-pointer text-xs text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
                          Result
                        </summary>
                        <pre className="mt-1 text-xs bg-gray-100 dark:bg-slate-900 p-2 rounded overflow-x-auto">
                          {JSON.stringify(message.result, null, 2)}
                        </pre>
                      </details>
                    )}
                  </div>
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>
    </div>
  )
}