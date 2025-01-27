import openai
from dotenv import load_dotenv


load_dotenv()

# You'll need to put your own key
openai.api_key_path = 'key.txt'


def chat_with_gpt():
    print("Welcome to the  Game!")
    print("Type 'exit' to end the game.\n")


    system_prompt = {
        "role": "system",
        "content": "You are a creative and immersive game master for a text-based adventure game. Respond as a narrator. Keep responses concise and engaging."
    }


    message_history = [system_prompt]

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Thanks for playing! Goodbye!")
            break

        message_history.append({"role": "user", "content": user_input})

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=message_history,
                max_tokens=150,
            )

            gpt_response = response['choices'][0]['message']['content']
            print(f"Game: {gpt_response}")

            message_history.append({"role": "assistant", "content": gpt_response})

        except Exception as e:
            print(f"An error occurred: {e}")
            break


if __name__ == "__main__":
    chat_with_gpt()
