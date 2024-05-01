import React from 'react'
import { Card, Typography } from 'antd'

const { Title } = Typography

const Pricing: React.FC = () => {
  return (
    <div className="fade-in">
      <Title level={1}>Dynamic Pricing</Title>
      <Card>
        <p>Dynamic pricing optimization will be displayed here.</p>
      </Card>
    </div>
  )
}

export default Pricing
