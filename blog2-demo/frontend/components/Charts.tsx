'use client'

import { Bar, Line, Pie, Doughnut } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions
} from 'chart.js'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
)

interface ChartComponentProps {
  type: string
  data: any
  title?: string
  xAxis?: string
  yAxis?: string
}

export default function ChartComponent({ type, data, title, xAxis, yAxis }: ChartComponentProps) {
  // Extract data from the renewable energy dataset
  const extractChartData = () => {
    // Check if we have actual data from the data agent
    if (data && typeof data === 'object' && data.data && Array.isArray(data.data)) {
      const dataset = data.data
      
      // For time series (line chart)
      if (type === 'line' || type === 'trend') {
        // Group by country and show trends over time
        const countries = [...new Set(dataset.map((d: any) => d.country))]
        const years = [...new Set(dataset.map((d: any) => d.year))].sort()
        
        return {
          labels: years,
          datasets: countries.slice(0, 5).map((country, idx) => ({
            label: country,
            data: years.map(year => {
              const entry = dataset.find((d: any) => d.country === country && d.year === year)
              return entry ? entry.total_renewable_mw : 0
            }),
            borderColor: `hsl(${idx * 60}, 70%, 50%)`,
            backgroundColor: `hsla(${idx * 60}, 70%, 50%, 0.1)`,
            tension: 0.1
          }))
        }
      }
      
      // For bar chart - show latest year comparison
      if (type === 'bar' || type === 'column') {
        const latestYear = Math.max(...dataset.map((d: any) => d.year))
        const latestData = dataset.filter((d: any) => d.year === latestYear)
        
        return {
          labels: latestData.map((d: any) => d.country),
          datasets: [{
            label: `Renewable Energy Capacity (${latestYear})`,
            data: latestData.map((d: any) => d.total_renewable_mw),
            backgroundColor: [
              'rgba(255, 99, 132, 0.5)',
              'rgba(54, 162, 235, 0.5)',
              'rgba(255, 206, 86, 0.5)',
              'rgba(75, 192, 192, 0.5)',
              'rgba(153, 102, 255, 0.5)',
            ],
            borderColor: [
              'rgba(255, 99, 132, 1)',
              'rgba(54, 162, 235, 1)',
              'rgba(255, 206, 86, 1)',
              'rgba(75, 192, 192, 1)',
              'rgba(153, 102, 255, 1)',
            ],
            borderWidth: 1
          }]
        }
      }
      
      // For pie chart - show distribution
      if (type === 'pie' || type === 'doughnut') {
        const latestYear = Math.max(...dataset.map((d: any) => d.year))
        const latestData = dataset.filter((d: any) => d.year === latestYear).slice(0, 5)
        
        return {
          labels: latestData.map((d: any) => d.country),
          datasets: [{
            label: 'Renewable Energy Share',
            data: latestData.map((d: any) => d.total_renewable_mw),
            backgroundColor: [
              'rgba(255, 99, 132, 0.5)',
              'rgba(54, 162, 235, 0.5)',
              'rgba(255, 206, 86, 0.5)',
              'rgba(75, 192, 192, 0.5)',
              'rgba(153, 102, 255, 0.5)',
            ],
            borderColor: [
              'rgba(255, 99, 132, 1)',
              'rgba(54, 162, 235, 1)',
              'rgba(255, 206, 86, 1)',
              'rgba(75, 192, 192, 1)',
              'rgba(153, 102, 255, 1)',
            ],
            borderWidth: 1
          }]
        }
      }
    }
    
    // Fallback demo data
    return {
      labels: ['United States', 'China', 'Germany', 'India', 'Japan'],
      datasets: [{
        label: title || 'Renewable Energy Capacity (MW)',
        data: [485800, 1525000, 173350, 215000, 159250],
        backgroundColor: [
          'rgba(255, 99, 132, 0.5)',
          'rgba(54, 162, 235, 0.5)',
          'rgba(255, 206, 86, 0.5)',
          'rgba(75, 192, 192, 0.5)',
          'rgba(153, 102, 255, 0.5)',
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
        ],
        borderWidth: 1
      }]
    }
  }

  const chartData = extractChartData()

  const options: ChartOptions<any> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: title || 'Renewable Energy Analysis',
      },
    },
    scales: type !== 'pie' && type !== 'doughnut' ? {
      x: {
        title: {
          display: !!xAxis,
          text: xAxis || 'Category'
        }
      },
      y: {
        title: {
          display: !!yAxis,
          text: yAxis || 'Value'
        },
        beginAtZero: true
      }
    } : undefined
  }

  // Render appropriate chart based on type
  const renderChart = () => {
    switch (type.toLowerCase()) {
      case 'line':
      case 'trend':
      case 'line_chart':
        return <Line data={chartData} options={options} />
      
      case 'bar':
      case 'column':
      case 'bar_chart':
        return <Bar data={chartData} options={options} />
      
      case 'pie':
      case 'pie_chart':
        return <Pie data={chartData} options={options} />
      
      case 'doughnut':
      case 'donut':
        return <Doughnut data={chartData} options={options} />
      
      case 'choropleth_map':
      case 'map':
        // For now, show a styled placeholder for maps
        return (
          <div className="flex items-center justify-center h-full bg-gradient-to-br from-blue-50 to-green-50 dark:from-blue-900/20 dark:to-green-900/20 rounded">
            <div className="text-center">
              <div className="text-4xl mb-2">🗺️</div>
              <p className="text-lg font-medium">World Map Visualization</p>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                Choropleth map showing renewable energy capacity by country
              </p>
              <div className="mt-4 grid grid-cols-5 gap-2 max-w-md mx-auto">
                {['🇺🇸', '🇨🇳', '🇩🇪', '🇮🇳', '🇯🇵'].map((flag, idx) => (
                  <div key={idx} className="text-2xl">{flag}</div>
                ))}
              </div>
            </div>
          </div>
        )
      
      default:
        return <Bar data={chartData} options={options} />
    }
  }

  return (
    <div className="w-full h-[400px]">
      {renderChart()}
    </div>
  )
}