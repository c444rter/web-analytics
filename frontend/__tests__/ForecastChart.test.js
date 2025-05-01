// __tests__/ForecastChart.test.js
import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ForecastChart from '../components/ForecastChart';
import { useAvailableModels, useForecast } from '../hooks/useProjections';

// Mock the hooks
jest.mock('../hooks/useProjections', () => ({
  useAvailableModels: jest.fn(),
  useForecast: jest.fn()
}));

// Create a new QueryClient for each test
const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

// Wrapper component with QueryClientProvider
const createWrapper = () => {
  const testQueryClient = createTestQueryClient();
  return ({ children }) => (
    <QueryClientProvider client={testQueryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('ForecastChart Component', () => {
  beforeEach(() => {
    // Reset mocks before each test
    jest.clearAllMocks();
  });

  test('renders loading state correctly', () => {
    // Mock the hooks to return loading state
    useAvailableModels.mockReturnValue({
      data: null,
      isLoading: true
    });
    
    useForecast.mockReturnValue({
      data: null,
      isLoading: true,
      isError: false,
      refreshForecast: jest.fn()
    });

    const Wrapper = createWrapper();
    render(<ForecastChart uploadId={1} />, { wrapper: Wrapper });

    // Check for loading indicators
    expect(screen.getByText(/Loading models/i)).toBeInTheDocument();
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  test('renders forecast data correctly', async () => {
    // Mock available models
    const mockModels = [
      { id: 'naive', name: 'Naive Seasonal', description: 'Simple forecasting' },
      { id: 'arima', name: 'ARIMA', description: 'Advanced forecasting' }
    ];
    
    // Mock forecast data
    const mockForecastData = {
      upload_id: 1,
      days_forecasted: 30,
      model: 'naive',
      generated_at: '2025-04-30T10:00:00Z',
      forecast: {
        forecast: [
          {
            date: '2025-05-01',
            predicted_revenue: 1000.50,
            predicted_orders: 10,
            confidence: 0.8
          },
          {
            date: '2025-05-02',
            predicted_revenue: 1200.75,
            predicted_orders: 12,
            confidence: 0.7
          }
        ],
        metrics: {
          mean_revenue: 1100.25,
          mean_orders: 11,
          total_days_analyzed: 90
        }
      }
    };
    
    // Set up the mock return values
    useAvailableModels.mockReturnValue({
      data: mockModels,
      isLoading: false
    });
    
    useForecast.mockReturnValue({
      data: mockForecastData,
      isLoading: false,
      isError: false,
      refreshForecast: jest.fn()
    });

    const Wrapper = createWrapper();
    render(<ForecastChart uploadId={1} />, { wrapper: Wrapper });

    // Check that the component renders the forecast data
    await waitFor(() => {
      expect(screen.getByText('Sales Forecast')).toBeInTheDocument();
      expect(screen.getByText('Forecast Period (Days)')).toBeInTheDocument();
      expect(screen.getByText('Forecast Model')).toBeInTheDocument();
      expect(screen.getByText('Refresh Forecast')).toBeInTheDocument();
      
      // Check for metrics
      expect(screen.getByText(/Mean Revenue/i)).toBeInTheDocument();
      expect(screen.getByText(/Mean Orders/i)).toBeInTheDocument();
      expect(screen.getByText(/Days Analyzed/i)).toBeInTheDocument();
    });
  });

  test('handles error state correctly', () => {
    // Mock the hooks to return error state
    useAvailableModels.mockReturnValue({
      data: null,
      isLoading: false
    });
    
    useForecast.mockReturnValue({
      data: null,
      isLoading: false,
      isError: true,
      refreshForecast: jest.fn()
    });

    const Wrapper = createWrapper();
    render(<ForecastChart uploadId={1} />, { wrapper: Wrapper });

    // Check for error message
    expect(screen.getByText(/Error loading forecast data/i)).toBeInTheDocument();
  });

  test('handles model selection change', async () => {
    // Mock available models
    const mockModels = [
      { id: 'naive', name: 'Naive Seasonal', description: 'Simple forecasting' },
      { id: 'arima', name: 'ARIMA', description: 'Advanced forecasting' }
    ];
    
    // Mock forecast data
    const mockForecastData = {
      upload_id: 1,
      days_forecasted: 30,
      model: 'naive',
      generated_at: '2025-04-30T10:00:00Z',
      forecast: {
        forecast: [],
        metrics: {
          mean_revenue: 1100.25,
          mean_orders: 11,
          total_days_analyzed: 90
        }
      }
    };
    
    // Set up the mock return values
    useAvailableModels.mockReturnValue({
      data: mockModels,
      isLoading: false
    });
    
    useForecast.mockReturnValue({
      data: mockForecastData,
      isLoading: false,
      isError: false,
      refreshForecast: jest.fn()
    });

    const Wrapper = createWrapper();
    render(<ForecastChart uploadId={1} />, { wrapper: Wrapper });

    // Find and click the model select
    const modelSelect = screen.getByLabelText(/Forecast Model/i);
    fireEvent.mouseDown(modelSelect);
    
    // Wait for the dropdown to appear and select ARIMA
    await waitFor(() => {
      const arimaOption = screen.getByText('ARIMA');
      fireEvent.click(arimaOption);
    });
    
    // Check that the model was changed
    expect(useForecast).toHaveBeenCalledWith(1, 30, 'naive', true);
  });

  test('handles refresh button click', async () => {
    // Mock the hooks
    const mockRefreshForecast = jest.fn();
    
    useAvailableModels.mockReturnValue({
      data: [{ id: 'naive', name: 'Naive Seasonal' }],
      isLoading: false
    });
    
    useForecast.mockReturnValue({
      data: {
        forecast: {
          forecast: [],
          metrics: {}
        }
      },
      isLoading: false,
      isError: false,
      refreshForecast: mockRefreshForecast
    });

    const Wrapper = createWrapper();
    render(<ForecastChart uploadId={1} />, { wrapper: Wrapper });

    // Find and click the refresh button
    const refreshButton = screen.getByText('Refresh Forecast');
    fireEvent.click(refreshButton);
    
    // Check that refreshForecast was called
    expect(mockRefreshForecast).toHaveBeenCalled();
  });
});
