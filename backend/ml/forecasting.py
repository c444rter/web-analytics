# backend/ml/forecasting.py

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from db import models

class TimeSeriesForecaster:
    """
    A simple time series forecasting service that provides sales projections
    based on historical order data.
    """
    
    def __init__(self, db: Session, user_id: int, upload_id: int):
        """
        Initialize the forecaster with database session and filters.
        
        Args:
            db: SQLAlchemy database session
            user_id: User ID for filtering orders
            upload_id: Upload ID for filtering orders
        """
        self.db = db
        self.user_id = user_id
        self.upload_id = upload_id
        self.data = None
        self.prepared_data = None
    
    def load_data(self) -> pd.DataFrame:
        """
        Load order data from the database and convert to a time series.
        
        Returns:
            DataFrame with date index and order metrics
        """
        # Query orders for this user and upload
        orders = self.db.query(models.Order).filter(
            models.Order.user_id == self.user_id,
            models.Order.upload_id == self.upload_id
        ).all()
        
        # Convert to DataFrame
        data = []
        for order in orders:
            if order.created_at and order.total is not None:
                data.append({
                    'date': order.created_at.date(),
                    'total': float(order.total),
                    'order_id': order.id
                })
        
        # Create DataFrame and aggregate by date
        df = pd.DataFrame(data)
        if df.empty:
            return pd.DataFrame()
        
        # Group by date and calculate metrics
        daily_data = df.groupby('date').agg(
            order_count=('order_id', 'count'),
            revenue=('total', 'sum'),
            avg_order_value=('total', 'mean')
        ).reset_index()
        
        # Ensure continuous date range
        if not daily_data.empty:
            date_range = pd.date_range(
                start=daily_data['date'].min(),
                end=daily_data['date'].max(),
                freq='D'
            )
            
            # Reindex to include all dates
            daily_data = daily_data.set_index('date')
            daily_data = daily_data.reindex(date_range, fill_value=0)
            daily_data = daily_data.reset_index()
            daily_data = daily_data.rename(columns={'index': 'date'})
        
        self.data = daily_data
        return daily_data
    
    def prepare_data(self) -> pd.DataFrame:
        """
        Prepare data for forecasting by handling missing values,
        adding features, etc.
        
        Returns:
            Prepared DataFrame
        """
        if self.data is None:
            self.load_data()
        
        if self.data.empty:
            return pd.DataFrame()
        
        # Copy data to avoid modifying original
        df = self.data.copy()
        
        # Add time-based features
        df['day_of_week'] = pd.to_datetime(df['date']).dt.dayofweek
        df['month'] = pd.to_datetime(df['date']).dt.month
        df['year'] = pd.to_datetime(df['date']).dt.year
        
        # Add rolling averages
        df['revenue_7d_avg'] = df['revenue'].rolling(window=7, min_periods=1).mean()
        df['order_count_7d_avg'] = df['order_count'].rolling(window=7, min_periods=1).mean()
        
        # Handle any remaining NaN values
        df = df.fillna(0)
        
        self.prepared_data = df
        return df
    
    def forecast_naive(self, days: int = 30) -> Dict[str, Any]:
        """
        Generate a simple naive forecast based on historical averages.
        This is a placeholder for more sophisticated models.
        
        Args:
            days: Number of days to forecast
            
        Returns:
            Dictionary with forecast results
        """
        if self.prepared_data is None:
            self.prepare_data()
        
        if self.prepared_data.empty:
            return {
                "error": "Insufficient data for forecasting",
                "forecast": []
            }
        
        df = self.prepared_data
        
        # Calculate averages by day of week
        dow_avg = df.groupby('day_of_week').agg({
            'revenue': 'mean',
            'order_count': 'mean'
        })
        
        # Get the last date in the dataset
        last_date = df['date'].max()
        
        # Generate forecast dates
        forecast_dates = [last_date + timedelta(days=i+1) for i in range(days)]
        
        # Generate forecast values
        forecast = []
        for date in forecast_dates:
            # Get day of week (0=Monday, 6=Sunday)
            dow = date.weekday()
            
            # Get average values for this day of week
            if dow in dow_avg.index:
                avg_revenue = dow_avg.loc[dow, 'revenue']
                avg_orders = dow_avg.loc[dow, 'order_count']
            else:
                # Fallback to overall average
                avg_revenue = df['revenue'].mean()
                avg_orders = df['order_count'].mean()
            
            # Add some randomness to make it look more realistic
            revenue = avg_revenue * (1 + np.random.normal(0, 0.1))
            orders = max(0, round(avg_orders * (1 + np.random.normal(0, 0.1))))
            
            forecast.append({
                'date': date.strftime('%Y-%m-%d'),
                'predicted_revenue': max(0, revenue),
                'predicted_orders': int(orders),
                'confidence': 0.7  # Placeholder confidence level
            })
        
        return {
            "forecast": forecast,
            "model_type": "naive_seasonal",
            "metrics": {
                "mean_revenue": df['revenue'].mean(),
                "mean_orders": df['order_count'].mean(),
                "total_days_analyzed": len(df)
            }
        }
    
    def forecast_arima(self, days: int = 30) -> Dict[str, Any]:
        """
        Placeholder for ARIMA forecasting.
        In a real implementation, this would use statsmodels or another library.
        
        Args:
            days: Number of days to forecast
            
        Returns:
            Dictionary with forecast results
        """
        # This is a placeholder - in a real implementation, you would:
        # 1. Fit an ARIMA model to the time series
        # 2. Generate forecasts with confidence intervals
        # 3. Return the results
        
        # For now, just return the naive forecast
        return self.forecast_naive(days)
    
    def forecast(self, days: int = 30, model: str = "naive") -> Dict[str, Any]:
        """
        Generate a forecast using the specified model.
        
        Args:
            days: Number of days to forecast
            model: Model type to use ('naive', 'arima', etc.)
            
        Returns:
            Dictionary with forecast results
        """
        if model == "arima":
            return self.forecast_arima(days)
        else:
            return self.forecast_naive(days)
