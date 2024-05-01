import React from 'react'
import { Card, Typography } from 'antd'

const { Title } = Typography

const SmartMeters: React.FC = () => {
  return (
    <div className="fade-in">
      <Title level={1}>Smart Meters</Title>
      <Card>
        <p>Smart meter management will be displayed here.</p>
      </Card>
    </div>
  )
}

export default SmartMeters
