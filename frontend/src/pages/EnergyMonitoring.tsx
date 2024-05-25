import React, { useState, useEffect, useMemo } from 'react'
import { Row, Col, Card, Table, Select, DatePicker, Button, Statistic, Tag, Spin } from 'antd'
import { Line } from 'react-chartjs-2'
import { ThunderboltOutlined, ApiOutlined, ReloadOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { useMeters } from '../hooks/useMeters'
import { useEnergyConsumption } from '../hooks/useEnergy'
import { EnergyReading } from '../types/energy'
import { SmartMeter } from '../types/meter'

const { RangePicker } = DatePicker
const { Option } = Select

const EnergyMonitoring: React.FC = () => {
  const [selectedMeter, setSelectedMeter] = useState<string | undefined>(undefined)
  const [chartData, setChartData] = useState<any>(null)

  // Fetch data using hooks
  const { data: meters, isLoading: loadingMeters, refetch: refetchMeters } = useMeters({ is_active: true })
  const { data: readings, isLoading: loadingReadings, refetch: refetchReadings } = useEnergyConsumption({
    meter_id: selectedMeter,
    limit: 100
  })

  const loading = loadingMeters || loadingReadings

  // Update chart when readings change
  useEffect(() => {
    if (readings && readings.length > 0) {
      updateChartData(readings)
    }
  }, [readings])

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
    if (!readings || readings.length === 0) return { totalEnergy: 0, avgPower: 0, maxPower: 0, activeMeters: 0 }

    const totalEnergy = readings.reduce((sum, reading) => sum + (reading.active_energy || 0), 0)
    const avgPower = readings.reduce((sum, reading) => sum + (reading.active_power || 0), 0) / readings.length
    const maxPower = Math.max(...readings.map(reading => reading.active_power || 0))
    const uniqueMeters = new Set(readings.map(reading => reading.meter_id)).size

    return {
      totalEnergy: totalEnergy.toFixed(1),
      avgPower: avgPower.toFixed(2),
      maxPower: maxPower.toFixed(2),
      activeMeters: uniqueMeters
    }
  }

  const stats = calculateSummaryStats()

  const handleRefresh = () => {
    refetchMeters()
    refetchReadings()
  }

  return (
    <div className="fade-in page-transition">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1>Energy Monitoring</h1>
        <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
          <Select
            value={selectedMeter}
            onChange={setSelectedMeter}
            style={{ width: 200 }}
            placeholder="All Meters"
            allowClear
            loading={loadingMeters}
          >
            {meters?.map(meter => (
              <Option key={meter.meter_id} value={meter.meter_id}>
                {meter.meter_id} - {meter.location}
              </Option>
            ))}
          </Select>
          <RangePicker showTime />
          <Button
            icon={<ReloadOutlined />}
            onClick={handleRefresh}
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
            {loading && !readings ? (
              <div style={{ display: 'flex', justifyContent: 'center', padding: 40 }}>
                <Spin size="large" />
              </div>
            ) : (
              <Table
                columns={columns}
                dataSource={readings || []}
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
                locale={{
                  emptyText: 'No energy readings available. Please ensure meters are active and data generator is running.'
                }}
              />
            )}
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default EnergyMonitoring
