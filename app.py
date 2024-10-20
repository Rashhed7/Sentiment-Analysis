from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import os
import pandas as pd
from textblob import TextBlob  # Ensure TextBlob is installed

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

UPLOAD_FOLDER = 'uploads'  
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def analyze_sentiment(comments):
    results = []
    for comment in comments:
        analysis = TextBlob(comment)  # Analyze the comment
        # Classify sentiment based on polarity
        if analysis.sentiment.polarity > 0:
            sentiment = 'Positive'
        elif analysis.sentiment.polarity < 0:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'
        
        results.append({
            'comment': comment,
            'sentiment': sentiment,
            'polarity': analysis.sentiment.polarity
        })
    
    return results

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            df = pd.read_csv(filepath)

            # Ensure your DataFrame contains the 'comment' column
            comments = df['comment'].tolist()  # Get comments as a list

            # Analyze sentiment
            sentiment_results = analyze_sentiment(comments)

            return jsonify({'message': 'File successfully uploaded and processed', 'data': sentiment_results}), 200
        except pd.errors.EmptyDataError:
            return jsonify({'error': 'Uploaded file is empty.'}), 400
        except pd.errors.ParserError:
            return jsonify({'error': 'Error parsing the CSV file. Please check its format.'}), 400
        except Exception as e:
            return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
