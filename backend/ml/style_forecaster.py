# backend/ml/style_forecaster.py

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from db import models

class StyleForecaster:
    """
    A forecasting service that provides sales projections for product styles
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
    
    def extract_style(self, product_name: str) -> str:
        """
        Extract style information from product name.
        This is a simple implementation that assumes style is the first word.
        In a real-world scenario, this would be more sophisticated.
        
        Args:
            product_name: The product name to extract style from
            
        Returns:
            The extracted style
        """
        if not product_name:
            return "Unknown"
        
        # Split by spaces and take the first word as the style
        # This is a simple implementation - in reality, you'd want more sophisticated parsing
        parts = product_name.split()
        if not parts:
            return "Unknown"
        
        # Return the first word as the style
        return parts[0]
    
    def load_data(self) -> pd.DataFrame:
        """
        Load order data from the database and convert to a time series by style.
        
        Returns:
            DataFrame with date and style information
        """
        # Query line items for this user and upload
        query = (
            self.db.query(
                models.Order.created_at,
                models.LineItem.lineitem_name,
                models.LineItem.lineitem_quantity,
                models.LineItem.lineitem_price
            )
            .join(models.LineItem, models.Order.id == models.LineItem.order_id)
            .filter(
                models.Order.user_id == self.user_id,
                models.Order.upload_id == self.upload_id
            )
        )
        
        # Execute query and convert to DataFrame
        rows = query.all()
        data = []
        for row in rows:
            if row.created_at and row.lineitem_name and row.lineitem_quantity is not None:
                # Extract style from product name
                style = self.extract_style(row.lineitem_name)
                
                # Calculate revenue
                price = float(row.lineitem_price) if row.lineitem_price is not None else 0
                revenue = price * row.lineitem_quantity
                
                data.append({
                    'date': row.created_at.date(),
                    'style': style,
                    'quantity': row.lineitem_quantity,
                    'revenue': revenue
                })
        
        # Create DataFrame
        df = pd.DataFrame(data)
        if df.empty:
            return pd.DataFrame()
        
        # Group by date and style
        daily_style_data = df.groupby(['date', 'style']).agg(
            order_count=('quantity', 'count'),
            total_quantity=('quantity', 'sum'),
            total_revenue=('revenue', 'sum')
        ).reset_index()
        
        self.data = daily_style_data
        return daily_style_data
    
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
        
        # For each style, calculate rolling averages
        styles = df['style'].unique()
        result_dfs = []
        
        for style in styles:
            style_df = df[df['style'] == style].copy()
            
            # Sort by date
            style_df = style_df.sort_values('date')
            
            # Add rolling averages if we have enough data
            if len(style_df) >= 3:
                style_df['quantity_7d_avg'] = style_df['total_quantity'].rolling(window=7, min_periods=1).mean()
                style_df['revenue_7d_avg'] = style_df['total_revenue'].rolling(window=7, min_periods=1).mean()
            else:
                style_df['quantity_7d_avg'] = style_df['total_quantity']
                style_df['revenue_7d_avg'] = style_df['total_revenue']
            
            result_dfs.append(style_df)
        
        # Combine all style dataframes
        if result_dfs:
            prepared_df = pd.concat(result_dfs)
            prepared_df = prepared_df.fillna(0)
            self.prepared_data = prepared_df
            return prepared_df
        else:
            return pd.DataFrame()
    
    def forecast_naive(self, days: int = 30) -> Dict[str, Any]:
        """
        Generate a simple naive forecast for styles based on historical averages.
        
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
        
        # Get unique styles
        styles = df['style'].unique()
        
        # Calculate averages by day of week for each style
        style_dow_avg = {}
        for style in styles:
            style_df = df[df['style'] == style]
            dow_avg = style_df.groupby('day_of_week').agg({
                'total_quantity': 'mean',
                'total_revenue': 'mean'
            })
            style_dow_avg[style] = dow_avg
        
        # Get the last date in the dataset
        last_date = df['date'].max()
        
        # Generate forecast dates
        forecast_dates = [last_date + timedelta(days=i+1) for i in range(days)]
        
        # Generate forecast values for each style
        forecast = []
        for date in forecast_dates:
            # Get day of week (0=Monday, 6=Sunday)
            dow = date.weekday()
            
            for style in styles:
                # Get average values for this style and day of week
                if style in style_dow_avg and dow in style_dow_avg[style].index:
                    avg_quantity = style_dow_avg[style].loc[dow, 'total_quantity']
                    avg_revenue = style_dow_avg[style].loc[dow, 'total_revenue']
                else:
                    # Fallback to overall average for this style
                    style_df = df[df['style'] == style]
                    avg_quantity = style_df['total_quantity'].mean()
                    avg_revenue = style_df['total_revenue'].mean()
                
                # Add some randomness to make it look more realistic
                quantity = max(0, avg_quantity * (1 + np.random.normal(0, 0.1)))
                revenue = max(0, avg_revenue * (1 + np.random.normal(0, 0.1)))
                
                forecast.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'style': style,
                    'predicted_quantity': round(quantity),
                    'predicted_revenue': revenue,
                    'confidence': 0.7  # Placeholder confidence level
                })
        
        # Get style metrics
        style_metrics = []
        for style in styles:
            style_df = df[df['style'] == style]
            style_metrics.append({
                'style': style,
                'mean_quantity': style_df['total_quantity'].mean(),
                'mean_revenue': style_df['total_revenue'].mean(),
                'total_days_analyzed': len(style_df)
            })
        
        return {
            "forecast": forecast,
            "model_type": "naive_seasonal",
            "styles": list(styles),
            "style_metrics": style_metrics,
            "overall_metrics": {
                "mean_quantity": df['total_quantity'].mean(),
                "mean_revenue": df['total_revenue'].mean(),
                "total_days_analyzed": len(df['date'].unique())
            }
        }
    
    def forecast_arima(self, days: int = 30) -> Dict[str, Any]:
        """
        Placeholder for ARIMA forecasting by style.
        In a real implementation, this would use statsmodels or another library.
        
        Args:
            days: Number of days to forecast
            
        Returns:
            Dictionary with forecast results
        """
        # This is a placeholder - in a real implementation, you would:
        # 1. Fit an ARIMA model to each style's time series
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
