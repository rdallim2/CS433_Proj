import openai
import re
from graph import DataGraph
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import pinecone

from levels import *

load_dotenv()
app = Flask(__name__)

attempts_tracker = {}
current_level = 1
message_history = [system_prompt]

#OPEN AI KEY
with open("key.txt", "r") as f:
    api_key = f.read().strip()
client = openai.OpenAI(api_key=api_key)



message_history.append(system_prompt)

@app.route('/')
def index():
    #return render_template('index.html')
    global current_level    
    message = {
        "role": "system",  # Set the role as 'system'
        "content": f"Welcome to DP-433, a simulation game designed to test your data poisoning knowledge and skills.\n\n"
                f"Current Level: {current_level}\n"
                f"Difficulty: {levels[current_level]['difficulty']}\n"
                f"Level Description: {levels[current_level]['description']}"
    }
    message_history.append(message)
    return render_template('index.html', initialMessage=message)

@app.route('/set_level', methods=['POST'])
def set_level():
    global current_level
    data = request.get_json()
    level = data.get('level')
    if level:
        current_level = level  # Set the global level to the new one
        return jsonify({"message": f"Level set to {level}"}), 200
    return jsonify({"error": "Invalid level"}), 400
    

@app.route('/ask', methods=['GET', 'POST'])
def chat_with_gpt():
    print("Welcome to the Data Injection Game!")
    print("Type 'exit' to end the game.")
    print("You will encounter increasingly difficult AI vulnerabilities to exploit as the levels progress. Good luck!")

    global current_level, message_history, attempts_tracker
    data = request.get_json()
    user_input = data.get('prompt')
    if not user_input:
        return jsonify({"error": "No prompt provided"}), 400


    if current_level not in attempts_tracker:
        attempts_tracker[current_level] = 0
    attempts_tracker[current_level] += 1

    message_history.append({"role": "user", "content": user_input})

    '''    
    if user_input.lower() == "exit":
        print("Thanks for playing! Goodbye!")
        dg = DataGraph(attempts_tracker)
        dg.save_attempts()
        dg.plot_attempts()
    '''

    for message in message_history:
        if 'role' not in message or 'content' not in message:
            print(f"Invalid message format: {message}")
            # Handle the error by skipping the malformed message or adding a default
            continue


    attempts_tracker[current_level] += 1
    dg = DataGraph(attempts_tracker)
    dg.save_attempts()

    message_history.append({"role": "user", "content": user_input})

    # This strengthens attack protection
    if re.search(r"(DROP|DELETE|TRUNCATE|ALTER|EXEC)", user_input, re.IGNORECASE):
        response_message = "Attempt detected! The system has rejected your input as potentially malicious."  
        message_history.append({"role": "assistant", "content": response_message})
        return jsonify({"message": response_message})



    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=message_history,
            max_tokens=150,
        )

        gpt_response = response.choices[0].message.content
        message_history.append({"role": "assistant", "content": gpt_response})

        # Check for success
        success = any(keyword in gpt_response.lower() for keyword in levels[current_level]["success_keywords"])
        response_data = {
            "message": gpt_response,
            "success": success
        }

        if success:
            current_level_data = levels[current_level]
            response_data["level_complete"] = True
            response_data["vulnerability_type"] = current_level_data["type"]
            response_data["difficulty"] = current_level_data["difficulty"]
            response_data["examples"] = current_level_data["examples"]
            
            # Advance to next level
            current_level += 1
            if current_level < len(levels):
                attempts_tracker[current_level] = 0
                response_data["next_level"] = {
                    "level": current_level,
                    "description": levels[current_level]["description"],
                    "difficulty": levels[current_level]["difficulty"]
                }
            else:
                response_data["game_complete"] = True
            
        # Save the attempts data
        dg = DataGraph(attempts_tracker)
        dg.save_attempts()
        print("returning some data")
        
        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5139)