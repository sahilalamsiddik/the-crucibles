import json
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
import warnings
import os
from datetime import datetime

warnings.filterwarnings("ignore", message="No supported index is available. Prediction results will be given with default integer index after 0.")
warnings.filterwarnings("ignore", message="A date index has been provided, but it has no associated frequency information and so will be ignored when e.g. forecasting.")
warnings.filterwarnings("ignore", message="Maximum Likelihood optimization failed to converge. Check mle_retvals.")

def load_and_preprocess_data(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"JSON file not found: {file_path}. Please ensure the file exists and is named correctly.")

    with open(file_path, 'r') as f:
        data = json.load(f)

    properties = data.get('properties', {}).get('parameter', {})
    
    # Print available parameters for debugging
    available_params = list(properties.keys()) if properties else []
    print(f"Available parameters in JSON: {available_params}")
    if 'T2M' not in available_params:
        raise KeyError("Expected 'T2M' parameter in JSON structure.")
    
    t2m_data = properties['T2M']
    
    # Try to find precipitation data with common keys, prioritizing 'PRECTOTCORR'
    precip_keys = ['PRECTOTCORR', 'TP', 'PRECT', 'RAIN', 'PRCP', 'TOTAL_PRECIPITATION']  # Added 'PRECTOTCORR' first
    precip_data = None
    precip_key_used = None
    for key in precip_keys:
        if key in available_params:
            precip_data = properties[key]
            precip_key_used = key
            break
    
    has_precip = bool(precip_data)
    
    # Create DataFrame for T2M
    df_t2m = pd.DataFrame(list(t2m_data.items()), columns=['Date', 'T2M'])
    df_t2m['Date'] = pd.to_datetime(df_t2m['Date'], format='%Y%m%d')
    df_t2m = df_t2m.set_index('Date')
    df_t2m = df_t2m.asfreq('D')
    df_t2m['T2M'] = df_t2m['T2M'].fillna(method='ffill').fillna(method='bfill')

    # Load precipitation if available
    df_tp = None
    if has_precip:
        df_tp = pd.DataFrame(list(precip_data.items()), columns=['Date', precip_key_used])
        df_tp['Date'] = pd.to_datetime(df_tp['Date'], format='%Y%m%d')
        df_tp = df_tp.set_index('Date')
        df_tp = df_tp.asfreq('D')
        df_tp[precip_key_used] = df_tp[precip_key_used].fillna(0)  # Fill missing with 0 (no rain)
        print(f"Precipitation data loaded successfully using key '{precip_key_used}'.")
    else:
        print("No precipitation data found. Using heuristic for rain prediction.")
        print("Suggestion: Add precip data to JSON (e.g., under 'PRECTOTCORR' or 'TP') or use an external API.")

    return df_t2m, df_tp, has_precip, precip_key_used

def train_model(data, order=(1,1,1), seasonal_order=(1,1,1,7)):
    if data is None or len(data) == 0:
        return None
    if data.index.freq is None:
        data = data.asfreq('D')
    model = SARIMAX(data, order=order, seasonal_order=seasonal_order,
                    enforce_stationarity=False, enforce_invertibility=False)
    model_fit = model.fit(disp=False)
    return model_fit

def evaluate_model(model_fit, test_data):
    if model_fit is None or test_data is None:
        return None, None, None, None
    start = len(model_fit.fittedvalues)
    end = start + len(test_data) - 1
    predictions = model_fit.predict(start=start, end=end, dynamic=False)
    predictions.index = test_data.index
    mae = mean_absolute_error(test_data, predictions)
    rmse = np.sqrt(mean_squared_error(test_data, predictions))
    mape = np.mean(np.abs((test_data - predictions) / test_data)) * 100
    return predictions, mae, rmse, mape

def forecast_for_date(model_fit_temp, model_fit_precip, last_date, target_date, has_precip, precip_key_used):
    """
    Forecasts daily temperature and precipitation (if available) from the day after last_date up to target_date,
    then returns the predicted values for target_date and a few days before for context.
    """
    if target_date <= last_date:
        raise ValueError("Target date must be after the last date in the dataset.")

    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), end=target_date, freq='D')
    n_steps = len(future_dates)
    
    # Temperature forecast
    forecast_temp = model_fit_temp.predict(start=len(model_fit_temp.fittedvalues),
                                          end=len(model_fit_temp.fittedvalues) + n_steps - 1)
    forecast_temp.index = future_dates

    # Precipitation forecast (if available)
    forecast_precip = None
    if has_precip and model_fit_precip:
        forecast_precip = model_fit_precip.predict(start=len(model_fit_precip.fittedvalues),
                                                  end=len(model_fit_precip.fittedvalues) + n_steps - 1)
        forecast_precip.index = future_dates
        # Ensure non-negative (precip can't be negative)
        forecast_precip = forecast_precip.clip(lower=0)

    # Extract forecast for target date and 3 days before for context (if available)
    context_start = max(target_date - pd.Timedelta(days=3), future_dates[0])
    context_temp = forecast_temp[context_start:target_date]
    context_precip = forecast_precip[context_start:target_date] if has_precip else None

    return context_temp, context_precip

