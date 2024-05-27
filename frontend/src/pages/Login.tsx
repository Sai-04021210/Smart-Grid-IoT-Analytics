/**
 * Login page component
 */

import React, { useState } from 'react'
import { Form, Input, Button, Card, Typography, Space, Alert } from 'antd'
import { UserOutlined, LockOutlined, ThunderboltOutlined } from '@ant-design/icons'
import { useAuth } from '../contexts/AuthContext'

const { Title, Text } = Typography

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { login } = useAuth()

  const onFinish = async (values: { username: string; password: string }) => {
    setError(null)
    setLoading(true)

    try {
      await login(values.username, values.password)
    } catch (err: any) {
      setError(err.message || 'Login failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '20px'
      }}
    >
      <Card
        style={{
          width: '100%',
          maxWidth: 450,
          boxShadow: '0 10px 40px rgba(0,0,0,0.2)',
          borderRadius: '12px'
        }}
      >
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* Logo and Title */}
          <div style={{ textAlign: 'center' }}>
            <ThunderboltOutlined
              style={{
                fontSize: '48px',
                color: '#1890ff',
                marginBottom: '16px'
              }}
            />
            <Title level={2} style={{ margin: 0 }}>
              Smart Grid IoT Analytics
            </Title>
            <Text type="secondary">Sign in to your account</Text>
          </div>

          {/* Error Alert */}
          {error && (
            <Alert
              message="Login Failed"
              description={error}
              type="error"
              showIcon
              closable
              onClose={() => setError(null)}
            />
          )}

          {/* Login Form */}
          <Form
            name="login"
            onFinish={onFinish}
            autoComplete="off"
            size="large"
            layout="vertical"
          >
            <Form.Item
              name="username"
              rules={[
                { required: true, message: 'Please enter your username' }
              ]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="Username"
                autoComplete="username"
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[
                { required: true, message: 'Please enter your password' }
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="Password"
                autoComplete="current-password"
              />
            </Form.Item>

            <Form.Item style={{ marginBottom: 0 }}>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                block
                style={{
                  height: '45px',
                  fontSize: '16px',
                  fontWeight: 500
                }}
              >
                {loading ? 'Signing in...' : 'Sign In'}
              </Button>
            </Form.Item>
          </Form>

          {/* Default Credentials Info */}
          <div
            style={{
              background: '#f0f2f5',
              padding: '12px',
              borderRadius: '8px',
              textAlign: 'center'
            }}
          >
            <Text type="secondary" style={{ fontSize: '12px' }}>
              Default credentials: <strong>admin</strong> / <strong>1234</strong>
            </Text>
          </div>
        </Space>
      </Card>
    </div>
  )
}

export default Login

