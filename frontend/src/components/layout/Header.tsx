import React from 'react'
import { Layout, Space, Badge, Button, Dropdown, Avatar, Typography } from 'antd'
import {
  BellOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
  WifiOutlined,
  DisconnectOutlined
} from '@ant-design/icons'
import { useMQTT } from '../../contexts/MQTTContext'

const { Header: AntHeader } = Layout
const { Text } = Typography

const Header: React.FC = () => {
  const { isConnected } = useMQTT()

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
        console.log('Navigate to profile')
        break
      case 'settings':
        console.log('Navigate to settings')
        break
      case 'logout':
        console.log('Logout user')
        break
      default:
        break
    }
  }

  return (
    <AntHeader
      style={{
        padding: '0 24px',
        background: '#fff',
        boxShadow: '0 1px 4px rgba(0,21,41,.08)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginLeft: 200,
        position: 'sticky',
        top: 0,
        zIndex: 10,
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
        <Badge count={3} size="small">
          <Button
            type="text"
            icon={<BellOutlined />}
            style={{ border: 'none' }}
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
              <Text style={{ color: '#262626' }}>Admin</Text>
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
    </AntHeader>
  )
}

export default Header
