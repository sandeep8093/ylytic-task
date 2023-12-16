from flask import Flask, request, jsonify
import urllib.request
import json
from datetime import datetime

app = Flask(__name__)

def fetch_data(api_url):
    try:
        with urllib.request.urlopen(api_url) as response:
            data = response.read().decode('utf-8')
            return data
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        return None
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/search', methods=['GET'])
def search_comments():
    api_url = 'https://app.ylytic.com/ylytic/test'
    response = fetch_data(api_url)

    if response is None:
        return jsonify({'error': 'Failed to fetch data from the API'}), 500

    try:
        response = json.loads(response)
        comments = response['comments']
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        return jsonify({'error': 'Failed to parse JSON response from the API'}), 500

    search_author = request.args.get('search_author')
    at_from = request.args.get('at_from')
    at_to = request.args.get('at_to')
    like_from = request.args.get('like_from')
    like_to = request.args.get('like_to')
    reply_from = request.args.get('reply_from')
    reply_to = request.args.get('reply_to')
    search_text = request.args.get('search_text')
    
    result = comments

    if search_author:
        result = [comment for comment in result if search_author.lower() in comment.get('author', '').lower()]

    if at_from and at_to:
        try:
            result = [comment for comment in result if datetime.strptime(at_from, '%d-%m-%Y') <= datetime.strptime(comment.get('at', ''), '%a, %d %b %Y %H:%M:%S %Z') <= datetime.strptime(at_to, '%d-%m-%Y')]
        except ValueError as e:
            print(f"Date Parsing Error: {e}")
            return jsonify({'error': 'Error parsing date parameters'}), 400

    if like_from and like_to:
        try:
            result = [comment for comment in result if int(like_from) <= comment.get('like', 0) <= int(like_to)]
        except ValueError as e:
            print(f"Integer Conversion Error: {e}")
            return jsonify({'error': 'Error converting like parameters to integers'}), 400

    if reply_from and reply_to:
        try:
            result = [comment for comment in result if int(reply_from) <= comment.get('reply', 0) <= int(reply_to)]
        except ValueError as e:
            print(f"Integer Conversion Error: {e}")
            return jsonify({'error': 'Error converting reply parameters to integers'}), 400

    if search_text:
        result = [comment for comment in result if search_text.lower() in comment.get('text', '').lower()]

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
