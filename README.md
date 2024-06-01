# Smart Grid IoT Analytics Platform

A comprehensive IoT analytics platform for smart grid energy management, featuring real-time energy consumption prediction, smart meter data aggregation, dynamic pricing optimization, and renewable energy forecasting.

## 🌟 Features

- **Real-time Energy Consumption Prediction**: LSTM neural networks for accurate energy demand forecasting
- **Smart Meter Data Aggregation**: MQTT-based real-time data collection from IoT devices
- **Dynamic Pricing Optimization**: Advanced algorithms for optimal energy pricing strategies
- **Renewable Energy Forecasting**: Weather-integrated prediction models for solar and wind energy
- **Node-RED Dashboards**: Interactive visual dashboards for monitoring and control
- **RESTful API**: Comprehensive API for data access and system integration

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Smart Meters  │───▶│   MQTT Broker   │───▶│   Data Pipeline │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌─────────────────┐             ▼
│  Weather APIs   │───▶│   ML Models     │    ┌─────────────────┐
└─────────────────┘    │   (LSTM/RF)     │◀───│   PostgreSQL    │
                       └─────────────────┘    └─────────────────┘
                                │                       │
┌─────────────────┐             ▼                       ▼
│  Node-RED       │    ┌─────────────────┐    ┌─────────────────┐
│  Dashboards     │◀───│   FastAPI       │◀───│   Data Services │
└─────────────────┘    │   Backend       │    └─────────────────┘
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   React Web     │
                       │   Frontend      │
                       └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Git** (for cloning)
- **8GB+ RAM** (recommended for all services)
- **Available ports**: 3000, 8000, 1880, 1883, 5432, 6379, 9001

### System Requirements
- **Linux**: Ubuntu 20.04+, CentOS 8+, or similar
- **macOS**: 10.15+ with Docker Desktop
- **Windows**: Windows 10+ with Docker Desktop or WSL2

### Installation

**Simple two-command setup:**

1. **Clone the repository:**
```bash
git clone https://github.com/Sai-04021210/Smart-Grid-IoT-Analytics.git
cd Smart-Grid-IoT-Analytics
```

2. **Start all services:**
```bash
docker compose up -d
```

**Wait 2-3 minutes** for all services to build and start.

### Verify Installation
Check if all services are running:
```bash
docker compose ps
```

All services should show "Up" status.

### Access the Applications
- **Web Dashboard**: http://localhost:3000
- **Node-RED Dashboard**: http://localhost:1880
- **API Documentation**: http://localhost:8000/docs
- **MQTT Broker**: localhost:1883

### Stopping the Services
```bash
docker compose down
```

## 🔧 Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Check what's using the ports
sudo netstat -tulpn | grep :3000
sudo netstat -tulpn | grep :8000

# Kill processes or change ports in docker-compose.yml
```

**2. Docker Build Fails**
```bash
# Clean Docker cache and rebuild
docker system prune -a
docker compose build --no-cache
docker compose up -d
```

**3. Services Won't Start**
```bash
# Check logs for specific service
docker compose logs frontend
docker compose logs backend
docker compose logs postgres

# Restart specific service
docker compose restart frontend
```

**4. Permission Issues (Linux)**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Logout and login again
```

**5. Low Memory Issues**
```bash
# Check available memory
free -h
# Increase Docker memory limit in Docker Desktop settings
```

### Environment Variables
Create `.env` file for optional configurations:
```bash
# Optional: OpenWeather API key for weather data
OPENWEATHER_API_KEY=your_api_key_here
```

## 📊 Technology Stack

- **Backend**: FastAPI 0.110.x, Python 3.11
- **Frontend**: React 18.2.x, Vite 5.2.x
- **Machine Learning**: TensorFlow 2.16.x, scikit-learn 1.4.x
- **Database**: PostgreSQL 15, SQLAlchemy 2.0.x
- **Message Broker**: Eclipse Mosquitto MQTT
- **Visualization**: Node-RED, Plotly.js, Chart.js
- **Containerization**: Docker 26.x

## 📁 Project Structure

```
Smart-Grid-IoT-Analytics/
├── backend/                 # FastAPI backend services
├── frontend/               # React web application
├── ml-models/              # Machine learning models
├── mqtt-broker/            # MQTT broker configuration
├── node-red/              # Node-RED flows and dashboards
├── database/              # Database schemas and migrations
├── docs/                  # Documentation
├── deployment/            # Deployment configurations
└── docker-compose.yml     # Docker services orchestration
```

## 🤖 Machine Learning Models

### LSTM Energy Prediction
- **Purpose**: Predict energy consumption patterns
- **Input**: Historical consumption data, weather data, time features
- **Output**: Energy demand forecasts (1-24 hours ahead)

### Renewable Energy Forecasting
- **Purpose**: Predict solar and wind energy generation
- **Input**: Weather forecasts, historical generation data
- **Output**: Renewable energy production estimates

### Dynamic Pricing Optimization
- **Purpose**: Optimize energy pricing based on demand and supply
- **Input**: Demand forecasts, generation capacity, market conditions
- **Output**: Optimal pricing strategies

## 📈 API Endpoints

- `GET /api/v1/energy/consumption` - Get energy consumption data
- `GET /api/v1/energy/prediction` - Get energy demand predictions
- `GET /api/v1/pricing/current` - Get current energy prices
- `GET /api/v1/renewable/forecast` - Get renewable energy forecasts
- `POST /api/v1/meters/data` - Submit smart meter readings

## 🔧 Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Node-RED Setup
```bash
cd node-red
npm install
node-red
```

## 📚 Documentation

Detailed documentation is available in the `/docs` directory:
- [API Reference](docs/api.md)
- [ML Models Guide](docs/ml-models.md)
- [Deployment Guide](docs/deployment.md)
- [Node-RED Flows](docs/node-red.md)

## 🧪 Testing

```bash
# Backend tests
cd backend && python -m pytest

# Frontend tests
cd frontend && npm test

# Integration tests
docker-compose -f docker-compose.test.yml up
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support

For support and questions, please open an issue in the GitHub repository.

---

**Built with ❤️ for sustainable energy management**