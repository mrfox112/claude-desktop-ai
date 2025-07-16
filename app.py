from flask import Flask, render_template, request, jsonify, session
import anthropic
import os
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Initialize Anthropic client
client = anthropic.Anthropic(
    api_key=os.environ.get('ANTHROPIC_API_KEY')
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Initialize conversation history in session if not exists
        if 'conversation' not in session:
            session['conversation'] = []
        
        # Add user message to conversation
        session['conversation'].append({
            'role': 'user',
            'content': user_message
        })
        
        # Send message to Claude
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0.7,
            messages=session['conversation']
        )
        
        # Extract Claude's response
        claude_response = response.content[0].text
        
        # Add Claude's response to conversation
        session['conversation'].append({
            'role': 'assistant',
            'content': claude_response
        })
        
        return jsonify({
            'response': claude_response,
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/clear', methods=['POST'])
def clear_conversation():
    session['conversation'] = []
    return jsonify({'success': True})

@app.route('/conversation', methods=['GET'])
def get_conversation():
    return jsonify({
        'conversation': session.get('conversation', []),
        'success': True
    })

if __name__ == '__main__':
    # Check if API key is set
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("❌ ANTHROPIC_API_KEY not found in environment variables!")
        print("Please copy .env.example to .env and add your API key")
        exit(1)
    
    print("🚀 Starting Local Claude AI...")
    print("📝 Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)
