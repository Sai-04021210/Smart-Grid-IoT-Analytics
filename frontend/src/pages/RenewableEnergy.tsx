import React from 'react'
import { Card, Typography } from 'antd'

const { Title } = Typography

const RenewableEnergy: React.FC = () => {
  return (
    <div className="fade-in">
      <Title level={1}>Renewable Energy</Title>
      <Card>
        <p>Solar and wind energy monitoring will be displayed here.</p>
      </Card>
    </div>
  )
}

export default RenewableEnergy
