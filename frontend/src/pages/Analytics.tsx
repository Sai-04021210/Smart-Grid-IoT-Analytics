import React from 'react'
import { Card, Typography } from 'antd'

const { Title } = Typography

const Analytics: React.FC = () => {
  return (
    <div className="fade-in">
      <Title level={1}>Analytics</Title>
      <Card>
        <p>Advanced analytics and reporting will be displayed here.</p>
      </Card>
    </div>
  )
}

export default Analytics
