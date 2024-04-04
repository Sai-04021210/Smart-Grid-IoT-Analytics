import React from 'react'
import { Routes, Route } from 'react-router-dom'
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
import { MQTTProvider } from './contexts/MQTTContext'
import './App.css'

const { Content } = Layout

function App() {
  return (
    <MQTTProvider>
      <Layout style={{ minHeight: '100vh' }}>
        <Sidebar />
        <Layout>
          <Header />
          <Content style={{ 
            margin: '16px',
            padding: '24px',
            background: '#fff',
            borderRadius: '8px',
            minHeight: 'calc(100vh - 112px)'
          }}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/energy" element={<EnergyMonitoring />} />
              <Route path="/predictions" element={<Predictions />} />
              <Route path="/renewable" element={<RenewableEnergy />} />
              <Route path="/pricing" element={<Pricing />} />
              <Route path="/meters" element={<SmartMeters />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </MQTTProvider>
  )
}

export default App
