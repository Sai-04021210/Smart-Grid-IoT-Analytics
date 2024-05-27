import React, { useState, useMemo } from 'react'
import { Row, Col, Card, Table, Tag, Button, Space, Statistic, Progress, Modal, Form, Input, Select, message, Alert } from 'antd'
import {
  ApiOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  CloseCircleOutlined,
  ThunderboltOutlined,
  EnvironmentOutlined
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { useMeters, useRegisterMeter, useMeterStats } from '../hooks/useMeters'
import type { SmartMeter } from '../types/meter'

const { Option } = Select

const SmartMeters: React.FC = () => {
  const [modalVisible, setModalVisible] = useState(false)
  const [editingMeter, setEditingMeter] = useState<SmartMeter | null>(null)
  const [filterType, setFilterType] = useState<string | undefined>(undefined)
  const [filterActive, setFilterActive] = useState<boolean | undefined>(undefined)
  const [form] = Form.useForm()

  // Fetch data with React Query
  const { data: meters, isLoading: loading, refetch } = useMeters({
    meter_type: filterType,
    is_active: filterActive
  })
  const { data: stats, isLoading: loadingStats } = useMeterStats()
  const { mutate: registerMeter, isLoading: registering } = useRegisterMeter()

  const handleAddMeter = () => {
    setEditingMeter(null)
    form.resetFields()
    setModalVisible(true)
  }

  const handleEditMeter = (meter: SmartMeter) => {
    setEditingMeter(meter)
    form.setFieldsValue({
      meter_id: meter.meter_id,
      location: meter.location,
      meter_type: meter.meter_type,
      latitude: meter.latitude,
      longitude: meter.longitude,
      firmware_version: meter.firmware_version
    })
    setModalVisible(true)
  }

  const handleDeleteMeter = (meterId: string) => {
    Modal.confirm({
      title: 'Delete Smart Meter',
      content: 'Are you sure you want to delete this smart meter? This action cannot be undone.',
      okText: 'Delete',
      okType: 'danger',
      onOk: () => {
        // TODO: Implement delete API call
        message.warning('Delete functionality not yet implemented in API')
      }
    })
  }

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields()

      if (editingMeter) {
        // TODO: Implement update API call
        message.warning('Update functionality not yet implemented in API')
        setModalVisible(false)
      } else {
        // Register new meter
        registerMeter(values, {
          onSuccess: () => {
            message.success('Smart meter registered successfully')
            setModalVisible(false)
            form.resetFields()
            refetch()
          },
          onError: (error: any) => {
            message.error(error.message || 'Failed to register smart meter')
          }
        })
      }
    } catch (error) {
      console.error('Form validation failed:', error)
    }
  }

  // Determine meter status based on last_communication
  const getMeterStatus = (meter: SmartMeter): 'online' | 'offline' | 'maintenance' => {
    if (!meter.is_active) return 'maintenance'
    if (!meter.last_communication) return 'offline'

    // Parse timestamp as UTC by adding 'Z' if not present
    const timestamp = meter.last_communication.endsWith('Z')
      ? meter.last_communication
      : meter.last_communication + 'Z'

    const lastComm = new Date(timestamp).getTime()
    const now = Date.now()
    const minutesSinceLastComm = (now - lastComm) / (1000 * 60)

    if (minutesSinceLastComm < 5) return 'online'
    if (minutesSinceLastComm < 30) return 'maintenance'
    return 'offline'
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

  // Enrich meters with status
  const enrichedMeters = useMemo(() => {
    if (!meters) return []
    return meters.map(meter => ({
      ...meter,
      status: getMeterStatus(meter)
    }))
  }, [meters])

  const columns: ColumnsType<any> = [
    {
      title: 'Meter ID',
      dataIndex: 'meter_id',
      key: 'meter_id',
      width: 100,
      fixed: 'left',
      render: (text: string) => <strong>{text}</strong>
    },
    {
      title: 'Location',
      dataIndex: 'location',
      key: 'location',
      width: 250,
      render: (text: string) => (
        <Space>
          <EnvironmentOutlined />
          {text}
        </Space>
      )
    },
    {
      title: 'Type',
      dataIndex: 'meter_type',
      key: 'meter_type',
      width: 120,
      filters: [
        { text: 'Residential', value: 'residential' },
        { text: 'Commercial', value: 'commercial' },
        { text: 'Industrial', value: 'industrial' }
      ],
      onFilter: (value: any, record: any) => record.meter_type === value,
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
      filters: [
        { text: 'Online', value: 'online' },
        { text: 'Offline', value: 'offline' },
        { text: 'Maintenance', value: 'maintenance' }
      ],
      onFilter: (value: any, record: any) => record.status === value,
      render: (status: string) => (
        <Tag icon={getStatusIcon(status)} color={getStatusColor(status)}>
          {status.toUpperCase()}
        </Tag>
      )
    },
    {
      title: 'Firmware',
      dataIndex: 'firmware_version',
      key: 'firmware_version',
      width: 100
    },
    {
      title: 'Last Communication',
      dataIndex: 'last_communication',
      key: 'last_communication',
      width: 180,
      sorter: (a: any, b: any) => {
        if (!a.last_communication) return 1
        if (!b.last_communication) return -1
        return new Date(a.last_communication).getTime() - new Date(b.last_communication).getTime()
      },
      render: (timestamp: string) => timestamp ? new Date(timestamp).toLocaleString() : 'Never'
    },
    {
      title: 'Active',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 80,
      filters: [
        { text: 'Active', value: true },
        { text: 'Inactive', value: false }
      ],
      onFilter: (value: any, record: any) => record.is_active === value,
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'success' : 'default'}>
          {isActive ? 'Yes' : 'No'}
        </Tag>
      )
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 120,
      fixed: 'right',
      render: (_, record: SmartMeter) => (
        <Space size="small">
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => handleEditMeter(record)}
            size="small"
            title="Edit meter"
          />
          <Button
            type="text"
            icon={<DeleteOutlined />}
            onClick={() => handleDeleteMeter(record.meter_id)}
            danger
            size="small"
            title="Delete meter"
          />
        </Space>
      )
    }
  ]

  const calculatedStats = useMemo(() => {
    if (!enrichedMeters || enrichedMeters.length === 0) {
      return { total: 0, online: 0, offline: 0, maintenance: 0 }
    }

    const total = enrichedMeters.length
    const online = enrichedMeters.filter(m => m.status === 'online').length
    const offline = enrichedMeters.filter(m => m.status === 'offline').length
    const maintenance = enrichedMeters.filter(m => m.status === 'maintenance').length

    return { total, online, offline, maintenance }
  }, [enrichedMeters])

  return (
    <div className="fade-in page-transition">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1>Smart Meters Management</h1>
        <Space>
          <Select
            placeholder="Filter by type"
            allowClear
            style={{ width: 150 }}
            onChange={setFilterType}
            value={filterType}
          >
            <Option value="residential">Residential</Option>
            <Option value="commercial">Commercial</Option>
            <Option value="industrial">Industrial</Option>
          </Select>
          <Select
            placeholder="Filter by status"
            allowClear
            style={{ width: 150 }}
            onChange={setFilterActive}
            value={filterActive}
          >
            <Option value={true}>Active</Option>
            <Option value={false}>Inactive</Option>
          </Select>
          <Button
            icon={<ReloadOutlined />}
            onClick={() => refetch()}
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
              value={stats?.total_meters || calculatedStats.total}
              prefix={<ApiOutlined />}
              valueStyle={{ color: '#1890ff' }}
              loading={loadingStats}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Online"
              value={calculatedStats.online}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
              loading={loading}
            />
            <div style={{ marginTop: 8, fontSize: 12, color: '#8c8c8c' }}>
              {calculatedStats.total > 0
                ? `${((calculatedStats.online / calculatedStats.total) * 100).toFixed(1)}% uptime`
                : 'N/A'}
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Total Energy"
              value={stats?.total_energy_kwh || 0}
              precision={1}
              suffix="kWh"
              prefix={<ThunderboltOutlined />}
              valueStyle={{ color: '#722ed1' }}
              loading={loadingStats}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Average Power"
              value={stats?.average_power_kw || 0}
              precision={2}
              suffix="kW"
              prefix={<ThunderboltOutlined />}
              valueStyle={{ color: '#faad14' }}
              loading={loadingStats}
            />
          </Card>
        </Col>
      </Row>

      {/* No Data Alert */}
      {!loading && (!enrichedMeters || enrichedMeters.length === 0) && (
        <Alert
          message="No Smart Meters Found"
          description="No smart meters are registered in the system. Click 'Add Meter' to register a new smart meter."
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      {/* Meters Table */}
      <Card title="Smart Meters" className="custom-table">
        <Table
          columns={columns}
          dataSource={enrichedMeters}
          rowKey="meter_id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `${range[0]}-${range[1]} of ${total} meters`
          }}
          scroll={{ x: 1400 }}
        />
      </Card>

      {/* Add/Edit Modal */}
      <Modal
        title={editingMeter ? 'Edit Smart Meter' : 'Register New Smart Meter'}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={() => {
          setModalVisible(false)
          form.resetFields()
        }}
        width={700}
        confirmLoading={registering}
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            meter_type: 'residential',
            firmware_version: 'v2.1.3'
          }}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="meter_id"
                label="Meter ID"
                rules={[
                  { required: true, message: 'Please enter meter ID' },
                  { pattern: /^[A-Z]{2}\d{3,}$/, message: 'Format: SM001, WT001, etc.' }
                ]}
              >
                <Input placeholder="e.g., SM006" disabled={!!editingMeter} />
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
                name="latitude"
                label="Latitude"
                rules={[
                  { required: true, message: 'Please enter latitude' },
                  {
                    validator: (_, value) => {
                      if (value >= -90 && value <= 90) {
                        return Promise.resolve()
                      }
                      return Promise.reject('Latitude must be between -90 and 90')
                    }
                  }
                ]}
              >
                <Input type="number" step="0.0001" placeholder="40.7128" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="longitude"
                label="Longitude"
                rules={[
                  { required: true, message: 'Please enter longitude' },
                  {
                    validator: (_, value) => {
                      if (value >= -180 && value <= 180) {
                        return Promise.resolve()
                      }
                      return Promise.reject('Longitude must be between -180 and 180')
                    }
                  }
                ]}
              >
                <Input type="number" step="0.0001" placeholder="-74.0060" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="firmware_version"
            label="Firmware Version"
            rules={[{ required: true, message: 'Please enter firmware version' }]}
          >
            <Input placeholder="v2.1.3" />
          </Form.Item>

          {editingMeter && (
            <Alert
              message="Note"
              description="Editing meter details is limited. Some fields cannot be modified after registration."
              type="info"
              showIcon
              style={{ marginTop: 16 }}
            />
          )}
        </Form>
      </Modal>
    </div>
  )
}

export default SmartMeters
