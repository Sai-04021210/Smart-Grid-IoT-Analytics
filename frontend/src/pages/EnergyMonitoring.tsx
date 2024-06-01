import React, { useState, useEffect } from 'react'
import { Row, Col, Card, Table, Select, DatePicker, Button, Statistic, Tag } from 'antd'
import { Line } from 'react-chartjs-2'
import { ThunderboltOutlined, ApiOutlined, ReloadOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'

const { RangePicker } = DatePicker
const { Option } = Select

interface EnergyReading {
  id: number
  meter_id: string
  timestamp: string
  active_energy: number
  active_power: number
  voltage_l1: number
  current_l1: number
  power_factor: number
  quality_flag: string
}

interface SmartMeter {
  meter_id: string
  location: string
  meter_type: string
  is_active: boolean
  last_communication: string
}

const EnergyMonitoring: React.FC = () => {
  const [readings, setReadings] = useState<EnergyReading[]>([])
  const [meters, setMeters] = useState<SmartMeter[]>([])
  const [selectedMeter, setSelectedMeter] = useState<string>('all')
  const [loading, setLoading] = useState(false)
  const [chartData, setChartData] = useState<any>(null)

  useEffect(() => {
    loadMeters()
    loadReadings()
  }, [])

  useEffect(() => {
    loadReadings()
  }, [selectedMeter])

  const loadMeters = async () => {
    try {
      // Simulate API call
      const mockMeters: SmartMeter[] = [
        {
          meter_id: 'SM001',
          location: 'Residential Area A - House 1',
          meter_type: 'residential',
          is_active: true,
          last_communication: '2024-04-01T10:00:00Z'
        },
        {
          meter_id: 'SM002',
          location: 'Residential Area A - House 2',
          meter_type: 'residential',
          is_active: true,
          last_communication: '2024-04-01T09:58:00Z'
        },
        {
          meter_id: 'SM003',
          location: 'Commercial District - Office Building',
          meter_type: 'commercial',
          is_active: true,
          last_communication: '2024-04-01T10:01:00Z'
        }
      ]
      setMeters(mockMeters)
    } catch (error) {
      console.error('Error loading meters:', error)
    }
  }

  const loadReadings = async () => {
    setLoading(true)
    try {
      // Simulate API call
      const mockReadings: EnergyReading[] = Array.from({ length: 20 }, (_, i) => ({
        id: i + 1,
        meter_id: selectedMeter === 'all' ? `SM00${(i % 3) + 1}` : selectedMeter,
        timestamp: new Date(Date.now() - i * 15 * 60 * 1000).toISOString(),
        active_energy: 125.5 + Math.random() * 50,
        active_power: 8.5 + Math.random() * 5,
        voltage_l1: 230 + Math.random() * 10 - 5,
        current_l1: 35 + Math.random() * 10,
        power_factor: 0.9 + Math.random() * 0.1,
        quality_flag: Math.random() > 0.1 ? 'good' : 'estimated'
      }))

      setReadings(mockReadings)
      updateChartData(mockReadings)
    } catch (error) {
      console.error('Error loading readings:', error)
    } finally {
      setLoading(false)
    }
  }

  const updateChartData = (data: EnergyReading[]) => {
    const sortedData = [...data].sort((a, b) =>
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    )

    setChartData({
      labels: sortedData.map(reading =>
        new Date(reading.timestamp).toLocaleTimeString()
      ),
      datasets: [
        {
          label: 'Active Power (kW)',
          data: sortedData.map(reading => reading.active_power),
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.4,
          yAxisID: 'y'
        },
        {
          label: 'Voltage L1 (V)',
          data: sortedData.map(reading => reading.voltage_l1),
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          tension: 0.4,
          yAxisID: 'y1'
        }
      ]
    })
  }

  const columns: ColumnsType<EnergyReading> = [
    {
      title: 'Meter ID',
      dataIndex: 'meter_id',
      key: 'meter_id',
      width: 100
    },
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 180,
      render: (timestamp: string) => new Date(timestamp).toLocaleString()
    },
    {
      title: 'Energy (kWh)',
      dataIndex: 'active_energy',
      key: 'active_energy',
      width: 120,
      render: (value: number) => value.toFixed(2)
    },
    {
      title: 'Power (kW)',
      dataIndex: 'active_power',
      key: 'active_power',
      width: 100,
      render: (value: number) => value.toFixed(2)
    },
    {
      title: 'Voltage (V)',
      dataIndex: 'voltage_l1',
      key: 'voltage_l1',
      width: 100,
      render: (value: number) => value.toFixed(1)
    },
    {
      title: 'Current (A)',
      dataIndex: 'current_l1',
      key: 'current_l1',
      width: 100,
      render: (value: number) => value.toFixed(1)
    },
    {
      title: 'Power Factor',
      dataIndex: 'power_factor',
      key: 'power_factor',
      width: 120,
      render: (value: number) => value.toFixed(3)
    },
    {
      title: 'Quality',
      dataIndex: 'quality_flag',
      key: 'quality_flag',
      width: 100,
      render: (flag: string) => (
        <Tag color={flag === 'good' ? 'green' : 'orange'}>
          {flag.toUpperCase()}
        </Tag>
      )
    }
  ]

  const chartOptions = {
    responsive: true,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      title: {
        display: true,
        text: 'Real-time Energy Monitoring'
      },
      legend: {
        position: 'top' as const,
      }
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: 'Time'
        }
      },
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        title: {
          display: true,
          text: 'Power (kW)'
        }
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        title: {
          display: true,
          text: 'Voltage (V)'
        },
        grid: {
          drawOnChartArea: false,
        },
      }
    }
  }

  const calculateSummaryStats = () => {
    if (readings.length === 0) return { totalEnergy: 0, avgPower: 0, maxPower: 0, activeMeters: 0 }

    const totalEnergy = readings.reduce((sum, reading) => sum + reading.active_energy, 0)
    const avgPower = readings.reduce((sum, reading) => sum + reading.active_power, 0) / readings.length
    const maxPower = Math.max(...readings.map(reading => reading.active_power))
    const uniqueMeters = new Set(readings.map(reading => reading.meter_id)).size

    return {
      totalEnergy: totalEnergy.toFixed(1),
      avgPower: avgPower.toFixed(2),
      maxPower: maxPower.toFixed(2),
      activeMeters: uniqueMeters
    }
  }

  const stats = calculateSummaryStats()

  return (
    <div className="fade-in page-transition">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1>Energy Monitoring</h1>
        <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
          <Select
            value={selectedMeter}
            onChange={setSelectedMeter}
            style={{ width: 200 }}
            placeholder="Select meter"
          >
            <Option value="all">All Meters</Option>
            {meters.map(meter => (
              <Option key={meter.meter_id} value={meter.meter_id}>
                {meter.meter_id} - {meter.meter_type}
              </Option>
            ))}
          </Select>
          <RangePicker showTime />
          <Button
            icon={<ReloadOutlined />}
            onClick={loadReadings}
            loading={loading}
          >
            Refresh
          </Button>
        </div>
      </div>

      {/* Summary Statistics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Total Energy"
              value={stats.totalEnergy}
              suffix="kWh"
              prefix={<ThunderboltOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Average Power"
              value={stats.avgPower}
              suffix="kW"
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Peak Power"
              value={stats.maxPower}
              suffix="kW"
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Active Meters"
              value={stats.activeMeters}
              prefix={<ApiOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Chart */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <Card title="Real-time Energy Data" className="chart-container">
            {chartData && (
              <Line data={chartData} options={chartOptions} />
            )}
          </Card>
        </Col>
      </Row>

      {/* Data Table */}
      <Row>
        <Col span={24}>
          <Card title="Energy Readings" className="custom-table">
            <Table
              columns={columns}
              dataSource={readings}
              rowKey="id"
              loading={loading}
              pagination={{
                pageSize: 10,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total, range) =>
                  `${range[0]}-${range[1]} of ${total} readings`
              }}
              scroll={{ x: 800 }}
            />
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default EnergyMonitoring
