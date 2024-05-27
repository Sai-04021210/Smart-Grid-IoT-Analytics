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
  Space,
  Tag,
  Table,
  Divider
} from 'antd'
import {
  DollarOutlined,
  ThunderboltOutlined,
  ReloadOutlined,
  RiseOutlined,
  FallOutlined,
  ClockCircleOutlined,
  RocketOutlined
} from '@ant-design/icons'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title as ChartTitle,
  Tooltip,
  Legend
} from 'chart.js'
import {
  useCurrentPrice,
  usePriceForecast,
  usePricingTiers,
  useDynamicPricing,
  useOptimizePricing
} from '../hooks/usePricing'
import type { ColumnsType } from 'antd/es/table'

const { Title, Text } = Typography

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ChartTitle,
  Tooltip,
  Legend
)

const Pricing: React.FC = () => {
  const [meterType, setMeterType] = useState<string>('residential')
  const [forecastHours, setForecastHours] = useState<number>(24)

  // Fetch data
  const { data: currentPrice, isLoading: loadingPrice, refetch: refetchPrice } = useCurrentPrice(meterType)
  const { data: forecast, isLoading: loadingForecast, refetch: refetchForecast } = usePriceForecast({
    hours_ahead: forecastHours,
    meter_type: meterType
  })
  const { data: tiers, isLoading: loadingTiers } = usePricingTiers()
  const { data: dynamicPricing, isLoading: loadingDynamic, refetch: refetchDynamic } = useDynamicPricing({
    hours: 24
  })
  const { mutate: optimizePricing, isLoading: optimizing } = useOptimizePricing()

  const loading = loadingPrice || loadingForecast || loadingTiers || loadingDynamic

  // Handle refresh
  const handleRefresh = () => {
    refetchPrice()
    refetchForecast()
    refetchDynamic()
  }

  // Handle optimize
  const handleOptimize = () => {
    optimizePricing(undefined, {
      onSuccess: () => {
        handleRefresh()
      }
    })
  }

  // Prepare forecast chart data
  const forecastChartData = useMemo(() => {
    if (!forecast || forecast.length === 0) return null

    const sortedData = [...forecast].sort((a, b) =>
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    )

    return {
      labels: sortedData.map(d => {
        const date = new Date(d.timestamp)
        return date.toLocaleString('en-US', {
          month: 'short',
          day: 'numeric',
          hour: '2-digit'
        })
      }),
      datasets: [
        {
          label: 'Predicted Price ($/kWh)',
          data: sortedData.map(d => d.predicted_price),
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.4,
          fill: true
        }
      ]
    }
  }, [forecast])

  // Prepare dynamic pricing chart
  const dynamicPricingChartData = useMemo(() => {
    if (!dynamicPricing || dynamicPricing.length === 0) return null

    const sortedData = [...dynamicPricing].sort((a, b) =>
      new Date(a.target_timestamp).getTime() - new Date(b.target_timestamp).getTime()
    )

    return {
      labels: sortedData.map(d => {
        const date = new Date(d.target_timestamp)
        return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
      }),
      datasets: [
        {
          label: 'Optimized Price ($/kWh)',
          data: sortedData.map(d => d.optimized_price_kwh),
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          tension: 0.4
        }
      ]
    }
  }, [dynamicPricing])

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
          text: 'Price ($/kWh)'
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

  // Table columns for pricing tiers
  const tierColumns: ColumnsType<any> = [
    {
      title: 'Tier Name',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: any) => (
        <Space>
          <Tag color={record.name === tiers?.current_tier ? 'green' : 'default'}>
            {text.charAt(0).toUpperCase() + text.slice(1).replace('_', ' ')}
          </Tag>
          {record.name === tiers?.current_tier && <Text type="success">(Current)</Text>}
        </Space>
      )
    },
    {
      title: 'Price Multiplier',
      dataIndex: 'multiplier',
      key: 'multiplier',
      render: (value: number) => value ? `${value.toFixed(2)}x` : 'N/A'
    },
    {
      title: 'Time Range',
      dataIndex: 'hours',
      key: 'hours',
      render: (value: string) => value || 'All day'
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description'
    }
  ]

  // Get price change indicator
  const getPriceChangeIndicator = () => {
    if (!dynamicPricing || dynamicPricing.length < 2) return null

    const latest = dynamicPricing[0]
    const previous = dynamicPricing[1]
    const change = ((latest.optimized_price_kwh - previous.optimized_price_kwh) / previous.optimized_price_kwh) * 100

    return {
      value: Math.abs(change),
      isIncrease: change > 0
    }
  }

  const priceChange = getPriceChangeIndicator()

  return (
    <div className="fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={1}>Dynamic Pricing</Title>
        <Space>
          <Select
            value={meterType}
            onChange={setMeterType}
            style={{ width: 150 }}
          >
            <Select.Option value="residential">Residential</Select.Option>
            <Select.Option value="commercial">Commercial</Select.Option>
            <Select.Option value="industrial">Industrial</Select.Option>
          </Select>
          <Button
            icon={<ReloadOutlined />}
            onClick={handleRefresh}
            loading={loading}
          >
            Refresh
          </Button>
          <Button
            type="primary"
            icon={<RocketOutlined />}
            onClick={handleOptimize}
            loading={optimizing}
          >
            Optimize Pricing
          </Button>
        </Space>
      </div>

      {/* Current Price Card */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Current Price"
              value={currentPrice?.price_per_kwh || 0}
              precision={3}
              suffix="$/kWh"
              prefix={<DollarOutlined />}
              valueStyle={{ color: '#52c41a', fontSize: 32 }}
              loading={loadingPrice}
            />
            <div style={{ marginTop: 12 }}>
              {priceChange && (
                <Space>
                  {priceChange.isIncrease ? (
                    <Tag icon={<RiseOutlined />} color="error">
                      +{priceChange.value.toFixed(2)}%
                    </Tag>
                  ) : (
                    <Tag icon={<FallOutlined />} color="success">
                      -{priceChange.value.toFixed(2)}%
                    </Tag>
                  )}
                  <Text type="secondary">vs last update</Text>
                </Space>
              )}
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Pricing Tier"
              value={currentPrice?.pricing_tier || 'N/A'}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ fontSize: 24 }}
              loading={loadingPrice}
            />
            <div style={{ marginTop: 12 }}>
              <Text type="secondary">
                {meterType.charAt(0).toUpperCase() + meterType.slice(1)} Rate
              </Text>
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Peak Price"
              value={currentPrice?.peak_price || 0}
              precision={3}
              suffix="$/kWh"
              prefix={<ThunderboltOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
              loading={loadingPrice}
            />
            <div style={{ marginTop: 12 }}>
              <Text type="secondary">Peak hours (5PM-9PM)</Text>
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Off-Peak Price"
              value={currentPrice?.off_peak_price || 0}
              precision={3}
              suffix="$/kWh"
              prefix={<ThunderboltOutlined />}
              valueStyle={{ color: '#1890ff' }}
              loading={loadingPrice}
            />
            <div style={{ marginTop: 12 }}>
              <Text type="secondary">Off-peak (10PM-6AM)</Text>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Charts */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={12}>
          <Card
            title="Price Forecast"
            extra={
              <Select
                value={forecastHours}
                onChange={setForecastHours}
                style={{ width: 120 }}
                size="small"
              >
                <Select.Option value={12}>12 Hours</Select.Option>
                <Select.Option value={24}>24 Hours</Select.Option>
                <Select.Option value={48}>48 Hours</Select.Option>
                <Select.Option value={168}>1 Week</Select.Option>
              </Select>
            }
          >
            {loadingForecast ? (
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
                <Spin size="large" />
              </div>
            ) : forecastChartData ? (
              <div style={{ height: 300 }}>
                <Line data={forecastChartData} options={chartOptions} />
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
                <DollarOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />
                <Text type="secondary">No forecast data available</Text>
              </div>
            )}
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="Dynamic Pricing History (24h)">
            {loadingDynamic ? (
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
                <Spin size="large" />
              </div>
            ) : dynamicPricingChartData ? (
              <div style={{ height: 300 }}>
                <Line data={dynamicPricingChartData} options={chartOptions} />
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
                <DollarOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />
                <Text type="secondary">No dynamic pricing data available</Text>
              </div>
            )}
          </Card>
        </Col>
      </Row>

      {/* Pricing Tiers Table */}
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card title="Pricing Tiers">
            {loadingTiers ? (
              <div style={{ display: 'flex', justifyContent: 'center', padding: 40 }}>
                <Spin size="large" />
              </div>
            ) : tiers?.tiers ? (
              <Table
                columns={tierColumns}
                dataSource={Object.entries(tiers.tiers).map(([name, data]: [string, any]) => ({
                  name,
                  ...data
                }))}
                rowKey="name"
                pagination={false}
                size="middle"
              />
            ) : (
              <Alert
                message="No Pricing Tiers Available"
                description="Pricing tier information is not available at this time."
                type="info"
                showIcon
              />
            )}
          </Card>
        </Col>
      </Row>

      {/* Info Section */}
      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col span={24}>
          <Card title="About Dynamic Pricing">
            <Text>
              Dynamic pricing adjusts energy rates in real-time based on supply and demand, renewable energy availability,
              and grid conditions. This helps balance the grid and incentivizes energy consumption during off-peak hours.
            </Text>
            <Divider />
            <Row gutter={16}>
              <Col xs={24} sm={8}>
                <Text strong>Peak Hours (5PM-9PM)</Text>
                <br />
                <Text type="secondary">Highest rates when demand is maximum</Text>
              </Col>
              <Col xs={24} sm={8}>
                <Text strong>Standard Hours</Text>
                <br />
                <Text type="secondary">Normal rates during regular hours</Text>
              </Col>
              <Col xs={24} sm={8}>
                <Text strong>Off-Peak (10PM-6AM)</Text>
                <br />
                <Text type="secondary">Lowest rates to encourage night usage</Text>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Pricing
