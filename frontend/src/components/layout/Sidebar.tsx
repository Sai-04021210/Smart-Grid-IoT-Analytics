import React from 'react'
import { Layout, Menu } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  DashboardOutlined,
  ThunderboltOutlined,
  LineChartOutlined,
  SunOutlined,
  DollarOutlined,
  ApiOutlined,
  BarChartOutlined,
  SettingOutlined,
  HomeOutlined
} from '@ant-design/icons'

const { Sider } = Layout

const Sidebar: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: '/energy',
      icon: <ThunderboltOutlined />,
      label: 'Energy Monitoring',
    },
    {
      key: '/predictions',
      icon: <LineChartOutlined />,
      label: 'Predictions',
    },
    {
      key: '/renewable',
      icon: <SunOutlined />,
      label: 'Renewable Energy',
    },
    {
      key: '/pricing',
      icon: <DollarOutlined />,
      label: 'Dynamic Pricing',
    },
    {
      key: '/meters',
      icon: <ApiOutlined />,
      label: 'Smart Meters',
    },
    {
      key: '/analytics',
      icon: <BarChartOutlined />,
      label: 'Analytics',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: 'Settings',
    },
  ]

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key)
  }

  return (
    <Sider
      width={200}
      style={{
        overflow: 'auto',
        height: '100vh',
        position: 'fixed',
        left: 0,
        top: 0,
        bottom: 0,
        background: '#001529',
      }}
    >
      <div
        style={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: '#002140',
          borderBottom: '1px solid #1890ff',
        }}
      >
        <div style={{ color: '#fff', fontSize: '16px', fontWeight: 'bold' }}>
          <HomeOutlined style={{ marginRight: 8, color: '#1890ff' }} />
          Smart Grid
        </div>
      </div>

      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={[location.pathname]}
        items={menuItems}
        onClick={handleMenuClick}
        style={{
          borderRight: 0,
          background: '#001529',
        }}
      />
    </Sider>
  )
}

export default Sidebar
