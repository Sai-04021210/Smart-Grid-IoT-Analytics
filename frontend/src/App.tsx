import React, { useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from 'antd'
import Sidebar from './components/layout/Sidebar'
import Header from './components/layout/Header'
import Dashboard from './pages/Dashboard'
import EnergyMonitoring from './pages/EnergyMonitoring'
import Predictions from './pages/Predictions'
import RenewableEnergy from './pages/RenewableEnergy'
import Pricing from './pages/Pricing'
import SmartMeters from './pages/SmartMeters'
import Analytics from './pages/Analytics'
import Settings from './pages/Settings'
import Login from './pages/Login'
import ProtectedRoute from './components/ProtectedRoute'
import { MQTTProvider } from './contexts/MQTTContext'
import { AuthProvider } from './contexts/AuthContext'
import './App.css'

const { Content } = Layout

// Main layout component for authenticated pages
const MainLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <MQTTProvider>
      <Layout style={{ minHeight: '100vh' }}>
        <Sidebar collapsed={collapsed} onCollapse={setCollapsed} />
        <Layout style={{
          marginLeft: collapsed ? 80 : 200,
          minHeight: '100vh',
          transition: 'margin-left 0.2s'
        }}>
          <Header />
          <Content style={{
            padding: '16px',
            background: '#f0f2f5',
            minHeight: 'calc(100vh - 64px)',
            overflow: 'auto'
          }}>
            <div style={{
              background: '#fff',
              padding: '24px',
              borderRadius: '8px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
              minHeight: 'calc(100vh - 128px)'
            }}>
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/energy" element={<EnergyMonitoring />} />
                <Route path="/predictions" element={<Predictions />} />
                <Route path="/renewable" element={<RenewableEnergy />} />
                <Route path="/pricing" element={<Pricing />} />
                <Route path="/meters" element={<SmartMeters />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </div>
          </Content>
        </Layout>
      </Layout>
    </MQTTProvider>
  )
}

function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Public route */}
        <Route path="/login" element={<Login />} />

        {/* Protected routes */}
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        />
      </Routes>
    </AuthProvider>
  )
}

export default App
