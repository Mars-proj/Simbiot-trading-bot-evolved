from flask import Flask, request, jsonify
from ml_predictor import predict
import logging

app = Flask(__name__)

def setup_logging():
    logging.basicConfig(
        filename='api.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

@app.route('/predict', methods=['POST'])
def predict_endpoint():
    setup_logging()
    try:
        data = request.json
        data_df = pd.DataFrame(data)
        prediction = predict(data_df, model_id=1)
        logging.info(f"Prediction made: {prediction}")
        return jsonify({"prediction": prediction})
    except Exception as e:
        logging.error(f"Prediction failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
