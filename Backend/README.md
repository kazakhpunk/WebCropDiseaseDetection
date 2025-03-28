# FastAPI Cryptocurrency API Tracker

A FastAPI-based REST API that integrates with CoinGecko's API to fetch and manage cryptocurrency data. The application includes authentication, database operations, and external API integration.

## How to start

```bash
docker-compose up --build
```

## 🌐 Live Demo & Documentation

- **Live API**: [https://cryptocoinsprice.onrender.com](https://cryptocoinsprice.onrender.com)
- **API Documentation**:
  - Swagger UI: [https://cryptocoinsprice.onrender.com/docs](https://cryptocoinsprice.onrender.com/docs)
  - ReDoc: [https://cryptocoinsprice.onrender.com/redoc](https://cryptocoinsprice.onrender.com/redoc)

## 📚 Table of Contents

- [Architecture](#-architecture)
- [Authentication](#-authentication)
- [External API Integration](#-external-api-integration)
- [Local Operations](#-local-operations)
- [Database Models](#-database-models)
- [Schemas](#-schemas)

## 🏗 Architecture

The application is structured into several modules:

- Authentication service
- External API integration
- Local database operations
- CRUD operations
- Database models and schemas

## 🔐 Authentication

### Endpoints

```python
POST /auth/token
```

- Login endpoint that returns JWT access token
- Accepts email and password via OAuth2 form
- Returns: `{"access_token": string, "token_type": "bearer"}`

```python
POST /auth/register
```

- Register new user
- Accepts: `{"email": string, "password": string}`
- Returns: `{"access_token": string, "token_type": "bearer"}`

```python
GET /auth/me
```

- Get current authenticated user information
- Requires: Bearer token
- Returns: User object

## 🌐 External API Integration

### Endpoints

```python
GET /external/status
```

- Checks CoinGecko API status
- Returns: `{"status": "ok"}`

```python
GET /external/coins
```

- Retrieves list of all available coins from CoinGecko
- Returns: List of coin objects

```python
GET /external/price/{coin}
```

- Gets current price and market data for specific coin
- Protected endpoint (requires authentication)
- Automatically saves data to local database
- Returns: Price response object with market data

## 💾 Local Operations

### Endpoints

```python
GET /local/coins
```

- Retrieves all coins from local database
- Returns: List of stored coin objects

```python
GET /local/coin/{coin_name}
```

- Retrieves specific coin by name
- Returns: Single coin object

```python
POST /local/coin
```

- Creates new coin entry
- Protected endpoint
- Accepts: Coin object
- Returns: Created coin object

```python
PUT /local/coin/{coin_name}
```

- Updates entire coin entry
- Protected endpoint
- Accepts: Complete coin update object
- Returns: Updated coin object

```python
PATCH /local/coin/{coin_name}
```

- Partially updates coin entry
- Protected endpoint
- Accepts: Partial coin update object
- Returns: Updated coin object

```python
DELETE /local/coin/{coin_name}
```

- Deletes coin entry
- Protected endpoint
- Returns: Deleted coin object

## 📊 Database Models

### User

- `id`: Integer (Primary Key)
- `email`: String (Unique)
- `hashed_password`: String

### Coin

- `id`: Integer (Primary Key)
- `coin`: String
- `usd`: Float
- `usd_market_cap`: Float
- `usd_24h_vol`: Float
- `usd_24h_change`: Float
- `last_updated_at`: Integer

## 📝 Schemas

### CoinBase

Base schema for coin data validation

### CoinCreate

Schema for creating new coin entries

### CoinUpdate

Schema for updating existing coin entries

### PriceResponse

Schema for external API price responses

### Token

Schema for authentication tokens

### UserCredentials

Schema for user registration/login

## 🔧 CRUD Operations

### CoinCrud

- `create_coin(price_data)`: Creates new coin entry
- `get_coin(coin_id)`: Retrieves coin by ID
- `get_coin_by_name(coin_name)`: Retrieves coin by name
- `get_all_coins()`: Retrieves all coins
- `update_coin(coin_name, price_data)`: Updates entire coin entry
- `patch_coin(coin_name, price_data)`: Partially updates coin entry
- `delete_coin(coin_id)`: Deletes coin by ID
- `delete_coin_by_name(coin_name)`: Deletes coin by name

## 🔄 Dependencies

- FastAPI
- SQLAlchemy (Async)
- Pydantic
- httpx
- python-jose (JWT)
- passlib
- python-dotenv
