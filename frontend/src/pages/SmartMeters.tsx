import React, { useState, useEffect } from 'react'
import { Row, Col, Card, Table, Tag, Button, Space, Statistic, Progress, Modal, Form, Input, Select, message } from 'antd'
import {
  ApiOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  CloseCircleOutlined
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'

const { Option } = Select

interface SmartMeter {
  id: string
  meter_id: string
  location: string
  meter_type: 'residential' | 'commercial' | 'industrial'
  is_active: boolean
  last_communication: string
  firmware_version: string
  signal_strength: number
  battery_level?: number
  total_energy: number
  current_power: number
  status: 'online' | 'offline' | 'maintenance'
}

const SmartMeters: React.FC = () => {
  const [meters, setMeters] = useState<SmartMeter[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingMeter, setEditingMeter] = useState<SmartMeter | null>(null)
  const [form] = Form.useForm()

  useEffect(() => {
    loadMeters()
  }, [])

  const loadMeters = async () => {
    setLoading(true)
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))

      const mockMeters: SmartMeter[] = [
        {
          id: '1',
          meter_id: 'SM001',
          location: 'Residential Area A - House 1',
          meter_type: 'residential',
          is_active: true,
          last_communication: '2024-05-15T10:30:00Z',
          firmware_version: '2.1.4',
          signal_strength: 85,
          battery_level: 92,
          total_energy: 1247.5,
          current_power: 3.2,
          status: 'online'
        },
        {
          id: '2',
          meter_id: 'SM002',
          location: 'Residential Area A - House 2',
          meter_type: 'residential',
          is_active: true,
          last_communication: '2024-05-15T10:28:00Z',
          firmware_version: '2.1.4',
          signal_strength: 78,
          battery_level: 88,
          total_energy: 892.3,
          current_power: 2.8,
          status: 'online'
        },
        {
          id: '3',
          meter_id: 'SM003',
          location: 'Commercial District - Office Building',
          meter_type: 'commercial',
          is_active: true,
          last_communication: '2024-05-15T10:31:00Z',
          firmware_version: '2.1.3',
          signal_strength: 92,
          total_energy: 5432.1,
          current_power: 15.7,
          status: 'online'
        },
        {
          id: '4',
          meter_id: 'SM004',
          location: 'Industrial Zone - Factory A',
          meter_type: 'industrial',
          is_active: false,
          last_communication: '2024-05-15T08:45:00Z',
          firmware_version: '2.0.8',
          signal_strength: 45,
          total_energy: 12890.7,
          current_power: 0,
          status: 'maintenance'
        },
        {
          id: '5',
          meter_id: 'SM005',
          location: 'Residential Area B - Apartment Complex',
          meter_type: 'residential',
          is_active: true,
          last_communication: '2024-05-15T10:29:00Z',
          firmware_version: '2.1.4',
          signal_strength: 67,
          battery_level: 76,
          total_energy: 3456.8,
          current_power: 8.9,
          status: 'online'
        }
      ]

      setMeters(mockMeters)
    } catch (error) {
      console.error('Error loading meters:', error)
      message.error('Failed to load smart meters')
    } finally {
      setLoading(false)
    }
  }

  const handleAddMeter = () => {
    setEditingMeter(null)
    form.resetFields()
    setModalVisible(true)
  }

  const handleEditMeter = (meter: SmartMeter) => {
    setEditingMeter(meter)
    form.setFieldsValue(meter)
    setModalVisible(true)
  }

  const handleDeleteMeter = (meterId: string) => {
    Modal.confirm({
      title: 'Delete Smart Meter',
      content: 'Are you sure you want to delete this smart meter?',
      okText: 'Delete',
      okType: 'danger',
      onOk: () => {
        setMeters(prev => prev.filter(meter => meter.id !== meterId))
        message.success('Smart meter deleted successfully')
      }
    })
  }

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields()

      if (editingMeter) {
        // Update existing meter
        setMeters(prev => prev.map(meter =>
          meter.id === editingMeter.id
            ? { ...meter, ...values }
            : meter
        ))
        message.success('Smart meter updated successfully')
      } else {
        // Add new meter
        const newMeter: SmartMeter = {
          id: Date.now().toString(),
          ...values,
          is_active: true,
          last_communication: new Date().toISOString(),
          firmware_version: '2.1.4',
          signal_strength: 85,
          battery_level: 100,
          total_energy: 0,
          current_power: 0,
          status: 'online'
        }
        setMeters(prev => [...prev, newMeter])
        message.success('Smart meter added successfully')
      }

      setModalVisible(false)
      form.resetFields()
    } catch (error) {
      console.error('Form validation failed:', error)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />
      case 'offline':
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
      case 'maintenance':
        return <ExclamationCircleOutlined style={{ color: '#faad14' }} />
      default:
        return null
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'success'
      case 'offline':
        return 'error'
      case 'maintenance':
        return 'warning'
      default:
        return 'default'
    }
  }

  const columns: ColumnsType<SmartMeter> = [
    {
      title: 'Meter ID',
      dataIndex: 'meter_id',
      key: 'meter_id',
      width: 100,
      render: (text: string) => <strong>{text}</strong>
    },
    {
      title: 'Location',
      dataIndex: 'location',
      key: 'location',
      width: 250
    },
    {
      title: 'Type',
      dataIndex: 'meter_type',
      key: 'meter_type',
      width: 120,
      render: (type: string) => (
        <Tag color={
          type === 'residential' ? 'blue' :
          type === 'commercial' ? 'green' : 'purple'
        }>
          {type.toUpperCase()}
        </Tag>
      )
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: string) => (
        <Tag icon={getStatusIcon(status)} color={getStatusColor(status)}>
          {status.toUpperCase()}
        </Tag>
      )
    },
    {
      title: 'Signal',
      dataIndex: 'signal_strength',
      key: 'signal_strength',
      width: 120,
      render: (strength: number) => (
        <Progress
          percent={strength}
          size="small"
          status={strength > 70 ? 'success' : strength > 40 ? 'normal' : 'exception'}
        />
      )
    },
    {
      title: 'Battery',
      dataIndex: 'battery_level',
      key: 'battery_level',
      width: 120,
      render: (level?: number) => level ? (
        <Progress
          percent={level}
          size="small"
          status={level > 20 ? 'success' : 'exception'}
        />
      ) : 'N/A'
    },
    {
      title: 'Current Power',
      dataIndex: 'current_power',
      key: 'current_power',
      width: 120,
      render: (power: number) => `${power.toFixed(1)} kW`
    },
    {
      title: 'Total Energy',
      dataIndex: 'total_energy',
      key: 'total_energy',
      width: 120,
      render: (energy: number) => `${energy.toFixed(1)} kWh`
    },
    {
      title: 'Last Communication',
      dataIndex: 'last_communication',
      key: 'last_communication',
      width: 180,
      render: (timestamp: string) => new Date(timestamp).toLocaleString()
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 120,
      render: (_, record: SmartMeter) => (
        <Space size="small">
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => handleEditMeter(record)}
            size="small"
          />
          <Button
            type="text"
            icon={<DeleteOutlined />}
            onClick={() => handleDeleteMeter(record.id)}
            danger
            size="small"
          />
        </Space>
      )
    }
  ]

  const calculateStats = () => {
    const total = meters.length
    const online = meters.filter(m => m.status === 'online').length
    const offline = meters.filter(m => m.status === 'offline').length
    const maintenance = meters.filter(m => m.status === 'maintenance').length
    const totalEnergy = meters.reduce((sum, m) => sum + m.total_energy, 0)
    const totalPower = meters.reduce((sum, m) => sum + m.current_power, 0)

    return { total, online, offline, maintenance, totalEnergy, totalPower }
  }

  const stats = calculateStats()

  return (
    <div className="fade-in page-transition">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1>Smart Meters Management</h1>
        <Space>
          <Button
            icon={<ReloadOutlined />}
            onClick={loadMeters}
            loading={loading}
          >
            Refresh
          </Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleAddMeter}
          >
            Add Meter
          </Button>
        </Space>
      </div>

      {/* Summary Statistics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Total Meters"
              value={stats.total}
              prefix={<ApiOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Online"
              value={stats.online}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Total Energy"
              value={stats.totalEnergy}
              precision={1}
              suffix="kWh"
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Current Power"
              value={stats.totalPower}
              precision={1}
              suffix="kW"
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Meters Table */}
      <Card title="Smart Meters" className="custom-table">
        <Table
          columns={columns}
          dataSource={meters}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `${range[0]}-${range[1]} of ${total} meters`
          }}
          scroll={{ x: 1200 }}
        />
      </Card>

      {/* Add/Edit Modal */}
      <Modal
        title={editingMeter ? 'Edit Smart Meter' : 'Add Smart Meter'}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={() => {
          setModalVisible(false)
          form.resetFields()
        }}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            meter_type: 'residential',
            status: 'online'
          }}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="meter_id"
                label="Meter ID"
                rules={[{ required: true, message: 'Please enter meter ID' }]}
              >
                <Input placeholder="e.g., SM006" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="meter_type"
                label="Meter Type"
                rules={[{ required: true, message: 'Please select meter type' }]}
              >
                <Select>
                  <Option value="residential">Residential</Option>
                  <Option value="commercial">Commercial</Option>
                  <Option value="industrial">Industrial</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="location"
            label="Location"
            rules={[{ required: true, message: 'Please enter location' }]}
          >
            <Input placeholder="e.g., Residential Area C - House 10" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="status"
                label="Status"
                rules={[{ required: true, message: 'Please select status' }]}
              >
                <Select>
                  <Option value="online">Online</Option>
                  <Option value="offline">Offline</Option>
                  <Option value="maintenance">Maintenance</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="signal_strength"
                label="Signal Strength (%)"
                rules={[{ required: true, message: 'Please enter signal strength' }]}
              >
                <Input type="number" min={0} max={100} placeholder="85" />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  )
}

export default SmartMeters
