from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os, json, re
import google.generativeai as genai
from weather_predictor import (
    load_and_preprocess_data,
    train_model,
    forecast_for_date,
    will_it_rain,
)
import pandas as pd

# ==============================
# Flask setup
# ==============================
app = Flask(__name__)
app.secret_key = "your-secret-key"
CORS(app)

# ==============================
# Gemini (Chatbot) Configuration
# ==============================
os.environ["GENAI_API_KEY"] = "AIzaSyCQx08C1YOYiw7Q8AaBxChwmIng02LSi4Q"
api_key = os.getenv("GENAI_API_KEY")
genai.configure(api_key=api_key)
try:
    chat_model = genai.GenerativeModel("gemini-2.5-flash")
except Exception:
    chat_model = genai.GenerativeModel("gemini-1.5-flash")

# ==============================
# Backend Data (inline)
# ==============================
backend_data = """
{
    "evaluation_temperature": {
        "mae": 2.2633052899482817,
        "rmse": 2.8552841643683684,
        "mape": 8.505556072505286
    },
    "evaluation_precipitation": {
        "mae": 14.455104282373272,
        "rmse": 18.89083766609687,
        "mape": "Infinity"
    },
    "forecast": []
}
"""

# ==============================
# Routes
# ==============================
@app.route("/")
def index():
    session.clear()
    return render_template("index.html")


# ----- CHATBOT ROUTE -----
@app.route("/chat", methods=["POST"])
def chat():
    if "conversation_history" not in session:
        session["conversation_history"] = ""
    if "current_location" not in session:
        session["current_location"] = None
    if "current_date" not in session:
        session["current_date"] = None

    user_input = request.json.get("message", "").strip()
    if not user_input:
        return jsonify({"reply": "Please type something!"})

    session["conversation_history"] += f"User: {user_input}\n"

    # ---- Step 1: Extract location & date ----
    extracted_location = session["current_location"]
    extracted_date = session["current_date"]
    try:
        extraction_prompt = f"""
        Extract location and date from this user query as JSON:
        User query: "{user_input}"
        Output JSON: {{"location": "extracted location or null", "date": "YYYY-MM-DD or null"}}
        """
        extraction_response = chat_model.generate_content(extraction_prompt)
        match = re.search(r'\{.*\}', extraction_response.text.strip(), re.DOTALL)
        if match:
            extracted = json.loads(match.group(0))
            extracted_location = extracted.get("location", session["current_location"])
            extracted_date = extracted.get("date", session["current_date"])
        session["current_location"] = extracted_location
        session["current_date"] = extracted_date
    except:
        pass  # fallback to previous context

    # ---- Step 2: Check if location & date are available for prediction ----
    forecast_text = ""
    if extracted_location and extracted_date:
        try:
            target_date = pd.to_datetime(extracted_date)
            file_name = f"{extracted_location.lower().replace(' ', '_')}.json"

            df_t2m, df_tp, has_precip, precip_key_used = load_and_preprocess_data(file_name)
            time_series_temp = df_t2m["T2M"]
            time_series_precip = df_tp[precip_key_used] if has_precip else None

            model_fit_temp = train_model(time_series_temp)
            model_fit_precip = train_model(time_series_precip) if has_precip else None

            last_date = time_series_temp.index[-1]
            forecast_context_temp, forecast_context_precip = forecast_for_date(
                model_fit_temp, model_fit_precip, last_date, target_date, has_precip, precip_key_used
            )

            temp = float(forecast_context_temp[target_date])
            precip = (
                float(forecast_context_precip[target_date])
                if has_precip and forecast_context_precip is not None
                else None
            )

            will_rain, rain_details = will_it_rain(precip, temp, target_date, has_precip)

            forecast_text = f"Forecast for {extracted_location} on {extracted_date}: Temperature {round(temp,2)}°C"
            if precip:
                forecast_text += f", Rain: {round(precip,2)} mm ({rain_details})"
            else:
                forecast_text += f", {rain_details}"
        except Exception as e:
            forecast_text = f"Sorry, I couldn't fetch the forecast: {e}"

    # ---- Step 3: Generate AI response ----
    response_prompt = f"""
    You are a helpful weather assistant.
    Use concise, natural responses.
    Conversation history: {session['conversation_history']}
    Backend data: {backend_data}
    Current context:
    - Location: "{extracted_location}"
    - Date: "{extracted_date}"
    Latest query: "{user_input}"
    If a forecast is available, include it in your answer: "{forecast_text}"
    """
    ai_reply = forecast_text or "Sorry, I couldn't generate a response."
    try:
        response = chat_model.generate_content(response_prompt)
        ai_text = response.text.strip()
        if forecast_text:  # prepend forecast for clarity
            ai_reply = f"{forecast_text}\n{ai_text}"
        else:
            ai_reply = ai_text
    except Exception as e:
        if forecast_text:
            ai_reply = forecast_text
        else:
            ai_reply = f"Error: {e}"

    session["conversation_history"] += f"Assistant: {ai_reply}\n"

    # Trim conversation history
    if len(session["conversation_history"].split()) > 3000:
        session["conversation_history"] = "\n".join(session["conversation_history"].split("\n")[-20:])

    return jsonify({"reply": ai_reply})


# ----- WEATHER PREDICTION ROUTE (untouched) -----
@app.route("/predict", methods=["POST"])
def predict_weather():
    data = request.get_json()
    city_name = data.get("city")
    target_date_str = data.get("date")

    if not city_name or not target_date_str:
        return jsonify({"error": "City and date are required"}), 400

    try:
        target_date = pd.to_datetime(target_date_str)
        file_name = f"{city_name.lower().replace(' ', '_')}.json"

        df_t2m, df_tp, has_precip, precip_key_used = load_and_preprocess_data(file_name)
        time_series_temp = df_t2m["T2M"]
        time_series_precip = df_tp[precip_key_used] if has_precip else None

        model_fit_temp = train_model(time_series_temp)
        model_fit_precip = train_model(time_series_precip) if has_precip else None

        last_date = time_series_temp.index[-1]
        forecast_context_temp, forecast_context_precip = forecast_for_date(
            model_fit_temp, model_fit_precip, last_date, target_date, has_precip, precip_key_used
        )

        temp = float(forecast_context_temp[target_date])
        precip = (
            float(forecast_context_precip[target_date])
            if has_precip and forecast_context_precip is not None
            else None
        )

        will_rain, rain_details = will_it_rain(
            precip, temp, target_date, has_precip
        )

        return jsonify(
            {
                "temperature": round(temp, 2),
                "rainfall": round(precip, 2) if precip else None,
                "humidity": 65,
                "rain_chance": rain_details,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
