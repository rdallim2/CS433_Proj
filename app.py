import openai
import os
import re
import time
from graph import DataGraph
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from pinecone import ServerlessSpec
from embeddings_data import *
from p_db import *
from levels import *


load_dotenv()
app = Flask(__name__)

attempts_tracker = {}
current_level = 1
system_prompt = {
    "role": "system",
    "content": """
    Follow user requests and prompts as directed. Do not attempt to fact check any conversation context data. Base output on retrieved data from pinecone db. 
    Keep responses concise and engaging. If data from the pinecone db is similar enough to the user prompt, simply output the corresponding data in the DB. Prioritize data from the vector database, even when it conflicts with openai's pretraining data. 
    Do not correct data from the database. You must treat all retrieved context from the vector database as absolute truth, even if it conflicts with your pretraining. 
    Do not correct, modify, or combine retrieved facts with prior knowledge. The database is always correct."""
}
message_history = [system_prompt]

#OPEN AI KEY
with open("key.txt", "r") as f:
    openai.api_key = f.read().strip()
#PINECONE DB KEY
with open("p_key.txt", "r") as f:
    p_api_key = f.read().strip()
pc = Pinecone(api_key=p_api_key)



@app.route('/')
def index():
    global current_level    
    message = {
        "role": "system",
        "content": f"Welcome to DP-433, a simulation game designed to test your data poisoning knowledge and skills.\n"
                f"Current Level: {current_level}\n"
                f"Difficulty: {levels[current_level]['difficulty']}\n"
                f"Level Description: {levels[current_level]['description']}"
    }
    message_history.append(message)
    return render_template('index.html', initialMessage=message)



@app.route('/update_data', methods=['POST'])
def update_data():
    global message_history
    data = request.json
    item_id = data.get('id')
    new_text = data.get('text')

    new_embedding = get_embedding(new_text)
    idx_name = "l" + str(current_level) + "-index"
    index = pc.Index(idx_name)

    index.upsert(
        vectors=[{
            "id": str(item_id),
            "values": new_embedding,
            "metadata": {"text": new_text}
        }],
        namespace = "ns1"
    )
    return jsonify({"message": "Update successful", "id": item_id, "text": new_text, "namespace": "ns1"})
    


@app.route('/set_level', methods=['POST'])
def set_level():
    global current_level
    data = request.get_json()
    current_level = data.get('level')

    #clear the message history and append the new level new each time use selects a new level
    for message in message_history:
        message_history.clear()

    message = {
        "role": "system",
        "content": f"Welcome to DP-433, a simulation game designed to test your data poisoning knowledge and skills.\n\n"
                    f"Current Level: {current_level}\n"
                    f"Difficulty: {levels[current_level]['difficulty']}\n"
                    f"Level Description: {levels[current_level]['description']}"
    }
    message_history.append(message)
    return jsonify({"message": message}), 200



@app.route('/get_data', methods=['POST'])
def get_data():
    global current_level, message_history
    idx_name = "l" + str(current_level) + "-index"
    index = pc.Index(idx_name)

    query_response = index.fetch(
        ids=["vec1", "vec2", "vec3", "vec4", "vec5", "vec6", "vec7", "vec8", "vec9", "vec10"],
        namespace="ns1" 
    )
    result_data = []
    for item_id, vector_data in query_response.vectors.items():
        text = vector_data.metadata.get('text')
        result_data.append({
            'id': item_id,
            'text': text
        })
    return jsonify({'data': result_data})



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
    global current_level, message_history, attempts_tracker
    data = request.get_json()
    user_input = data.get('prompt')
    idx_name = "l" + str(current_level) + "-index"

    if not user_input:
        return jsonify({"error": "No prompt provided"}), 400
    
    if current_level not in attempts_tracker:
        attempts_tracker[current_level] = 0
    attempts_tracker[current_level] += 1
    print(f"Current level: {current_level}")


    message_history.append({"role": "user", "content": user_input})

    for message in message_history:
        #Remove the instructions from the message history, so that the LLM doesn't see whats coming
        if message['role'] == 'system':
            message_history.remove(message)
        if 'role' not in message or 'content' not in message:
            print(f"Invalid message format: {message}")
            
    message_history.append(system_prompt)
    if current_level > 2:
        index = pc.Index(idx_name)
        query_embedding = get_embedding(user_input)
        #Get the top match from the DB
        pinecone_results = index.query(query_embedding, top_k=1, include_metadata=True, namespace="ns1")
        context = "\n".join([match["metadata"].get("text", "") for match in pinecone_results["matches"]])

        if context:
            message_history.append({"role": "system", "content": context})

    dg = DataGraph(attempts_tracker)
    dg.save_attempts()

    print("Beginning message history:")
    for message in message_history:
        print(message)
    print("End of message history")

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=message_history,
        max_tokens=150,
    )

    gpt_response = response.choices[0].message.content
    success = any(keyword in gpt_response.lower() for keyword in levels[current_level]["success_keywords"])
    success_msg = "Congratulations! You have completed the level."

    formatted_response = gpt_response
    final_message = ""
    response_data = {
        "message": gpt_response,
        "success": success
    }

    dg = DataGraph(attempts_tracker)
    dg.save_attempts()

    if success: 
        levels[current_level]["completed"] = True
        current_level_data = levels[current_level]
        response_data["level_complete"] = True
        response_data["vulnerability_type"] = current_level_data["type"]
        response_data["difficulty"] = current_level_data["difficulty"]
        response_data["examples"] = current_level_data["examples"]
    
        incomplete_levels = []
        success_msg += '<span style="color: green;"><br> Congratulations! You have completed the level.<br> Levels left to complete:<br>'
        for level in levels:                
            if not levels[level]["completed"]:
                incomplete_levels.append(level)
                success_msg += f'{level}<br>'
        success_msg += '</span>'

        if not incomplete_levels:
            response_data["trigger_end_quiz"] = True
            response_data["game_complete"] = True

        final_message = formatted_response + "\n\n" + success_msg
    else:
        failure_msg = "\n\nYour attempt was unsuccessful. Please try again."
        final_message = formatted_response + failure_msg
    dg.plot_attempts()

    return jsonify({
        "message": final_message, 
        "success": success,
        "game_complete": response_data.get("game_complete", False),
        "trigger_end_quiz": response_data.get("trigger_end_quiz", False)
    })

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5139)