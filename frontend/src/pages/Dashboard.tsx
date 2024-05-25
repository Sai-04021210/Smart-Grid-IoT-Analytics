import React, { useState, useEffect, useMemo } from 'react'
import { Row, Col, Card, Statistic, Progress, Alert, Spin, Button } from 'antd'
import {
  ThunderboltOutlined,
  SunOutlined,
  DollarOutlined,
  ApiOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  ReloadOutlined
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
import { useConsumptionSummary, useHourlyConsumption } from '../hooks/useEnergy'
import { useCurrentPrice } from '../hooks/usePricing'
import { useRenewableSummary } from '../hooks/useRenewable'
import { useMeters } from '../hooks/useMeters'

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
  const { isConnected, messages } = useMQTT()

  // Fetch data using custom hooks
  const { data: consumptionSummary, isLoading: loadingConsumption, refetch: refetchConsumption } = useConsumptionSummary()
  const { data: hourlyData, isLoading: loadingHourly, refetch: refetchHourly } = useHourlyConsumption({ hours: 24 })
  const { data: currentPrice, isLoading: loadingPrice, refetch: refetchPrice } = useCurrentPrice()
  const { data: renewableSummary, isLoading: loadingRenewable, refetch: refetchRenewable } = useRenewableSummary({ hours: 24 })
  const { data: meters, isLoading: loadingMeters, refetch: refetchMeters } = useMeters({ is_active: true })

  const loading = loadingConsumption || loadingHourly || loadingPrice || loadingRenewable || loadingMeters

  // Calculate metrics from API data
  const metrics = useMemo(() => {
    const totalConsumption = consumptionSummary?.total_consumption || 0
    const price = currentPrice?.price_per_kwh || 0
    const renewableGen = renewableSummary?.total_renewable_energy || 0
    const activeMeters = meters?.filter(m => m.is_active).length || 0

    return {
      totalConsumption,
      currentPrice: price,
      renewableGeneration: renewableGen,
      activeMeters,
      gridStatus: 'normal',
      consumptionChange: 0, // TODO: Calculate from historical data
      priceChange: 0, // TODO: Calculate from historical data
      renewableChange: renewableSummary?.renewable_percentage || 0
    }
  }, [consumptionSummary, currentPrice, renewableSummary, meters])

  // Prepare chart data from hourly consumption
  const energyData = useMemo(() => {
    if (!hourlyData || hourlyData.length === 0) {
      return null
    }

    // Sort by hour and take last 24 hours
    const sortedData = [...hourlyData].sort((a, b) =>
      new Date(a.hour).getTime() - new Date(b.hour).getTime()
    ).slice(-24)

    return {
      labels: sortedData.map(d => {
        const date = new Date(d.hour)
        return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
      }),
      datasets: [
        {
          label: 'Energy Consumption (kWh)',
          data: sortedData.map(d => d.total_consumption),
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.4
        }
      ]
    }
  }, [hourlyData])

  // Prepare renewable energy mix chart
  const renewableData = useMemo(() => {
    if (!renewableSummary) {
      return null
    }

    const solarEnergy = renewableSummary.solar?.total_energy_kwh || 0
    const windEnergy = renewableSummary.wind?.total_energy_kwh || 0
    const totalRenewable = solarEnergy + windEnergy
    const gridEnergy = Math.max(0, (consumptionSummary?.total_consumption || 0) - totalRenewable)

    const total = solarEnergy + windEnergy + gridEnergy

    if (total === 0) {
      return null
    }

    return {
      labels: ['Solar', 'Wind', 'Grid'],
      datasets: [
        {
          data: [
            ((solarEnergy / total) * 100).toFixed(1),
            ((windEnergy / total) * 100).toFixed(1),
            ((gridEnergy / total) * 100).toFixed(1)
          ],
          backgroundColor: [
            '#FFD700',
            '#87CEEB',
            '#FF6B6B'
          ],
          borderWidth: 2
        }
      ]
    }
  }, [renewableSummary, consumptionSummary])

  // Refresh all data
  const handleRefresh = () => {
    refetchConsumption()
    refetchHourly()
    refetchPrice()
    refetchRenewable()
    refetchMeters()
  }

  // Update data when MQTT messages arrive
  useEffect(() => {
    if (messages.length > 0) {
      const latestMessage = messages[0]

      // Refetch data when new readings arrive
      if (latestMessage.topic.includes('meters') ||
          latestMessage.topic.includes('solar') ||
          latestMessage.topic.includes('wind')) {
        // Debounce refetch to avoid too many requests
        const timer = setTimeout(() => {
          refetchConsumption()
          refetchRenewable()
        }, 2000)

        return () => clearTimeout(timer)
      }

      // Update price when pricing updates arrive
      if (latestMessage.topic.includes('pricing')) {
        refetchPrice()
      }
    }
  }, [messages, refetchConsumption, refetchRenewable, refetchPrice])

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
        height: '400px',
        flexDirection: 'column',
        gap: '16px'
      }}>
        <Spin size="large" />
        <div style={{ color: '#8c8c8c' }}>Loading dashboard data...</div>
      </div>
    )
  }

  // Show message if no data available
  const hasNoData = !consumptionSummary && !currentPrice && !renewableSummary && !meters

  return (
    <div className="fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1>Smart Grid Dashboard</h1>
        <Button
          icon={<ReloadOutlined />}
          onClick={handleRefresh}
          loading={loading}
        >
          Refresh
        </Button>
      </div>

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

      {/* No Data Alert */}
      {hasNoData && (
        <Alert
          message="No Data Available"
          description="No energy data found. Please ensure the data generator is running and meters are registered."
          type="info"
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
              prefix={<SunOutlined />}
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
          <Card title="Energy Consumption Trend (Last 24 Hours)" className="chart-container">
            {energyData ? (
              <Line data={energyData} options={chartOptions} />
            ) : (
              <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: 300,
                color: '#8c8c8c'
              }}>
                No consumption data available
              </div>
            )}
          </Card>
        </Col>

        <Col xs={24} lg={8}>
          <Card title="Energy Mix (%)" className="chart-container-small">
            {renewableData ? (
              <Doughnut data={renewableData} options={doughnutOptions} />
            ) : (
              <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: 300,
                color: '#8c8c8c'
              }}>
                No renewable data available
              </div>
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
