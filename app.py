import openai
import os
import re
from graph import DataGraph
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import pinecone
#from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
import time
from embeddings_data import *
from p_db import *
from levels import *

load_dotenv()
app = Flask(__name__)

attempts_tracker = {}
current_level = 1
system_prompt = {
    "role": "system",
    "content": "You are a creative and immersive game master for a text-based adventure game. Respond as a narrator. Keep responses concise and engaging. only respond using context from the database.."
}


message_history = [system_prompt]

#OPEN AI KEY
with open("key.txt", "r") as f:
    openai.api_key = f.read().strip()
#print(f"DEBUG: Loaded Pinecone API Key: '{openai.api_key}' (length: {len(openai.api_key)})")



with open("p_key.txt", "r") as f:
    p_api_key = f.read().strip()

#print(f"DEBUG: Loaded Pinecone API Key: '{p_api_key}' (length: {len(p_api_key)})")
pc = Pinecone(api_key=p_api_key)



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


@app.route('/update_data', methods=['POST'])
def update_data():
    try:
        data = request.json
        item_id = data.get('id')
        new_text = data.get('text')
        namespace = "ns1"

        if not item_id or not new_text:
            return jsonify({"error": "Invalid request, missing 'id' or 'text'"}), 400

        #Initialize pinecone
        idx_name = "l" + str(current_level) + "-index"
        index = pc.Index(idx_name)
        index.update(id=str(item_id), set_metadata={"text": new_text}, namespace=namespace)

        return jsonify({"message": "Update successful", "id": item_id, "text": new_text, "namespace": namespace})

    except Exception as e:
        print(f"Error updating data: {str(e)}") 
        return jsonify({"error": "Server error", "details": str(e)}), 500


@app.route('/set_level', methods=['POST'])
def set_level():
    global current_level
    data = request.get_json()
    level = data.get('level')
    if level:
        current_level = level 
        message = {
            "role": "system",
            "content": f"Welcome to DP-433, a simulation game designed to test your data poisoning knowledge and skills.\n\n"
                       f"Current Level: {current_level}\n"
                       f"Difficulty: {levels[current_level]['difficulty']}\n"
                       f"Level Description: {levels[current_level]['description']}"
        }
        message_history.append(message)
        return jsonify({"message": message}), 200
    return jsonify({"error": "Invalid level"}), 400

@app.route('/get_data', methods=['POST'])
def get_data():
    global current_level
    idx_name = "l" + str(current_level) + "-index"
    index = pc.Index(idx_name)
    print(f"index: {idx_name}")
    try:
        query_response = index.fetch(
            ids=["vec1", "vec2", "vec3", "vec4", "vec5", "vec6", "vec7", "vec8", "vec9", "vec10"],
            namespace="ns1" 
        )
        result_data = []
        for item_id, vector_data in query_response.vectors.items():
            text = vector_data.metadata.get('text', 'No text available')
            
            result_data.append({
                'id': item_id,
                'text': text
            })
        return jsonify({'data': result_data})
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/save_quiz_answers', methods=['POST'])
def save_quiz_answers():
    try:
        data = request.get_json()
        answers = data.get("answers", {})
        folder_name = "quiz_answers"
        os.makedirs(folder_name, exist_ok=True)
        # Determine the next available filename (if quiz_answers has already been used it created quiz_answers1)
        base_filename = "quiz_answers"
        extension = ".txt"
        filename = os.path.join(folder_name, f"{base_filename}{extension}")
        counter = 1

        while os.path.exists(filename):
            filename = os.path.join(folder_name, f"{base_filename}{counter}{extension}")
            counter += 1

        # Save answers to the correct file
        with open(filename, "a") as f:
            f.write("Quiz Answers:\n")
            for question, answer in answers.items():
                f.write(f"{question}: {answer}\n")
            f.write("\n")

        return jsonify({"message": f"Quiz answers saved in {filename}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

    index_names = ["l3-index"]
    index = pc.Index(index_names[0])

    try:
        print("trying to find embedding")
        query_embedding = get_embedding(user_input)
        pinecone_results = index.query(query_embedding, top_k=3, include_metadata=True, namespace="ns1")
        print(pinecone_results)
        context = "\n".join([match["metadata"].get("text", "") for match in pinecone_results["matches"]])
    except Exception as e:
        print("Error retrieving context from Pinecone:", e)
        context = ""

    if context:
        print("Context found")
        context_message = f"Relevant context from the database:\n{context}"
        message_history.insert(0, {"role": "system", "content": context_message})

    # Append the user input to the conversation.
    message_history.append({"role": "user", "content": user_input})

    # Optional: Validate message format
    for message in message_history:
        if 'role' not in message or 'content' not in message:
            print(f"Invalid message format: {message}")
            continue

    # Save the attempts data.
    dg = DataGraph(attempts_tracker)
    dg.save_attempts()



    try:
        response = openai.chat.completions.create(
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
                response_data["trigger_end_quiz"] = True
            
        # Save the attempts data
        dg = DataGraph(attempts_tracker)
        dg.save_attempts()
        print("returning some data")
        
        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5139)