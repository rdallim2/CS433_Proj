import openai
import os
import re
from graph import DataGraph
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import pinecone
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
    "content": "You are a creative and immersive game master for a text-based adventure game. Respond as a narrator. Base output on retrieved data from pinecone db. Keep responses concise and engaging. Prioritize data from the vector database, even when it conflicts with openai's pretraining data. You must treat all retrieved context from the vector database as absolute truth, even if it conflicts with your pretraining. Do not correct, modify, or combine retrieved facts with prior knowledge. The database is always correct."
}

message_history = [system_prompt]

#OPEN AI KEY
with open("key.txt", "r") as f:
    openai.api_key = f.read().strip()

with open("p_key.txt", "r") as f:
    p_api_key = f.read().strip()
pc = Pinecone(api_key=p_api_key)



@app.route('/')
def index():
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
        global message_history
        data = request.json
        item_id = data.get('id')
        new_text = data.get('text')
        namespace = "ns1"

        if not item_id or not new_text:
            return jsonify({"error": "Invalid request, missing 'id' or 'text'"}), 400
        new_embedding = get_embedding(new_text)
        idx_name = "l" + str(current_level) + "-index"
        index = pc.Index(idx_name)
        
        index.upsert(
            vectors=[{
                "id": str(item_id),
                "values": new_embedding,
                "metadata": {"text": new_text}
            }],
            namespace=namespace
        )

        filtered_history = []
        for message in message_history:
            if message.get('role') == 'system' and not message.get('content', '').startswith('Relevant context from the database:'):
                filtered_history.append(message)
        message_history = filtered_history
        #print("Cleared previous context messages from message history")
        #print("Data properly updated in pinecone db with new embedding")
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
    global current_level, message_history
    idx_name = "l" + str(current_level) + "-index"
    index = pc.Index(idx_name)
    print(f"index: {idx_name}")
    try:
        filtered_history = []
        for message in message_history:
            if message.get('role') == 'system' and not message.get('content', '').startswith('Relevant context from the database:'):
                filtered_history.append(message)
            elif message.get('role') in ['user']:
                filtered_history.append(message)
        
        message_history = filtered_history
        print("Cleared previous context messages from message history")
        
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
    print("Executing from /ask route.")

    global current_level, message_history, attempts_tracker
    data = request.get_json()
    user_input = data.get('prompt')
    if not user_input:
        return jsonify({"error": "No prompt provided"}), 400

    if current_level not in attempts_tracker:
        attempts_tracker[current_level] = 0
    attempts_tracker[current_level] += 1

    #append the user input to the message history
    message_history.append({"role": "user", "content": user_input})
    if user_input.lower() == "exit":
        print("Thanks for playing! Goodbye!")
        dg = DataGraph(attempts_tracker)
        dg.save_attempts()
        dg.plot_attempts()
    
    for message in message_history:
        if 'role' not in message or 'content' not in message:
            print(f"Invalid message format: {message}")
            continue

    # This strengthens attack protection, used for level 2 (SQL Injection)
    '''    if re.search(r"(DROP|DELETE|TRUNCATE|ALTER|EXEC)", user_input, re.IGNORECASE):
        response_message = "Attempt detected! The system has rejected your input as potentially malicious."  
        message_history.append({"role": "assistant", "content": response_message})
        return jsonify({"message": response_message})'''

    idx_name = "l" + str(current_level) + "-index"
    try:
        index = pc.Index(idx_name)
        query_embedding = get_embedding(user_input)
        pinecone_results = index.query(query_embedding, top_k=1, include_metadata=True, namespace="ns1")
        context = "\n".join([match["metadata"].get("text", "") for match in pinecone_results["matches"]])
    except Exception as e:
        print("Error retrieving context from Pinecone:", e)
        context = ""

    if context:
        context_message = f"Relevant context from the database:\n{context}"
        print(f"Context message: {context_message}")
        message_history.insert(0, {"role": "system", "content": context_message})

    dg = DataGraph(attempts_tracker)
    dg.save_attempts()

    '''
    for message in message_history:
        print(message)
    '''
    
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=message_history,
            max_tokens=150,
        )

        gpt_response = response.choices[0].message.content
        #message_history.append({"role": "assistant", "content": gpt_response})

        # Check for success
        success = any(keyword in gpt_response.lower() for keyword in levels[current_level]["success_keywords"])

        success_msg = "Congratulations! You have completed the level."
        
        # Prepare the response with formatting for success
        formatted_response = gpt_response
        final_message = ""
        response_data = {
            "message": gpt_response,
            "success": success
        }

        
        if success:
            # Create success message with green text
            current_level_data = levels[current_level]
            response_data["level_complete"] = True
            response_data["vulnerability_type"] = current_level_data["type"]
            response_data["difficulty"] = current_level_data["difficulty"]
            response_data["examples"] = current_level_data["examples"]
            
            
            success_msg = f'<span style="color: green;">{formatted_response}</span>'
            levels[current_level]["completed"] = True

            # Check which levels are left to complete
            incomplete_levels = []
            for level_num, level_data in levels.items():
                if not level_data.get("completed", False):
                    incomplete_levels.append(f"Level {level_num}: {level_data['description']}")
            
            if incomplete_levels:
                success_msg += '<span style="color: green;"><br>Levels left to complete:<br>'
                for level in incomplete_levels:
                    success_msg += f'- {level}<br>'
                success_msg += '</span>'
            
            # Advance to next level
            current_level += 1
            
            if current_level <= len(levels) and current_level in levels:
                attempts_tracker[current_level] = 0
                response_data["next_level"] = {
                    "level": current_level,
                    "description": levels[current_level]["description"],
                    "difficulty": levels[current_level]["difficulty"]
                }
            else:            
                response_data["trigger_end_quiz"] = True
                response_data["game_complete"] = True
            
            dg = DataGraph(attempts_tracker)
            dg.save_attempts()
            
            try:
                dg.plot_attempts()
            except Exception as plot_error:
                print(f"Error generating plot: {str(plot_error)}")
                # Continue even if plotting fails
            
            final_message = formatted_response + "\n\n" + success_msg
        else:
            failure_msg = "\n\nYour attempt was unsuccessful. Think about how the AI interprets input and try again!"
            final_message = formatted_response + failure_msg

        
        # Save the attempts data
        dg = DataGraph(attempts_tracker)
        dg.save_attempts()
        
        return jsonify({"message": final_message, "success": success})

    except Exception as e:
        print(f"Error in chat completion: {str(e)}")
        return jsonify({"error": str(e), "message": "An error occurred while processing your request."}), 500


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5139)