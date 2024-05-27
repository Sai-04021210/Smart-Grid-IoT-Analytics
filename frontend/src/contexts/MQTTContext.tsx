import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import mqtt, { MqttClient } from 'mqtt'
import toast from 'react-hot-toast'

interface MQTTMessage {
  topic: string
  payload: any
  timestamp: Date
}

interface MQTTContextType {
  client: MqttClient | null
  isConnected: boolean
  messages: MQTTMessage[]
  subscribe: (topic: string) => void
  unsubscribe: (topic: string) => void
  publish: (topic: string, message: any) => void
  clearMessages: () => void
}

const MQTTContext = createContext<MQTTContextType | undefined>(undefined)

interface MQTTProviderProps {
  children: ReactNode
}

export const MQTTProvider: React.FC<MQTTProviderProps> = ({ children }) => {
  const [client, setClient] = useState<MqttClient | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [messages, setMessages] = useState<MQTTMessage[]>([])

  useEffect(() => {
    // MQTT broker URL - using WebSocket connection
    const brokerUrl = import.meta.env.VITE_MQTT_URL || 'ws://localhost:9001'

    let mqttClient: MqttClient | null = null

    try {
      // Create MQTT client
      mqttClient = mqtt.connect(brokerUrl, {
        clientId: `smartgrid_web_${Math.random().toString(16).substr(2, 8)}`,
        clean: true,
        connectTimeout: 4000,
        reconnectPeriod: 5000,
      })

      // Connection event handlers
      mqttClient.on('connect', () => {
        console.log('Connected to MQTT broker')
        setIsConnected(true)
        setClient(mqttClient)
        toast.success('Connected to MQTT broker')

        // Subscribe to default topics
        if (mqttClient) {
          mqttClient.subscribe('smartgrid/+/+/data')
          mqttClient.subscribe('smartgrid/grid/status')
          mqttClient.subscribe('smartgrid/pricing/update')
        }
      })

      mqttClient.on('disconnect', () => {
        console.log('Disconnected from MQTT broker')
        setIsConnected(false)
      })

      mqttClient.on('error', (error) => {
        console.error('MQTT connection error:', error)
        // Don't show error toast on initial connection failure
        setIsConnected(false)
      })
    } catch (error) {
      console.error('Failed to initialize MQTT client:', error)
    }

    mqttClient.on('message', (topic, payload) => {
      try {
        const message = JSON.parse(payload.toString())
        const newMessage: MQTTMessage = {
          topic,
          payload: message,
          timestamp: new Date()
        }
        
        setMessages(prev => {
          // Keep only last 100 messages
          const updated = [newMessage, ...prev].slice(0, 100)
          return updated
        })
        
        // Handle specific message types
        handleMessage(topic, message)
      } catch (error) {
        console.error('Error parsing MQTT message:', error)
      }
    })

    // Cleanup on unmount
    return () => {
      if (mqttClient) {
        mqttClient.end()
      }
    }
  }, [])

  const handleMessage = (topic: string, payload: any) => {
    // Handle different types of messages
    if (topic.includes('meters') && topic.includes('data')) {
      // Smart meter data
      console.log('Received meter data:', payload)
    } else if (topic.includes('solar') && topic.includes('data')) {
      // Solar panel data
      console.log('Received solar data:', payload)
    } else if (topic.includes('wind') && topic.includes('data')) {
      // Wind turbine data
      console.log('Received wind data:', payload)
    } else if (topic.includes('grid/status')) {
      // Grid status updates
      console.log('Received grid status:', payload)
      if (payload.alert) {
        toast.warning(`Grid Alert: ${payload.message}`)
      }
    } else if (topic.includes('pricing/update')) {
      // Pricing updates
      console.log('Received pricing update:', payload)
      toast.info('Energy pricing updated')
    }
  }

  const subscribe = (topic: string) => {
    if (client && isConnected) {
      client.subscribe(topic)
      console.log(`Subscribed to topic: ${topic}`)
    }
  }

  const unsubscribe = (topic: string) => {
    if (client && isConnected) {
      client.unsubscribe(topic)
      console.log(`Unsubscribed from topic: ${topic}`)
    }
  }

  const publish = (topic: string, message: any) => {
    if (client && isConnected) {
      client.publish(topic, JSON.stringify(message))
      console.log(`Published to topic ${topic}:`, message)
    }
  }

  const clearMessages = () => {
    setMessages([])
  }

  const value: MQTTContextType = {
    client,
    isConnected,
    messages,
    subscribe,
    unsubscribe,
    publish,
    clearMessages
  }

  return (
    <MQTTContext.Provider value={value}>
      {children}
    </MQTTContext.Provider>
  )
}

export const useMQTT = (): MQTTContextType => {
  const context = useContext(MQTTContext)
  if (context === undefined) {
    throw new Error('useMQTT must be used within a MQTTProvider')
  }
  return context
}
