import React, { useState, useMemo } from 'react'
import {
  Card,
  Typography,
  Row,
  Col,
  Statistic,
  Select,
  Button,
  Spin,
  Alert,
  Progress,
  Space,
  Tag
} from 'antd'
import {
  SunOutlined,
  ThunderboltOutlined,
  ReloadOutlined,
  RiseOutlined,
  CloudOutlined
} from '@ant-design/icons'
import { Line, Doughnut } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title as ChartTitle,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js'
import {
  useSolarGeneration,
  useWindGeneration,
  useRenewableSummary
} from '../hooks/useRenewable'

const { Title, Text } = Typography

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ChartTitle,
  Tooltip,
  Legend,
  ArcElement
)

const RenewableEnergy: React.FC = () => {
  const [selectedSource, setSelectedSource] = useState<string | undefined>(undefined)
  const [timeRange, setTimeRange] = useState<number>(24)

  // Fetch data
  const { data: solarData, isLoading: loadingSolar, refetch: refetchSolar } = useSolarGeneration({
    source_id: selectedSource,
    hours: timeRange
  })
  const { data: windData, isLoading: loadingWind, refetch: refetchWind } = useWindGeneration({
    source_id: selectedSource,
    hours: timeRange
  })
  const { data: summary, isLoading: loadingSummary, refetch: refetchSummary } = useRenewableSummary({
    hours: timeRange
  })

  const loading = loadingSolar || loadingWind || loadingSummary

  // Handle refresh
  const handleRefresh = () => {
    refetchSolar()
    refetchWind()
    refetchSummary()
  }

  // Prepare solar chart data
  const solarChartData = useMemo(() => {
    if (!solarData || solarData.length === 0) return null

    const sortedData = [...solarData].sort((a, b) =>
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    )

    return {
      labels: sortedData.map(d => {
        const date = new Date(d.timestamp)
        return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
      }),
      datasets: [
        {
          label: 'Solar Power (kW)',
          data: sortedData.map(d => d.power_output_kw),
          borderColor: 'rgb(255, 193, 7)',
          backgroundColor: 'rgba(255, 193, 7, 0.2)',
          tension: 0.4,
          fill: true
        }
      ]
    }
  }, [solarData])

  // Prepare wind chart data
  const windChartData = useMemo(() => {
    if (!windData || windData.length === 0) return null

    const sortedData = [...windData].sort((a, b) =>
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    )

    return {
      labels: sortedData.map(d => {
        const date = new Date(d.timestamp)
        return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
      }),
      datasets: [
        {
          label: 'Wind Power (kW)',
          data: sortedData.map(d => d.power_output_kw),
          borderColor: 'rgb(33, 150, 243)',
          backgroundColor: 'rgba(33, 150, 243, 0.2)',
          tension: 0.4,
          fill: true
        }
      ]
    }
  }, [windData])

  // Prepare renewable mix chart
  const renewableMixData = useMemo(() => {
    if (!summary) return null

    const solarEnergy = summary.solar?.total_energy_kwh || 0
    const windEnergy = summary.wind?.total_energy_kwh || 0
    const total = solarEnergy + windEnergy

    if (total === 0) return null

    return {
      labels: ['Solar', 'Wind'],
      datasets: [
        {
          data: [solarEnergy, windEnergy],
          backgroundColor: [
            'rgba(255, 193, 7, 0.8)',
            'rgba(33, 150, 243, 0.8)'
          ],
          borderColor: [
            'rgb(255, 193, 7)',
            'rgb(33, 150, 243)'
          ],
          borderWidth: 2
        }
      ]
    }
  }, [summary])

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Power Output (kW)'
        }
      },
      x: {
        title: {
          display: true,
          text: 'Time'
        }
      }
    }
  }

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
      title: {
        display: true,
        text: 'Renewable Energy Mix (kWh)'
      }
    }
  }

  return (
    <div className="fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={1}>Renewable Energy</Title>
        <Space>
          <Select
            value={timeRange}
            onChange={setTimeRange}
            style={{ width: 150 }}
          >
            <Select.Option value={6}>Last 6 Hours</Select.Option>
            <Select.Option value={12}>Last 12 Hours</Select.Option>
            <Select.Option value={24}>Last 24 Hours</Select.Option>
            <Select.Option value={48}>Last 48 Hours</Select.Option>
            <Select.Option value={168}>Last Week</Select.Option>
          </Select>
          <Button
            icon={<ReloadOutlined />}
            onClick={handleRefresh}
            loading={loading}
          >
            Refresh
          </Button>
        </Space>
      </div>

      {/* Summary Statistics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Solar Power"
              value={summary?.solar?.total_power_kw || 0}
              precision={2}
              suffix="kW"
              prefix={<SunOutlined />}
              valueStyle={{ color: '#faad14' }}
              loading={loadingSummary}
            />
            <div style={{ marginTop: 8 }}>
              <Text type="secondary">
                Active Panels: {summary?.solar?.active_panels || 0}
              </Text>
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Wind Power"
              value={summary?.wind?.total_power_kw || 0}
              precision={2}
              suffix="kW"
              prefix={<CloudOutlined />}
              valueStyle={{ color: '#1890ff' }}
              loading={loadingSummary}
            />
            <div style={{ marginTop: 8 }}>
              <Text type="secondary">
                Active Turbines: {summary?.wind?.active_turbines || 0}
              </Text>
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Renewable Energy"
              value={summary?.total_renewable_energy || 0}
              precision={2}
              suffix="kWh"
              prefix={<ThunderboltOutlined />}
              valueStyle={{ color: '#52c41a' }}
              loading={loadingSummary}
            />
            <div style={{ marginTop: 8 }}>
              <Text type="secondary">
                Last {timeRange} hours
              </Text>
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Solar Capacity Factor"
              value={(summary?.solar?.avg_capacity_factor || 0) * 100}
              precision={1}
              suffix="%"
              prefix={<RiseOutlined />}
              valueStyle={{ color: '#722ed1' }}
              loading={loadingSummary}
            />
            <div style={{ marginTop: 8 }}>
              <Progress
                percent={((summary?.solar?.avg_capacity_factor || 0) * 100)}
                size="small"
                showInfo={false}
                strokeColor="#faad14"
              />
            </div>
          </Card>
        </Col>
      </Row>

      {/* No Data Alert */}
      {!loading && !solarData?.length && !windData?.length && (
        <Alert
          message="No Renewable Energy Data"
          description="No solar or wind generation data available. Please ensure renewable energy sources are configured and data generator is running."
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      {/* Generation Charts */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="Solar Power Generation">
            {loadingSolar ? (
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
                <Spin size="large" />
              </div>
            ) : solarChartData ? (
              <div style={{ height: 300 }}>
                <Line data={solarChartData} options={chartOptions} />
              </div>
            ) : (
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                height: 300,
                gap: 16
              }}>
                <SunOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />
                <Text type="secondary">No solar generation data available</Text>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  Solar panels may be inactive or it's nighttime
                </Text>
              </div>
            )}
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="Wind Power Generation">
            {loadingWind ? (
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
                <Spin size="large" />
              </div>
            ) : windChartData ? (
              <div style={{ height: 300 }}>
                <Line data={windChartData} options={chartOptions} />
              </div>
            ) : (
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                height: 300,
                gap: 16
              }}>
                <CloudOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />
                <Text type="secondary">No wind generation data available</Text>
              </div>
            )}
          </Card>
        </Col>
      </Row>

      {/* Renewable Mix and Details */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={8}>
          <Card title="Renewable Energy Mix">
            {loadingSummary ? (
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
                <Spin size="large" />
              </div>
            ) : renewableMixData ? (
              <div style={{ height: 300 }}>
                <Doughnut data={renewableMixData} options={doughnutOptions} />
              </div>
            ) : (
              <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: 300
              }}>
                <Text type="secondary">No data available</Text>
              </div>
            )}
          </Card>
        </Col>

        <Col xs={24} lg={16}>
          <Card title="Performance Metrics">
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12}>
                <Card size="small" style={{ backgroundColor: '#fffbe6' }}>
                  <Statistic
                    title="Solar Energy Generated"
                    value={summary?.solar?.total_energy_kwh || 0}
                    precision={2}
                    suffix="kWh"
                    valueStyle={{ color: '#faad14' }}
                  />
                  <div style={{ marginTop: 12 }}>
                    <Text type="secondary">Peak Power: </Text>
                    <Text strong>{(summary?.solar?.peak_power_kw || 0).toFixed(2)} kW</Text>
                  </div>
                  <div style={{ marginTop: 4 }}>
                    <Text type="secondary">Avg Power: </Text>
                    <Text strong>{(summary?.solar?.average_power_kw || 0).toFixed(2)} kW</Text>
                  </div>
                </Card>
              </Col>

              <Col xs={24} sm={12}>
                <Card size="small" style={{ backgroundColor: '#e6f7ff' }}>
                  <Statistic
                    title="Wind Energy Generated"
                    value={summary?.wind?.total_energy_kwh || 0}
                    precision={2}
                    suffix="kWh"
                    valueStyle={{ color: '#1890ff' }}
                  />
                  <div style={{ marginTop: 12 }}>
                    <Text type="secondary">Peak Power: </Text>
                    <Text strong>{(summary?.wind?.peak_power_kw || 0).toFixed(2)} kW</Text>
                  </div>
                  <div style={{ marginTop: 4 }}>
                    <Text type="secondary">Avg Power: </Text>
                    <Text strong>{(summary?.wind?.average_power_kw || 0).toFixed(2)} kW</Text>
                  </div>
                </Card>
              </Col>

              <Col xs={24}>
                <Card size="small" style={{ backgroundColor: '#f6ffed' }}>
                  <Row gutter={16}>
                    <Col xs={12}>
                      <Statistic
                        title="Solar Capacity Factor"
                        value={(summary?.solar?.avg_capacity_factor || 0) * 100}
                        precision={1}
                        suffix="%"
                        valueStyle={{ fontSize: 20 }}
                      />
                    </Col>
                    <Col xs={12}>
                      <Statistic
                        title="Wind Capacity Factor"
                        value={(summary?.wind?.avg_capacity_factor || 0) * 100}
                        precision={1}
                        suffix="%"
                        valueStyle={{ fontSize: 20 }}
                      />
                    </Col>
                  </Row>
                </Card>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default RenewableEnergy
