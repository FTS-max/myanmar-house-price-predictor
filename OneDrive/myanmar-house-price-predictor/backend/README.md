# Myanmar House Price Predictor

A production-ready Python backend for predicting real estate prices in Myanmar using machine learning, AI enrichment, and FastAPI. Built with modern technologies and designed for seamless integration with Next.js frontends.

## 🚀 Features

- **Machine Learning Models**: Multiple ML algorithms (XGBoost, LightGBM, Random Forest, Gradient Boosting)
- **AI-Powered Enrichment**: OpenRouter integration for intelligent property analysis
- **REST API**: Comprehensive FastAPI endpoints with automatic documentation
- **Production Ready**: Structured logging, error handling, rate limiting, and monitoring
- **Modular Architecture**: Clean separation of concerns for maintainability
- **Batch Processing**: Support for bulk price predictions
- **Market Analysis**: AI-generated market insights and trends
- **Real-time Health Checks**: Service monitoring and diagnostics

## 🏗️ Architecture

```
myanmar-house-price-predictor/
├── app/
│   ├── api/
│   │   └── routes.py          # FastAPI routes and endpoints
│   ├── core/
│   │   ├── config.py          # Configuration management
│   │   ├── exceptions.py      # Custom exceptions and error handling
│   │   └── logging.py         # Structured logging setup
│   ├── models/
│   │   └── schemas.py         # Pydantic models and validation
│   └── services/
│       ├── ml_service.py      # Machine learning service
│       └── openrouter_service.py  # AI enrichment service
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── .env.example              # Environment configuration template
└── README.md                 # This file
```

## 🛠️ Technology Stack

- **Framework**: FastAPI 0.104.1
- **ML Libraries**: scikit-learn, XGBoost, LightGBM
- **AI Integration**: OpenRouter API with Claude 3 Haiku
- **Data Processing**: Pandas, NumPy
- **Validation**: Pydantic v2
- **Logging**: Loguru
- **HTTP Client**: httpx, aiohttp
- **Database**: SQLAlchemy with SQLite/PostgreSQL support

## 📋 Prerequisites

- Python 3.8+
- pip or conda
- OpenRouter API key (optional, for AI features)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd myanmar-house-price-predictor

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
# At minimum, set:
# - SECRET_KEY (generate a strong random key)
# - OPENROUTER_API_KEY (for AI features)
```

### 3. Run the Application

```bash
# Development mode
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📚 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Service health check |
| GET | `/api/v1/config` | API configuration |
| GET | `/api/v1/stats` | Usage statistics |

### Prediction Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/predict` | Single property price prediction |
| POST | `/api/v1/predict/batch` | Batch price predictions |
| POST | `/api/v1/market/analysis` | Market analysis for location |
| POST | `/api/v1/property/description` | AI-generated property description |

### Model Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/models/performance` | ML model performance metrics |

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|----------|
| `DEBUG` | Enable debug mode | `false` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `SECRET_KEY` | Application secret key | Required |
| `DATABASE_URL` | Database connection string | SQLite |
| `OPENROUTER_API_KEY` | OpenRouter API key | Optional |
| `ENABLE_AI_ENRICHMENT` | Enable AI features | `true` |
| `RATE_LIMIT_PER_MINUTE` | API rate limit | `60` |

### ML Model Configuration

- **Supported Models**: XGBoost, LightGBM, Random Forest, Gradient Boosting
- **Feature Engineering**: Automated feature creation and encoding
- **Model Persistence**: Automatic model saving and loading
- **Performance Monitoring**: Built-in metrics tracking

## 📊 Usage Examples

### Single Property Prediction

```python
import httpx

# Property data
property_data = {
    "property_type": "apartment",
    "condition": "good",
    "size_sqft": 1200,
    "location": {
        "city": "Yangon",
        "township": "Kamayut",
        "latitude": 16.8161,
        "longitude": 96.1392
    },
    "features": {
        "bedrooms": 3,
        "bathrooms": 2,
        "floors": 1,
        "parking_spaces": 1,
        "has_elevator": true,
        "has_security": true
    },
    "year_built": 2020,
    "enable_ai_enrichment": true
}

# Make prediction request
response = httpx.post(
    "http://localhost:8000/api/v1/predict",
    json=property_data
)

result = response.json()
print(f"Predicted Price: {result['predicted_price_mmk']:,.0f} MMK")
print(f"Confidence: {result['confidence_score']:.2%}")
```

### Market Analysis

```python
market_request = {
    "location": {
        "city": "Yangon",
        "township": "Downtown"
    },
    "property_type": "apartment",
    "time_period_months": 12
}

response = httpx.post(
    "http://localhost:8000/api/v1/market/analysis",
    json=market_request
)

analysis = response.json()
print(f"Average Price: {analysis['average_price_mmk']:,.0f} MMK")
```

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## 🚀 Production Deployment

### Docker Deployment

```dockerfile
# Dockerfile example
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Checklist

- [ ] Set `DEBUG=false`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure PostgreSQL database
- [ ] Set up Redis for caching
- [ ] Configure proper logging
- [ ] Set up monitoring and alerts
- [ ] Configure reverse proxy (nginx)
- [ ] Set up SSL certificates
- [ ] Configure backup strategy

## 🔗 Frontend Integration

This backend is designed for seamless integration with Next.js frontends:

```typescript
// Next.js API integration example
const predictPrice = async (propertyData: PropertyData) => {
  const response = await fetch('/api/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(propertyData)
  });
  
  return response.json();
};
```

## 📈 Monitoring and Observability

- **Health Checks**: `/health` endpoint for service monitoring
- **Metrics**: Built-in performance metrics and logging
- **Error Tracking**: Comprehensive error handling and reporting
- **Request Tracing**: Unique request IDs for debugging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:

- Check the API documentation at `/docs`
- Review the health check at `/health`
- Check logs for detailed error information
- Ensure all environment variables are properly configured

## 🔮 Roadmap

- [ ] Database integration for property storage
- [ ] User authentication and authorization
- [ ] Advanced caching with Redis
- [ ] Real-time price updates
- [ ] Property image analysis
- [ ] Mobile app API support
- [ ] Advanced analytics dashboard
- [ ] Multi-language support

---

**Built with ❤️ for Myanmar's real estate market**