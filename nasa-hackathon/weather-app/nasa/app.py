from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os, json, re
import google.generativeai as genai
from weather_predictor import load_and_preprocess_data, train_model, forecast_for_date, will_it_rain
import pandas as pd

app = Flask(__name__)
app.secret_key = "your-secret-key"
CORS(app)

os.environ["GENAI_API_KEY"] = "AIzaSyCQx08C1YOYiw7Q8AaBxChwmIng02LSi4Q"
api_key = os.getenv("GENAI_API_KEY")
genai.configure(api_key=api_key)
try:
    chat_model = genai.GenerativeModel("gemini-2.5-flash")
except Exception:
    chat_model = genai.GenerativeModel("gemini-1.5-flash")

backend_data = '{"evaluation_temperature":{"mae":2.2633,"rmse":2.8552,"mape":8.5056},"evaluation_precipitation":{"mae":14.4551,"rmse":18.8908,"mape":"Infinity"},"forecast":[]}'

@app.route("/")
def index():
    session.clear()
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    if "conversation_history" not in session:
        session["conversation_history"] = ""
    if "current_location" not in session:
        session["current_location"] = None
    if "current_date" not in session:
        session["current_date"] = None
    if "last_forecast" not in session:
        session["last_forecast"] = None

    user_input = request.json.get("message", "").strip()
    if not user_input:
        return jsonify({"reply": "Please type something!"})

    session["conversation_history"] += f"User: {user_input}\n"
    user_lower = user_input.lower()
    extracted_location = session.get("current_location")
    extracted_date = session.get("current_date")

    try:
        extraction_prompt = f"""
        Extract location and date from this user query as JSON.
        Return JSON exactly in the form: {{ "location": "<city or null>", "date": "<YYYY-MM-DD or null>" }}
        User query: \"{user_input}\"
        """
        extraction_response = chat_model.generate_content(extraction_prompt)
        match = re.search(r"\{[\s\S]*\}", extraction_response.text.strip())
        if match:
            parsed = json.loads(match.group(0))
            loc = parsed.get("location")
            if loc and isinstance(loc, str) and loc.strip().lower() != "null":
                extracted_location = loc.strip()
            dt = parsed.get("date")
            if dt and isinstance(dt, str) and dt.strip().lower() != "null":
                iso = pd.to_datetime(dt, dayfirst=False, errors="coerce")
                if not pd.isna(iso):
                    extracted_date = iso.strftime("%Y-%m-%d")
        session["current_location"] = extracted_location
        session["current_date"] = extracted_date
    except Exception:
        pass

    if "date" in user_lower and any(w in user_lower for w in ("ask", "asked", "just", "which", "what", "did", "previous", "last")):
        reply = f"You asked for {session['current_date']}." if session.get("current_date") else "I don't have a recorded date."
        session["conversation_history"] += f"Assistant: {reply}\n"
        return jsonify({"reply": reply})

    if any(w in user_lower for w in ("which city", "which location", "what city", "what location", "which place")) or \
       ("location" in user_lower and any(w in user_lower for w in ("ask", "asked", "did", "which", "what", "last"))):
        reply = f"You asked about {session['current_location']}." if session.get("current_location") else "I don't have a recorded location."
        session["conversation_history"] += f"Assistant: {reply}\n"
        return jsonify({"reply": reply})

    if any(w in user_lower for w in ("repeat", "remind", "again", "show me")) and any(w in user_lower for w in ("forecast", "weather", "prediction", "result", "last")):
        last = session.get("last_forecast")
        reply = last["text"] if last and isinstance(last, dict) and last.get("text") else "I don't have a saved forecast."
        session["conversation_history"] += f"Assistant: {reply}\n"
        return jsonify({"reply": reply})

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
            forecast_context_temp, forecast_context_precip = forecast_for_date(model_fit_temp, model_fit_precip, last_date, target_date, has_precip, precip_key_used)
            temp = float(forecast_context_temp[target_date])
            precip = float(forecast_context_precip[target_date]) if has_precip and forecast_context_precip is not None else 0.0
            if temp >= 35:
                feeling = "It will feel very hot."
            elif temp >= 28:
                feeling = "It will feel warm."
            elif temp >= 20:
                feeling = "It will feel pleasant."
            else:
                feeling = "It will feel cool."
            if precip >= 10:
                rain_feel = "Expect heavy/rainy conditions."
            elif precip >= 5:
                rain_feel = "Expect rainy weather."
            elif precip > 0:
                rain_feel = "Light rain is possible."
            else:
                rain_feel = "It should remain dry."
            forecast_text = f"Forecast for {extracted_location} on {extracted_date}: Temperature {round(temp,2)}°C, Rain: {round(precip,2)} mm. {feeling} {rain_feel}"
            session["last_forecast"] = {"text": forecast_text, "temp": temp, "precip": precip, "date": extracted_date, "location": extracted_location}
            session["current_location"] = extracted_location
            session["current_date"] = extracted_date
        except Exception as e:
            forecast_text = f"Couldn't compute forecast: {e}"
            session["last_forecast"] = {"text": forecast_text}

    response_prompt = f"""
    You are a helpful weather assistant. Keep replies short.
    Conversation history:
    {session['conversation_history']}
    If available, this is the forecast info to include at the top: "{forecast_text}"
    Latest user query: "{user_input}"
    """
    ai_text = ""
    try:
        response = chat_model.generate_content(response_prompt)
        ai_text = response.text.strip()
    except Exception:
        ai_text = ""

    ai_reply = f"{forecast_text}\n{ai_text}".strip() if forecast_text else ai_text or "Please tell me a city and a date."

    session["conversation_history"] += f"Assistant: {ai_reply}\n"
    return jsonify({"reply": ai_reply})

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
        forecast_context_temp, forecast_context_precip = forecast_for_date(model_fit_temp, model_fit_precip, last_date, target_date, has_precip, precip_key_used)
        temp = float(forecast_context_temp[target_date])
        precip = float(forecast_context_precip[target_date]) if has_precip and forecast_context_precip is not None else 0.0
        will_rain, rain_details = will_it_rain(precip, temp, target_date, has_precip)
        base_humidity = 50 + (precip * 2) - ((temp - 25) * 0.8)
        humidity = max(30, min(round(base_humidity, 2), 95))
        if precip >= 10: rain_probability = "90%"
        elif precip >= 9: rain_probability = "95%"
        elif precip >= 8.5: rain_probability = "85%"
        elif precip >=8: rain_probability = "80%"
        elif precip >= 7.5: rain_probability = "77.5%"
        elif precip >= 7: rain_probability = "75%"
        elif precip >= 6: rain_probability = "70%"
        elif precip >= 5: rain_probability = "60%"
        elif precip > 0: rain_probability = "40%"
        else: rain_probability = "10%"
        return jsonify({"temperature": round(temp, 2), "rainfall": round(precip, 2), "humidity": humidity, "rain_chance": rain_probability, "rain_details": rain_details, "will_rain": "Yes" if will_rain else "No"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
