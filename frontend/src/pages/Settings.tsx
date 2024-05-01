import React from 'react'
import { Card, Typography } from 'antd'

const { Title } = Typography

const Settings: React.FC = () => {
  return (
    <div className="fade-in">
      <Title level={1}>Settings</Title>
      <Card>
        <p>Application settings and configuration will be displayed here.</p>
      </Card>
    </div>
  )
}

export default Settings
