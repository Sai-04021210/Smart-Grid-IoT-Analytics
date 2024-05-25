import React, { useState, useMemo } from 'react'
import {
  Card,
  Typography,
  Row,
  Col,
  Select,
  Button,
  Statistic,
  Alert,
  Spin,
  Tag,
  Space,
  Divider
} from 'antd'
import {
  ThunderboltOutlined,
  RocketOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ReloadOutlined,
  LineChartOutlined
} from '@ant-design/icons'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title as ChartTitle,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import {
  useEnergyPredictions,
  useGeneratePredictions,
  usePredictionAccuracy,
  useModelStatus
} from '../hooks/usePredictions'
import { useMeters } from '../hooks/useMeters'
import { useEnergyConsumption } from '../hooks/useEnergy'

const { Title, Text } = Typography

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ChartTitle,
  Tooltip,
  Legend,
  Filler
)

const Predictions: React.FC = () => {
  const [selectedMeter, setSelectedMeter] = useState<string | undefined>(undefined)

  // Fetch data
  const { data: meters, isLoading: loadingMeters } = useMeters({ is_active: true })
  const { data: predictions, isLoading: loadingPredictions, refetch: refetchPredictions } = useEnergyPredictions({
    meter_id: selectedMeter,
    hours_ahead: 24
  })
  const { data: actualData, isLoading: loadingActual } = useEnergyConsumption({
    meter_id: selectedMeter,
    limit: 100
  })
  const { data: modelStatus, isLoading: loadingModel } = useModelStatus()
  const { data: accuracy, isLoading: loadingAccuracy } = usePredictionAccuracy({
    meter_id: selectedMeter,
    days: 7
  })
  const { mutate: generatePredictions, isLoading: generating } = useGeneratePredictions()

  const loading = loadingPredictions || loadingMeters || loadingModel

  // Handle generate predictions
  const handleGenerate = () => {
    generatePredictions(selectedMeter, {
      onSuccess: () => {
        refetchPredictions()
      }
    })
  }

  // Prepare chart data
  const chartData = useMemo(() => {
    if (!predictions || predictions.length === 0) {
      return null
    }

    // Sort predictions by target timestamp
    const sortedPredictions = [...predictions].sort((a, b) =>
      new Date(a.target_timestamp).getTime() - new Date(b.target_timestamp).getTime()
    )

    // Get actual data for comparison
    const actualMap = new Map()
    if (actualData) {
      actualData.forEach(reading => {
        const timestamp = new Date(reading.timestamp).toISOString()
        actualMap.set(timestamp, reading.active_energy)
      })
    }

    const labels = sortedPredictions.map(p => {
      const date = new Date(p.target_timestamp)
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    })

    const predictedValues = sortedPredictions.map(p => p.predicted_consumption)
    const upperBound = sortedPredictions.map(p => p.confidence_interval_upper || p.predicted_consumption * 1.1)
    const lowerBound = sortedPredictions.map(p => p.confidence_interval_lower || p.predicted_consumption * 0.9)

    // Match actual values with predictions
    const actualValues = sortedPredictions.map(p => {
      const timestamp = new Date(p.target_timestamp).toISOString()
      return actualMap.get(timestamp) || null
    })

    return {
      labels,
      datasets: [
        {
          label: 'Predicted Consumption',
          data: predictedValues,
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.1)',
          borderWidth: 2,
          tension: 0.4,
          pointRadius: 4,
          pointHoverRadius: 6
        },
        {
          label: 'Actual Consumption',
          data: actualValues,
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.1)',
          borderWidth: 2,
          tension: 0.4,
          pointRadius: 4,
          pointHoverRadius: 6,
          borderDash: [5, 5]
        },
        {
          label: 'Upper Confidence Bound',
          data: upperBound,
          borderColor: 'rgba(75, 192, 192, 0.3)',
          backgroundColor: 'rgba(75, 192, 192, 0.05)',
          borderWidth: 1,
          fill: '+1',
          tension: 0.4,
          pointRadius: 0
        },
        {
          label: 'Lower Confidence Bound',
          data: lowerBound,
          borderColor: 'rgba(75, 192, 192, 0.3)',
          backgroundColor: 'rgba(75, 192, 192, 0.05)',
          borderWidth: 1,
          fill: false,
          tension: 0.4,
          pointRadius: 0
        }
      ]
    }
  }, [predictions, actualData])

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Energy Consumption Predictions (24 Hours Ahead)'
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Energy Consumption (kWh)'
        }
      },
      x: {
        title: {
          display: true,
          text: 'Time'
        }
      }
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false
    }
  }

  return (
    <div className="fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={1}>Energy Predictions</Title>
        <Space>
          <Button
            icon={<ReloadOutlined />}
            onClick={() => refetchPredictions()}
            loading={loading}
          >
            Refresh
          </Button>
          <Button
            type="primary"
            icon={<RocketOutlined />}
            onClick={handleGenerate}
            loading={generating}
          >
            Generate Predictions
          </Button>
        </Space>
      </div>

      {/* Model Status */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <Card size="small">
            <Row gutter={16} align="middle">
              <Col>
                <Text strong>Model Status:</Text>
              </Col>
              <Col>
                {loadingModel ? (
                  <Spin size="small" />
                ) : modelStatus?.lstm_model?.loaded ? (
                  <Tag icon={<CheckCircleOutlined />} color="success">
                    LSTM Model Loaded
                  </Tag>
                ) : (
                  <Tag icon={<CloseCircleOutlined />} color="error">
                    Model Not Loaded
                  </Tag>
                )}
              </Col>
              {modelStatus?.lstm_model && (
                <>
                  <Col>
                    <Text type="secondary">
                      Version: {modelStatus.lstm_model.version}
                    </Text>
                  </Col>
                  <Col>
                    <Text type="secondary">
                      Sequence Length: {modelStatus.lstm_model.sequence_length}h
                    </Text>
                  </Col>
                  <Col>
                    <Text type="secondary">
                      Prediction Horizon: {modelStatus.lstm_model.prediction_horizon}h
                    </Text>
                  </Col>
                </>
              )}
            </Row>
          </Card>
        </Col>
      </Row>

      {/* Meter Selection and Accuracy Metrics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} md={8}>
          <Card>
            <Text strong>Select Smart Meter:</Text>
            <Select
              style={{ width: '100%', marginTop: 8 }}
              placeholder="All Meters"
              allowClear
              value={selectedMeter}
              onChange={setSelectedMeter}
              loading={loadingMeters}
            >
              {meters?.map(meter => (
                <Select.Option key={meter.meter_id} value={meter.meter_id}>
                  {meter.meter_id} - {meter.location}
                </Select.Option>
              ))}
            </Select>
          </Card>
        </Col>

        <Col xs={24} md={16}>
          <Card>
            <Row gutter={16}>
              <Col xs={12} sm={6}>
                <Statistic
                  title="Predictions"
                  value={predictions?.length || 0}
                  prefix={<LineChartOutlined />}
                  valueStyle={{ fontSize: 24 }}
                />
              </Col>
              <Col xs={12} sm={6}>
                <Statistic
                  title="Avg Accuracy"
                  value={accuracy?.average_accuracy || 0}
                  precision={1}
                  suffix="%"
                  valueStyle={{ fontSize: 24, color: '#52c41a' }}
                  loading={loadingAccuracy}
                />
              </Col>
              <Col xs={12} sm={6}>
                <Statistic
                  title="MAE"
                  value={accuracy?.mae || 0}
                  precision={2}
                  suffix="kWh"
                  valueStyle={{ fontSize: 24 }}
                  loading={loadingAccuracy}
                />
              </Col>
              <Col xs={12} sm={6}>
                <Statistic
                  title="RMSE"
                  value={accuracy?.rmse || 0}
                  precision={2}
                  suffix="kWh"
                  valueStyle={{ fontSize: 24 }}
                  loading={loadingAccuracy}
                />
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* No Model Warning */}
      {!loadingModel && !modelStatus?.lstm_model?.loaded && (
        <Alert
          message="ML Model Not Available"
          description="The LSTM prediction model is not loaded. Please train the model first or check the backend logs."
          type="warning"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      {/* Predictions Chart */}
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card title="Prediction vs Actual Consumption">
            {loading ? (
              <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: 400
              }}>
                <Spin size="large" />
              </div>
            ) : chartData ? (
              <div style={{ height: 400 }}>
                <Line data={chartData} options={chartOptions} />
              </div>
            ) : (
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                height: 400,
                gap: 16
              }}>
                <ThunderboltOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />
                <Text type="secondary">No predictions available</Text>
                <Button
                  type="primary"
                  icon={<RocketOutlined />}
                  onClick={handleGenerate}
                  loading={generating}
                >
                  Generate Predictions
                </Button>
              </div>
            )}
          </Card>
        </Col>
      </Row>

      {/* Accuracy Details */}
      {accuracy && accuracy.predictions_analyzed > 0 && (
        <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
          <Col span={24}>
            <Card title="Prediction Accuracy Details">
              <Row gutter={16}>
                <Col xs={24} sm={12}>
                  <Statistic
                    title="Analysis Period"
                    value={accuracy.analysis_period_days}
                    suffix="days"
                  />
                </Col>
                <Col xs={24} sm={12}>
                  <Statistic
                    title="Predictions Analyzed"
                    value={accuracy.predictions_analyzed}
                  />
                </Col>
              </Row>
              {accuracy.accuracy_by_meter && (
                <>
                  <Divider />
                  <Text strong>Accuracy by Meter:</Text>
                  <Row gutter={[8, 8]} style={{ marginTop: 12 }}>
                    {Object.entries(accuracy.accuracy_by_meter).map(([meterId, acc]) => (
                      <Col key={meterId} xs={24} sm={12} md={8}>
                        <Card size="small">
                          <Statistic
                            title={meterId}
                            value={acc as number}
                            precision={1}
                            suffix="%"
                            valueStyle={{ fontSize: 20 }}
                          />
                        </Card>
                      </Col>
                    ))}
                  </Row>
                </>
              )}
            </Card>
          </Col>
        </Row>
      )}
    </div>
  )
}

export default Predictions
