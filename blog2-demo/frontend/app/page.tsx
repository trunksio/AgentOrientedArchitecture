'use client'

import { useState, useEffect } from 'react'
import GUIAgent from '@/components/GUIAgent'
import AgentStatus from '@/components/AgentStatus'
import RegistryBrowser from '@/components/RegistryBrowser'
import ToolTester from '@/components/ToolTester'
import AgentCommunication from '@/components/AgentCommunication'
import AgentConfiguration from '@/components/AgentConfiguration'
import LiveAgentManager from '@/components/LiveAgentManager'
import { motion, AnimatePresence } from 'framer-motion'

export default function Home() {
  const [isConnected, setIsConnected] = useState(false)
  const [agents, setAgents] = useState([])
  const [activeTab, setActiveTab] = useState<'demo' | 'system' | 'config'>('demo')
  const [systemSubTab, setSystemSubTab] = useState<'status' | 'registry' | 'tools' | 'messages'>('status')
  
  // Move generated components state here so it persists across tab switches
  const [generatedComponents, setGeneratedComponents] = useState<any[]>([])
  const [discoveredAgents, setDiscoveredAgents] = useState<any[]>([])
  const [currentQuery, setCurrentQuery] = useState('')

  useEffect(() => {
    // Check backend connection
    checkConnection()
    fetchAgents()
  }, [])

  const checkConnection = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/health`)
      const data = await response.json()
      setIsConnected(data.status === 'healthy')
    } catch (error) {
      setIsConnected(false)
    }
  }

  const fetchAgents = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/registry/agents`)
      const data = await response.json()
      setAgents(data)
    } catch (error) {
      console.error('Failed to fetch agents:', error)
    }
  }

  const tabStyles = (isActive: boolean) => `
    px-6 py-3 font-medium rounded-lg transition-all duration-200 
    ${isActive 
      ? 'bg-gradient-to-r from-aoa-primary to-aoa-accent text-white shadow-lg scale-105' 
      : 'bg-white dark:bg-slate-800 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700 shadow'
    }
  `

  const subTabStyles = (isActive: boolean) => `
    px-4 py-2 font-medium rounded-md transition-colors text-sm
    ${isActive 
      ? 'bg-aoa-primary/10 text-aoa-primary dark:bg-aoa-primary/20 dark:text-aoa-primary' 
      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
    }
  `

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="bg-white dark:bg-slate-800 shadow-sm border-b border-gray-200 dark:border-slate-700"
      >
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="text-center">
            <h1 className="text-5xl font-bold bg-gradient-to-r from-aoa-primary to-aoa-accent bg-clip-text text-transparent mb-2">
              Agent Oriented Architecture
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-300">
              Experience the future of AI collaboration
            </p>
          </div>

          {/* Main Navigation */}
          <div className="flex justify-center mt-8 space-x-4">
            <button
              onClick={() => setActiveTab('demo')}
              className={tabStyles(activeTab === 'demo')}
            >
              <span className="flex items-center space-x-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span>Demo</span>
                {generatedComponents.length > 0 && (
                  <span className="ml-2 px-2 py-1 text-xs bg-white/20 rounded-full">
                    {generatedComponents.length}
                  </span>
                )}
              </span>
            </button>
            <button
              onClick={() => setActiveTab('system')}
              className={tabStyles(activeTab === 'system')}
            >
              <span className="flex items-center space-x-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span>System Info</span>
              </span>
            </button>
            <button
              onClick={() => setActiveTab('config')}
              className={tabStyles(activeTab === 'config')}
            >
              <span className="flex items-center space-x-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <span>Configuration</span>
              </span>
            </button>
          </div>
        </div>
      </motion.div>

      {/* Content Area */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <AnimatePresence mode="wait">
          {/* Demo Tab */}
          {activeTab === 'demo' && (
            <motion.div
              key="demo"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
              className="max-w-4xl mx-auto"
            >
              <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8">
                <GUIAgent 
                  generatedComponents={generatedComponents}
                  setGeneratedComponents={setGeneratedComponents}
                  discoveredAgents={discoveredAgents}
                  setDiscoveredAgents={setDiscoveredAgents}
                  currentQuery={currentQuery}
                  setCurrentQuery={setCurrentQuery}
                />
              </div>
              
              {/* Connection Status */}
              <motion.div 
                className="mt-4 text-center"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
              >
                <div className={`inline-flex items-center space-x-2 text-sm ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
                  <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-600' : 'bg-red-600'} animate-pulse`} />
                  <span>{isConnected ? 'Connected to Backend' : 'Disconnected'}</span>
                </div>
              </motion.div>
            </motion.div>
          )}

          {/* System Tab */}
          {activeTab === 'system' && (
            <motion.div
              key="system"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              {/* Sub-navigation */}
              <div className="flex justify-center mb-6 space-x-2 bg-white dark:bg-slate-800 rounded-lg p-2 shadow">
                <button
                  onClick={() => setSystemSubTab('status')}
                  className={subTabStyles(systemSubTab === 'status')}
                >
                  Agent Status
                </button>
                <button
                  onClick={() => setSystemSubTab('registry')}
                  className={subTabStyles(systemSubTab === 'registry')}
                >
                  Registry Browser
                </button>
                <button
                  onClick={() => setSystemSubTab('tools')}
                  className={subTabStyles(systemSubTab === 'tools')}
                >
                  Tool Tester
                </button>
                <button
                  onClick={() => setSystemSubTab('messages')}
                  className={subTabStyles(systemSubTab === 'messages')}
                >
                  Agent Messages
                </button>
              </div>

              {/* Sub-tab content */}
              <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6">
                <AnimatePresence mode="wait">
                  {systemSubTab === 'status' && (
                    <motion.div key="status" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                      <AgentStatus agents={agents} isConnected={isConnected} onRefresh={fetchAgents} />
                    </motion.div>
                  )}
                  {systemSubTab === 'registry' && (
                    <motion.div key="registry" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                      <RegistryBrowser />
                    </motion.div>
                  )}
                  {systemSubTab === 'tools' && (
                    <motion.div key="tools" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                      <ToolTester />
                    </motion.div>
                  )}
                  {systemSubTab === 'messages' && (
                    <motion.div key="messages" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                      <AgentCommunication />
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>
          )}

          {/* Configuration Tab */}
          {activeTab === 'config' && (
            <motion.div
              key="config"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <AgentConfiguration />
                <LiveAgentManager 
                  onAgentAdded={(agent) => {
                    console.log('New agent added:', agent)
                    // Refresh agent list
                    fetchAgents()
                  }}
                />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </main>
  )
}