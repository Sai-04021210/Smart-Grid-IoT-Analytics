import React from 'react'
import { Card, Typography } from 'antd'

const { Title } = Typography

const Predictions: React.FC = () => {
  return (
    <div className="fade-in">
      <Title level={1}>Energy Predictions</Title>
      <Card>
        <p>LSTM-based energy consumption predictions will be displayed here.</p>
      </Card>
    </div>
  )
}

export default Predictions
