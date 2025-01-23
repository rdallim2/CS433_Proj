import os
from huggingface_hub import hf_hub_download
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

#Set your own environment variable- generate a key at huggingface
HUGGING_FACE_API_KEY = os.getenv('HUGGING_FACE_API_KEY')

#Can plug in different models in this spot, this one produces pretty poor output but is easy to run on the laptop. Just a start. 
model_id = "openai-community/gpt2"

tokenizer = AutoTokenizer.from_pretrained(model_id, legacy=False)
model = AutoModelForCausalLM.from_pretrained(model_id)

generator = pipeline("text-generation", model=model, device=-1, tokenizer=tokenizer, max_length=1000)
while True:
    # Get user input
    user_input = input("You: ")

    # Break the loop if user types 'exit'
    if user_input.lower() == "exit":
        print("Goodbye!")
        break

    # Generate a response from GPT-2
    response = generator(user_input, max_length=100, num_return_sequences=1, pad_token_id=50256)
    
    # Display the model's response
    print("GPT-2: " + response[0]['generated_text'][len(user_input):].strip())
