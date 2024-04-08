import React, { useState, useEffect } from 'react'
import { Row, Col, Card, Statistic, Progress, Alert, Spin } from 'antd'
import {
  ThunderboltOutlined,
  SolarOutlined,
  DollarOutlined,
  ApiOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined
} from '@ant-design/icons'
import { Line, Doughnut } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js'
import { useMQTT } from '../contexts/MQTTContext'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
)

interface DashboardMetrics {
  totalConsumption: number
  currentPrice: number
  renewableGeneration: number
  activeMeters: number
  gridStatus: string
  consumptionChange: number
  priceChange: number
  renewableChange: number
}

const Dashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics>({
    totalConsumption: 0,
    currentPrice: 0,
    renewableGeneration: 0,
    activeMeters: 0,
    gridStatus: 'normal',
    consumptionChange: 0,
    priceChange: 0,
    renewableChange: 0
  })
  const [loading, setLoading] = useState(true)
  const [energyData, setEnergyData] = useState<any>(null)
  const [renewableData, setRenewableData] = useState<any>(null)
  
  const { isConnected, messages } = useMQTT()

  useEffect(() => {
    // Simulate loading dashboard data
    const loadDashboardData = async () => {
      try {
        // Simulate API calls
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // Mock data - in real app, fetch from API
        setMetrics({
          totalConsumption: 1247.5,
          currentPrice: 0.145,
          renewableGeneration: 324.8,
          activeMeters: 5,
          gridStatus: 'normal',
          consumptionChange: 5.2,
          priceChange: -2.1,
          renewableChange: 12.3
        })

        // Mock chart data
        setEnergyData({
          labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
          datasets: [
            {
              label: 'Energy Consumption (kWh)',
              data: [850, 720, 950, 1100, 1400, 1200],
              borderColor: 'rgb(75, 192, 192)',
              backgroundColor: 'rgba(75, 192, 192, 0.2)',
              tension: 0.4
            }
          ]
        })

        setRenewableData({
          labels: ['Solar', 'Wind', 'Grid'],
          datasets: [
            {
              data: [45, 25, 30],
              backgroundColor: [
                '#FFD700',
                '#87CEEB',
                '#FF6B6B'
              ],
              borderWidth: 2
            }
          ]
        })

        setLoading(false)
      } catch (error) {
        console.error('Error loading dashboard data:', error)
        setLoading(false)
      }
    }

    loadDashboardData()
  }, [])

  // Update metrics based on MQTT messages
  useEffect(() => {
    if (messages.length > 0) {
      const latestMessage = messages[0]
      
      if (latestMessage.topic.includes('meters') && latestMessage.topic.includes('data')) {
        // Update consumption metrics
        const consumption = latestMessage.payload.active_energy || 0
        setMetrics(prev => ({
          ...prev,
          totalConsumption: prev.totalConsumption + consumption
        }))
      }
    }
  }, [messages])

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Energy Consumption Trend'
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }

  const doughnutOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
      title: {
        display: true,
        text: 'Energy Mix (%)'
      }
    }
  }

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '400px' 
      }}>
        <Spin size="large" />
      </div>
    )
  }

  return (
    <div className="fade-in">
      <h1>Smart Grid Dashboard</h1>
      
      {/* Connection Status Alert */}
      {!isConnected && (
        <Alert
          message="MQTT Disconnected"
          description="Real-time data updates are not available. Please check your connection."
          type="warning"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      {/* Key Metrics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Consumption"
              value={metrics.totalConsumption}
              precision={1}
              suffix="kWh"
              prefix={<ThunderboltOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
            <div style={{ marginTop: 8 }}>
              {metrics.consumptionChange > 0 ? (
                <span style={{ color: '#cf1322' }}>
                  <ArrowUpOutlined /> {metrics.consumptionChange}%
                </span>
              ) : (
                <span style={{ color: '#3f8600' }}>
                  <ArrowDownOutlined /> {Math.abs(metrics.consumptionChange)}%
                </span>
              )}
              <span style={{ marginLeft: 8, color: '#8c8c8c' }}>vs last hour</span>
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Current Price"
              value={metrics.currentPrice}
              precision={3}
              suffix="$/kWh"
              prefix={<DollarOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
            <div style={{ marginTop: 8 }}>
              {metrics.priceChange > 0 ? (
                <span style={{ color: '#cf1322' }}>
                  <ArrowUpOutlined /> {metrics.priceChange}%
                </span>
              ) : (
                <span style={{ color: '#3f8600' }}>
                  <ArrowDownOutlined /> {Math.abs(metrics.priceChange)}%
                </span>
              )}
              <span style={{ marginLeft: 8, color: '#8c8c8c' }}>vs last hour</span>
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Renewable Generation"
              value={metrics.renewableGeneration}
              precision={1}
              suffix="kWh"
              prefix={<SolarOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
            <div style={{ marginTop: 8 }}>
              <span style={{ color: '#3f8600' }}>
                <ArrowUpOutlined /> {metrics.renewableChange}%
              </span>
              <span style={{ marginLeft: 8, color: '#8c8c8c' }}>vs last hour</span>
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Active Meters"
              value={metrics.activeMeters}
              prefix={<ApiOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
            <div style={{ marginTop: 8 }}>
              <Progress 
                percent={100} 
                size="small" 
                status="active"
                showInfo={false}
              />
              <span style={{ color: '#8c8c8c' }}>All systems operational</span>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Charts */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={16}>
          <Card title="Energy Consumption Trend" className="chart-container">
            {energyData && (
              <Line data={energyData} options={chartOptions} />
            )}
          </Card>
        </Col>

        <Col xs={24} lg={8}>
          <Card title="Energy Mix" className="chart-container-small">
            {renewableData && (
              <Doughnut data={renewableData} options={doughnutOptions} />
            )}
          </Card>
        </Col>
      </Row>

      {/* Grid Status */}
      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col span={24}>
          <Card title="Grid Status">
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={8}>
                <Statistic
                  title="Frequency"
                  value={50.02}
                  precision={2}
                  suffix="Hz"
                  valueStyle={{ 
                    color: Math.abs(50.02 - 50.0) < 0.1 ? '#3f8600' : '#cf1322' 
                  }}
                />
              </Col>
              <Col xs={24} sm={8}>
                <Statistic
                  title="Voltage Stability"
                  value={98.5}
                  precision={1}
                  suffix="%"
                  valueStyle={{ color: '#3f8600' }}
                />
              </Col>
              <Col xs={24} sm={8}>
                <Statistic
                  title="Load Factor"
                  value={85.2}
                  precision={1}
                  suffix="%"
                  valueStyle={{ color: '#1890ff' }}
                />
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* Recent MQTT Messages */}
      {isConnected && messages.length > 0 && (
        <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
          <Col span={24}>
            <Card title="Recent Data Updates" size="small">
              <div style={{ maxHeight: 200, overflowY: 'auto' }}>
                {messages.slice(0, 5).map((message, index) => (
                  <div key={index} style={{ 
                    padding: '8px 0', 
                    borderBottom: index < 4 ? '1px solid #f0f0f0' : 'none' 
                  }}>
                    <div style={{ fontSize: '12px', color: '#8c8c8c' }}>
                      {message.timestamp.toLocaleTimeString()} - {message.topic}
                    </div>
                    <div style={{ fontSize: '14px', marginTop: '4px' }}>
                      {message.topic.includes('meters') && 
                        `Energy: ${message.payload.active_energy || 0} kWh, Power: ${message.payload.active_power || 0} kW`
                      }
                      {message.topic.includes('solar') && 
                        `Solar: ${message.payload.power_output_kw || 0} kW`
                      }
                      {message.topic.includes('wind') && 
                        `Wind: ${message.payload.power_output_kw || 0} kW`
                      }
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </Col>
        </Row>
      )}
    </div>
  )
}

export default Dashboard
