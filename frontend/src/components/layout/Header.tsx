import React, { useState } from 'react'
import { Layout, Space, Badge, Button, Dropdown, Avatar, Typography, Modal, message, Tag } from 'antd'
import {
  BellOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
  WifiOutlined,
  DisconnectOutlined,
  CrownOutlined
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useMQTT } from '../../contexts/MQTTContext'
import { useAuth } from '../../contexts/AuthContext'

const { Header: AntHeader } = Layout
const { Text } = Typography

const Header: React.FC = () => {
  const navigate = useNavigate()
  const [notificationModalVisible, setNotificationModalVisible] = useState(false)
  const { user, logout } = useAuth()

  // Try to get MQTT context, but don't fail if it's not available
  let isConnected = false
  let messages: any[] = []
  try {
    const mqtt = useMQTT()
    isConnected = mqtt.isConnected
    messages = mqtt.messages
  } catch (error) {
    // MQTT context not available, use defaults
    console.log('MQTT context not available')
  }

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Profile',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Settings',
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      danger: true,
    },
  ]

  const handleUserMenuClick = ({ key }: { key: string }) => {
    switch (key) {
      case 'profile':
        message.info('Profile page coming soon!')
        break
      case 'settings':
        navigate('/settings')
        break
      case 'logout':
        Modal.confirm({
          title: 'Logout',
          content: 'Are you sure you want to logout?',
          okText: 'Logout',
          okType: 'danger',
          onOk: () => {
            logout()
          }
        })
        break
      default:
        break
    }
  }

  const handleNotificationClick = () => {
    setNotificationModalVisible(true)
  }

  // Get recent MQTT messages as notifications
  const recentNotifications = messages.slice(0, 10)

  return (
    <AntHeader
      style={{
        padding: '0 24px',
        background: '#fff',
        boxShadow: '0 1px 4px rgba(0,21,41,.08)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'sticky',
        top: 0,
        zIndex: 10,
        height: 64,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <Typography.Title level={4} style={{ margin: 0, color: '#262626' }}>
          IoT Analytics Platform
        </Typography.Title>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {isConnected ? (
            <>
              <WifiOutlined style={{ color: '#52c41a' }} />
              <Text type="success" style={{ fontSize: 12 }}>
                MQTT Connected
              </Text>
            </>
          ) : (
            <>
              <DisconnectOutlined style={{ color: '#ff4d4f' }} />
              <Text type="danger" style={{ fontSize: 12 }}>
                MQTT Disconnected
              </Text>
            </>
          )}
        </div>
      </div>

      <Space size="middle">
        {/* Real-time status indicators */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <div
              style={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                backgroundColor: '#52c41a',
                animation: 'pulse 2s infinite',
              }}
            />
            <Text style={{ fontSize: 12, color: '#8c8c8c' }}>
              System Online
            </Text>
          </div>
        </div>

        {/* Notifications */}
        <Badge count={recentNotifications.length} size="small">
          <Button
            type="text"
            icon={<BellOutlined />}
            style={{ border: 'none' }}
            onClick={handleNotificationClick}
          />
        </Badge>

        {/* User menu */}
        <Dropdown
          menu={{
            items: userMenuItems,
            onClick: handleUserMenuClick,
          }}
          placement="bottomRight"
          arrow
        >
          <Button type="text" style={{ border: 'none', padding: 0 }}>
            <Space>
              <Avatar
                size="small"
                icon={<UserOutlined />}
                style={{ backgroundColor: '#1890ff' }}
              />
              <div style={{ textAlign: 'left' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  <Text style={{ color: '#262626', fontWeight: 500 }}>
                    {user?.full_name || user?.username || 'User'}
                  </Text>
                  {user?.role === 'admin' && (
                    <Tag color="gold" icon={<CrownOutlined />} style={{ margin: 0, fontSize: 10 }}>
                      Admin
                    </Tag>
                  )}
                </div>
                <Text type="secondary" style={{ fontSize: 11 }}>
                  {user?.email}
                </Text>
              </div>
            </Space>
          </Button>
        </Dropdown>
      </Space>

      <style>
        {`
          @keyframes pulse {
            0% {
              box-shadow: 0 0 0 0 rgba(82, 196, 26, 0.7);
            }
            70% {
              box-shadow: 0 0 0 10px rgba(82, 196, 26, 0);
            }
            100% {
              box-shadow: 0 0 0 0 rgba(82, 196, 26, 0);
            }
          }
        `}
      </style>

      {/* Notifications Modal */}
      <Modal
        title="Recent Data Updates"
        open={notificationModalVisible}
        onCancel={() => setNotificationModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setNotificationModalVisible(false)}>
            Close
          </Button>
        ]}
        width={600}
      >
        {recentNotifications.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '20px', color: '#8c8c8c' }}>
            No recent notifications
          </div>
        ) : (
          <div style={{ maxHeight: 400, overflowY: 'auto' }}>
            {recentNotifications.map((notification, index) => (
              <div
                key={index}
                style={{
                  padding: '12px',
                  borderBottom: index < recentNotifications.length - 1 ? '1px solid #f0f0f0' : 'none',
                  marginBottom: 8
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                  <Text strong style={{ fontSize: 13 }}>
                    {notification.topic}
                  </Text>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {notification.timestamp.toLocaleTimeString()}
                  </Text>
                </div>
                <div style={{ fontSize: 12, color: '#595959' }}>
                  {notification.topic.includes('meters') && notification.payload.active_power && (
                    <>
                      <span>Power: {notification.payload.active_power.toFixed(2)} kW</span>
                      <span style={{ marginLeft: 16 }}>
                        Energy: {notification.payload.active_energy?.toFixed(2) || 0} kWh
                      </span>
                    </>
                  )}
                  {notification.topic.includes('solar') && notification.payload.power_output_kw !== undefined && (
                    <span>Solar: {notification.payload.power_output_kw.toFixed(2)} kW</span>
                  )}
                  {notification.topic.includes('wind') && notification.payload.power_output_kw !== undefined && (
                    <span>Wind: {notification.payload.power_output_kw.toFixed(2)} kW</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </Modal>
    </AntHeader>
  )
}

export default Header
