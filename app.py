from flask import Flask, request, jsonify, send_from_directory
import joblib
import pandas as pd
import numpy as np
import os

app = Flask(__name__, static_folder='.')

# Load the saved model and preprocessors
model = joblib.load('rf_classifier_model.pkl')
scaler = joblib.load('scaler.pkl')
encoder = joblib.load('encoder.pkl')
selected_features = joblib.load('selected_features.pkl')

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        input_data = pd.DataFrame([{
            'Area': data['Area'],
            'Rainfall': data['Rainfall'],
            'Contract_Area': data['Contract_Area'],
            'Fertilizer_Type': data['Fertilizer_Type'],
            'Epidemic': data['Epidemic'],
            'Water_Type': data['Water_Type'],
            'Soil_Type': data['Soil_Type'],
            'Fertilizer': data['Fertilizer'],
            'Country': data['Country']
        }])

        # Encode categorical columns
        categorical_cols = input_data.select_dtypes(include='object').columns
        encoded = encoder.transform(input_data[categorical_cols])
        encoded_df = pd.DataFrame(encoded, columns=encoder.get_feature_names_out(categorical_cols))

        # Merge with scaled numerical columns
        input_data = pd.concat([input_data.drop(columns=categorical_cols), encoded_df], axis=1)
        numerical_cols = ['Area', 'Rainfall', 'Contract_Area']
        input_data[numerical_cols] = scaler.transform(input_data[numerical_cols])

        # Select features
        input_data = input_data[selected_features]

        # Predict
        prediction = model.predict(input_data)
        prediction_label = 'High' if prediction[0] == 1 else 'Low'

        return jsonify({'prediction': prediction_label, 'status': 'success'})

    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'})

if __name__ == '__main__':
    app.run(debug=True)
