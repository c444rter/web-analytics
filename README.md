# Shopify Analytics App

A comprehensive analytics dashboard for Shopify data with machine learning forecasting capabilities.

## Overview

This application provides a powerful analytics platform for Shopify store owners to process and visualize their order data. It features a FastAPI backend with PostgreSQL database, Redis for caching and task queuing, and a Next.js/React frontend for interactive dashboards.

Key features include:

- Efficient bulk data ingestion (processing ~13,000 records in under 30 seconds)
- Real-time progress tracking for file uploads
- Comprehensive analytics dashboard with customizable KPIs
- Machine learning-based sales forecasting
- Style-based product forecasting for future sales trends
- Historical upload management
- Secure user authentication

## Tech Stack

### Backend

- **FastAPI**: Modern, high-performance web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Alembic**: Database migration tool
- **PostgreSQL**: Relational database
- **Redis**: Caching and task queue management
- **RQ (Redis Queue)**: Background task processing
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing for forecasting algorithms

### Frontend

- **Next.js**: React framework with server-side rendering
- **React**: UI library
- **Material-UI**: Component library
- **TanStack Query**: Data fetching and state management
- **Recharts**: Charting library
- **Axios**: HTTP client

### Authentication

- **NextAuth.js**: Authentication for Next.js
- **JWT**: Token-based authentication

## Project Structure

```
├── backend/                # FastAPI backend
│   ├── api/                # API endpoints
│   │   ├── v1/             # API version 1
│   │   └── v2/             # API version 2
│   ├── core/               # Core functionality
│   ├── db/                 # Database models and schemas
│   ├── ml/                 # Machine learning models
│   ├── test_data/          # Test data files
│   ├── tests/              # Backend tests
│   └── uploads/            # Upload storage
├── docs/                   # Documentation
├── frontend/               # Next.js frontend
│   ├── app/                # Next.js app router
│   ├── components/         # React components
│   ├── hooks/              # Custom React hooks
│   ├── lib/                # Utility functions
│   ├── store/              # State management
│   └── styles/             # CSS styles
├── migrations/             # Database migrations
└── uploads/                # Uploaded files storage
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- Supabase account (for database and storage)
- Railway account (for backend hosting)
- Vercel account (for frontend hosting)

### Local Development Setup

1. Clone the repository:

   ```
   git clone https://github.com/c444rter/web-analytics.git
   cd web-analytics
   ```

2. Set up the backend:

   ```
   # Create a virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Set up environment variables
   cp backend/.env.supabase.example backend/.env
   # Edit backend/.env with your configuration
   ```

3. Set up the frontend:

   ```
   cd frontend
   npm install

   # Set up environment variables
   cp .env.local.supabase.example .env.local
   # Edit .env.local with your configuration
   ```

4. Set up the database:
   ```
   # Run migrations
   alembic upgrade head
   ```

### Running the Application Locally

1. Start the backend:

   ```
   uvicorn backend.main:app --reload
   ```

2. Start the worker for background tasks:

   ```
   python -m backend.worker
   ```

3. Start the frontend:

   ```
   cd frontend
   npm run dev
   ```

4. Access the application at http://localhost:3000

### Production Deployment

#### Supabase Setup (Database & Storage)

1. Create a Supabase project at https://supabase.com/
2. Create a storage bucket named "uploads" with appropriate permissions
3. Note your Supabase URL and anon key from Project Settings → API
4. For the database connection string, use the session pooler format for IPv4 compatibility:
   ```
   postgresql://postgres.tipdainlasfkkgwxoexm:[YOUR-PASSWORD]@aws-0-us-west-1.pooler.supabase.com:5432/postgres
   ```
   Note the format with project ID in the username and AWS region in the hostname.

#### Railway Setup (Backend)

1. Create a new project on Railway
2. Connect your GitHub repository
3. Configure the following environment variables:
   - `DATABASE_URL`: Your Supabase PostgreSQL connection string
   - `SECRET_KEY`: A secure random string
   - `NEXTAUTH_SECRET`: A secure random string
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_KEY`: Your Supabase anon key
   - `BUCKET_NAME`: "uploads"
4. Set the root directory to `/backend`
5. Set the start command to `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Deploy the API service
7. Add a second service for the worker with the start command `rq worker --with-scheduler`

#### Vercel Setup (Frontend)

1. Import your GitHub repository to Vercel
2. Set the root directory to `/frontend`
3. Configure the following environment variables:
   - `NEXT_PUBLIC_BACKEND_URL`: Your Railway API URL
   - `NEXTAUTH_SECRET`: Same value used in Railway
   - `NEXTAUTH_URL`: Your Vercel deployment URL
4. Deploy the frontend

## Security Notes

- Never commit `.env` files containing secrets to the repository
- Use the provided `.env.example` files as templates
- Ensure proper authentication is set up before deployment

## Documentation

For more detailed information, see the following documentation:

- [Software Requirements Specification](docs/SRS.md)
- [Software Development Plan](docs/SDP.md)
- [Software Design Description](docs/SDD.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Testing Guide](docs/TESTING.md)

## License

[MIT License](LICENSE)
