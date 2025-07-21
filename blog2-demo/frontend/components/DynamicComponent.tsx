'use client'

import dynamic from 'next/dynamic'

// Dynamically import the chart component to avoid SSR issues
const ChartComponent = dynamic(() => import('./Charts'), { 
  ssr: false,
  loading: () => <div className="h-[400px] flex items-center justify-center">Loading chart...</div>
})

interface DynamicComponentProps {
  component?: {
    type: string
    data?: any
    agent?: string
    [key: string]: any
  }
  type?: string
  content?: any
  data?: any
  [key: string]: any
}

export default function DynamicComponent({ component, type, content, data, ...props }: DynamicComponentProps) {
  // Handle both new component format and legacy format
  const componentType = component?.type || type
  const componentData = component?.data || content || data
  const agentId = component?.agent || props.agent
  // This will be extended to dynamically load and render generated components
  // For now, it handles basic message types
  
  switch (componentType) {
    case 'message':
      return (
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <div className="text-blue-800 dark:text-blue-200">
            {typeof componentData === 'object' && componentData !== null ? (
              componentData.title ? (
                <div>
                  <h4 className="font-semibold mb-2">{componentData.title}</h4>
                  <div className="whitespace-pre-wrap">{componentData.content || JSON.stringify(componentData, null, 2)}</div>
                </div>
              ) : (
                <pre className="whitespace-pre-wrap text-sm">{JSON.stringify(componentData, null, 2)}</pre>
              )
            ) : (
              <p>{String(componentData)}</p>
            )}
          </div>
        </div>
      )
    
    case 'error':
      return (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-800 dark:text-red-200">{String(componentData)}</p>
        </div>
      )
    
    case 'agent_result':
    case 'agent-result':
      return (
        <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold mb-3 flex items-center">
            <span className="text-sm px-2 py-1 bg-gray-200 dark:bg-slate-700 rounded mr-2">
              {agentId || 'Agent'}
            </span>
            Result
          </h3>
          <div className="space-y-2">
            {/* Handle data tables specifically */}
            {componentData && componentData.data && Array.isArray(componentData.data) && componentData.columns ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-slate-700">
                    <tr>
                      {componentData.columns.slice(0, 6).map((col: string) => (
                        <th key={col} className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                          {col.replace(/_/g, ' ')}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-slate-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {componentData.data.slice(0, 5).map((row: any, idx: number) => (
                      <tr key={idx}>
                        {componentData.columns.slice(0, 6).map((col: string) => (
                          <td key={col} className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                            {typeof row[col] === 'number' ? row[col].toLocaleString() : String(row[col])}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
                <div className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                  Showing 5 of {componentData.data.length} rows, {Math.min(6, componentData.columns.length)} of {componentData.columns.length} columns
                </div>
              </div>
            ) : componentData && typeof componentData === 'object' ? (
              <div className="space-y-4">
                {/* Display insights if available */}
                {componentData.data_insights && Array.isArray(componentData.data_insights) && (
                  <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
                    <h4 className="font-medium text-green-800 dark:text-green-200 mb-2">Data Insights</h4>
                    <ul className="list-disc list-inside space-y-1">
                      {componentData.data_insights.map((insight: string, idx: number) => (
                        <li key={idx} className="text-green-700 dark:text-green-300">{insight}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {/* Display row count */}
                {componentData.row_count && (
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    <strong>Total Records:</strong> {componentData.row_count.toLocaleString()}
                  </div>
                )}
                
                {/* Fallback to JSON for other structured data */}
                <details className="mt-4">
                  <summary className="cursor-pointer text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200">
                    View Raw Data
                  </summary>
                  <pre className="mt-2 bg-gray-100 dark:bg-slate-900 p-4 rounded overflow-x-auto text-xs">
                    {JSON.stringify(componentData, null, 2)}
                  </pre>
                </details>
              </div>
            ) : (
              <p className="text-gray-600 dark:text-gray-300">{String(componentData || 'No data returned')}</p>
            )}
          </div>
        </div>
      )
    
    case 'data_table':
      // Render data table
      if (componentData && componentData.data && Array.isArray(componentData.data)) {
        const columns = componentData.columns || Object.keys(componentData.data[0] || {})
        return (
          <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6 overflow-x-auto">
            <h3 className="text-lg font-semibold mb-4">Data Table</h3>
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-slate-700">
                <tr>
                  {columns.map((col: string) => (
                    <th key={col} className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      {col.replace(/_/g, ' ')}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-slate-800 divide-y divide-gray-200 dark:divide-gray-700">
                {componentData.data.slice(0, 10).map((row: any, idx: number) => (
                  <tr key={idx}>
                    {columns.map((col: string) => (
                      <td key={col} className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                        {typeof row[col] === 'number' ? row[col].toLocaleString() : row[col]}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            {componentData.data.length > 10 && (
              <p className="mt-4 text-sm text-gray-500 dark:text-gray-400">
                Showing 10 of {componentData.data.length} rows
              </p>
            )}
          </div>
        )
      }
      return null
    
    case 'narrative':
      // Render narrative content
      if (componentData && componentData.result && componentData.result.content) {
        const narrativeContent = componentData.result.content
        return (
          <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Analysis Narrative</h3>
            <div className="prose dark:prose-invert max-w-none">
              {narrativeContent.summary && (
                <p className="text-gray-700 dark:text-gray-300 mb-4">
                  {typeof narrativeContent.summary === 'string' ? narrativeContent.summary : JSON.stringify(narrativeContent.summary)}
                </p>
              )}
              
              {narrativeContent.key_points && Array.isArray(narrativeContent.key_points) && narrativeContent.key_points.length > 0 && (
                <div>
                  <h4 className="text-md font-semibold mb-2">Key Points:</h4>
                  <ul className="list-disc pl-5 space-y-1">
                    {narrativeContent.key_points.map((point: any, idx: number) => (
                      <li key={idx} className="text-gray-600 dark:text-gray-400">
                        {typeof point === 'string' ? point : JSON.stringify(point)}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {narrativeContent.highlights && typeof narrativeContent.highlights === 'object' && (
                <div className="mt-4">
                  <h4 className="text-md font-semibold mb-2">Highlights:</h4>
                  <ul className="space-y-1">
                    {Object.entries(narrativeContent.highlights).map(([key, value], idx) => (
                      <li key={idx} className="text-gray-600 dark:text-gray-400">
                        <span className="font-medium">{key.replace(/_/g, ' ')}:</span> {String(value)}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {narrativeContent.context && (
                <div className="mt-4 p-4 bg-gray-50 dark:bg-slate-700 rounded">
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {typeof narrativeContent.context === 'string' ? narrativeContent.context : JSON.stringify(narrativeContent.context)}
                  </p>
                </div>
              )}
              
              {/* Handle any other nested objects */}
              {Object.entries(narrativeContent).map(([key, value]) => {
                if (!['summary', 'key_points', 'highlights', 'context'].includes(key) && value) {
                  return (
                    <div key={key} className="mt-4">
                      <h4 className="text-md font-semibold mb-2 capitalize">{key.replace(/_/g, ' ')}:</h4>
                      {typeof value === 'object' && !Array.isArray(value) ? (
                        <ul className="space-y-1">
                          {Object.entries(value).map(([subKey, subValue], idx) => (
                            <li key={idx} className="text-gray-600 dark:text-gray-400">
                              <span className="font-medium">{subKey.replace(/_/g, ' ')}:</span> {String(subValue)}
                            </li>
                          ))}
                        </ul>
                      ) : Array.isArray(value) ? (
                        <ul className="list-disc pl-5 space-y-1">
                          {value.map((item, idx) => (
                            <li key={idx} className="text-gray-600 dark:text-gray-400">
                              {typeof item === 'string' ? item : JSON.stringify(item)}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-gray-600 dark:text-gray-400">{String(value)}</p>
                      )}
                    </div>
                  )
                }
                return null
              })}
            </div>
          </div>
        )
      }
      return null
    
    case 'chart':
    case 'visualization':
      // Render visualization/chart content
      if (componentData) {
        // Handle both direct data and wrapped response format
        const vizData = componentData.result || componentData
        
        // Get the data from previous agent outputs (stored in props)
        const dataSource = props.previousData || componentData.previousData || null
        
        return (
          <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold mb-4">
              {vizData.type === 'dashboard' ? 'Data Visualizations' : 'Data Analysis'}
            </h3>
            
            {vizData.visualizations && vizData.visualizations.length > 0 ? (
              <div className="space-y-6">
                {vizData.visualizations.map((viz: any, idx: number) => (
                  <div key={idx} className="border border-gray-200 dark:border-gray-700 rounded p-4">
                    <h4 className="font-medium mb-4">{viz.title || `${viz.chart_type} Chart`}</h4>
                    <ChartComponent
                      type={viz.chart_type || 'bar'}
                      data={dataSource}
                      title={viz.title}
                      xAxis={viz.x_axis}
                      yAxis={viz.y_axis}
                    />
                  </div>
                ))}
              </div>
            ) : (
              <div className="border border-gray-200 dark:border-gray-700 rounded p-4">
                <ChartComponent
                  type={vizData.chart_type || 'bar'}
                  data={dataSource}
                  title={vizData.title || 'Renewable Energy Analysis'}
                />
              </div>
            )}
            
            {vizData.component_code && (
              <details className="mt-4">
                <summary className="cursor-pointer text-sm text-gray-600 dark:text-gray-400">
                  View generated code
                </summary>
                <pre className="mt-2 text-xs bg-gray-100 dark:bg-gray-900 p-2 rounded overflow-x-auto">
                  {vizData.component_code}
                </pre>
              </details>
            )}
          </div>
        )
      }
      return null
    
    case 'component':
      // This will dynamically load and render generated React components
      return (
        <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6">
          <p className="text-gray-500">Dynamic component loading will be implemented here</p>
        </div>
      )
    
    default:
      return (
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
          <p className="text-gray-600 dark:text-gray-300">Unknown component type: {componentType}</p>
          {componentData && (
            <pre className="mt-2 text-xs bg-gray-100 dark:bg-gray-900 p-2 rounded overflow-x-auto">
              {JSON.stringify(componentData, null, 2)}
            </pre>
          )}
        </div>
      )
  }
}