import openai
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# You'll need to put your own key
openai.api_key_path = 'key.txt'

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ask', methods=['POST'])
def chat_with_gpt():
    data = request.get_json()
    user_input = data.get('prompt')
    if not user_input:
        return jsonify({"error": "No prompt provided"}), 400
    
    system_prompt = {
        "role": "system",
        "content": user_input
    }


    message_history = [system_prompt]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=message_history,
            max_tokens=1000,
        )

        gpt_response = response['choices'][0]['message']['content']
        print("Returning a response")
        return jsonify({"response": gpt_response})


    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5139)