def will_it_rain(precip_forecast, temp_forecast, date, has_precip):
    """Rain prediction: Use actual precip if available, else heuristic based on temp and season."""
    if has_precip and precip_forecast is not None:
        # Actual precip: rain if > 0 mm (adjust threshold if needed, e.g., >0.1 for light rain)
        return precip_forecast > 0, f"Rain: {'Yes' if precip_forecast > 0 else 'No'} (Precip: {precip_forecast:.2f} mm)"
    
    # Heuristic fallback (simple, not accurate—customize for your region)
    month = date.month
    temp = temp_forecast if temp_forecast is not None else 25  # Default temp
    # Example for Indian cities: Higher rain chance in monsoon (Jun-Sep) if temp 20-30°C
    is_monsoon = 6 <= month <= 9
    likely_rain = is_monsoon and 20 <= temp <= 30
    rain_status = "Yes (Likely)" if likely_rain else "No (Unlikely)"
    precip_estimate = ">0.1 mm (est.)" if likely_rain else "0 mm (est.)"
    return likely_rain, f"Rain: {rain_status} ({precip_estimate} - heuristic)"

def main():
    city_name = input("Enter city name (e.g., Bangalore, Mumbai): ").strip()
    file_name = f"{city_name.lower().replace(' ', '_')}.json"
    target_date_str = input("Enter target future date (YYYY-MM-DD, e.g., 2025-12-31): ").strip()
    try:
        target_date = pd.to_datetime(target_date_str)
    except:
        print("Invalid date format. Please use YYYY-MM-DD.")
        return

    df_t2m, df_tp, has_precip, precip_key_used = load_and_preprocess_data(file_name)
    time_series_temp = df_t2m['T2M']
    time_series_precip = df_tp[precip_key_used] if has_precip else None

    train_size = int(len(time_series_temp) * 0.95)
    train_temp, test_temp = time_series_temp.iloc[:train_size], time_series_temp.iloc[train_size:]
    train_precip = time_series_precip.iloc[:train_size] if has_precip else None
    test_precip = time_series_precip.iloc[train_size:] if has_precip else None

    model_fit_temp = train_model(train_temp)
    model_fit_precip = train_model(train_precip) if has_precip else None

    # Optional: Evaluate models on test data and print metrics
    print(f"\nModel evaluation on test data (Temperature):")
    test_preds_temp, mae_temp, rmse_temp, mape_temp = evaluate_model(model_fit_temp, test_temp)
    print(f"MAE: {mae_temp:.2f}, RMSE: {rmse_temp:.2f}, MAPE: {mape_temp:.2f}%")

    if has_precip:
        print(f"\nModel evaluation on test data (Precipitation):")
        test_preds_precip, mae_precip, rmse_precip, mape_precip = evaluate_model(model_fit_precip, test_precip)
        print(f"MAE: {mae_precip:.4f}, RMSE: {rmse_precip:.4f}, MAPE: {mape_precip:.2f}%")

    last_date = time_series_temp.index[-1]
    if target_date <= last_date:
        print(f"Warning: Target date {target_date.strftime('%Y-%m-%d')} is not in the future relative to data end date {last_date.strftime('%Y-%m-%d')}.")
        print("No forecast will be made for past dates.")
        return

    forecast_context_temp, forecast_context_precip = forecast_for_date(
        model_fit_temp, model_fit_precip, last_date, target_date, has_precip, precip_key_used
    )

    print(f"\n--- Forecasted Weather Details for {city_name.capitalize()} ---")
    print(f"Data end date: {last_date.strftime('%Y-%m-%d')}")
    if has_precip:
        print(f"Using precipitation data from '{precip_key_used}' (rain if > 0 mm).")
    else:
        print("No precip data; using simple heuristic for rain (based on season/temp). Not highly accurate.")
    
    for date in forecast_context_temp.index:
        temp = forecast_context_temp[date]
        day_label = "Target Date" if date == target_date else f"Context ({(target_date - date).days} days prior)"
        will_rain, rain_details = will_it_rain(
            forecast_context_precip[date] if has_precip else None, 
            temp, 
            date, 
            has_precip
        )
        print(f"{date.strftime('%Y-%m-%d')} ({day_label}): {temp:.2f} °C | {rain_details}")

if __name__ == "__main__":
    main()
