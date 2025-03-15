# DP-433
The motivation behind this project is to educate users on the possible vulnerabilities that arise from large language models (LLMs) by demonstrating various types of data poisoning attacks in a controlled environment. By interacting with the system, users will gain hands-on experience with techniques like backdoor attacks, data corruption, and prompt injections. As they progress through different levels, they will experience a variety of simulated attacks and gain knowledge of what each attack does. This project aims to raise awareness and promote better security practices in AI usage, training, and deployment. 

## Features
The user is tasked with completeing 6 levels with increasing level of difficulty: 
1. Prompt Injection
2. SQL Injection
3. Label Flipping
4. Backdoor Attack
5. Data Poisoning
6. Data Poisoning with Backdoor

Real-Time AI Interaction: User is able to engage with a GPT-3.5 AI that responds to player input

Challenges: Test and learn about different attack scenarios on AI models

Data modification: In later levels the user is able to retrieve, edit, and manipulate stored embeddings through the use of Pinecone integration

## Technical Requirements
### **Backend**:

- Python: Our core language for backend development. Python libraries include: 
    -   Matplotlib
    -   dotenv
    -   re
    -   time
    -   json

- Flask: Handles the HTTP requests and is the webframework

- Pinecone: Fully managed vector database that stores and retrieved embeddings for the AI

- OpenAI GPT-3.5: Provides the AI-generated outputs 
### **Front End**:
- HTML, CSS, JavaScript: Provides the interactive UI
### **Platform Support**: 
- Compatible with MacOS and Windows devices
## Installation Instructions

1. Clone the repository
     ```bash
    git clone    https://github.com/rdallim2/CS433_Proj.git
    cd ./CS433_proj
    ```
2. Install dependencies
    ```bash
    pip install -r requirements.txt
    ```
3. Set up OpenAI API key:
    - Navigate to https://openai.com/
    - Log into your API platform account
    - Open settings and under the Organization tab click API keys
    - Click the button "Create new secret key" and fill out the information
    - Click create secret key
    - Copy the key and put it into a text document called **"key.txt"**
4. Set up Pinecone API key:
    - Navigate to https://www.pinecone.io/
    - Log into your aacount
    - Click the API keys tab and then click the "Create API Key" button
    - Fill out the information and click "Create key"
    - Copy the key and put it into a text document called **"p_key.txt"**
5. Run the application
    ```bash
     python app.py
    ```



## Using the Game
To use the game:
1. Open a web browser and navigate to http://localhost:5139/

2. Complete an initial assessment quiz

3. Select a level and interact with the AI to execute different data poisoning attacks

4. Progress through all the levels

5. Complete the post assessment quiz



## Directory Structure


```bash
.
├── .idea/
├──  __pychache__/
├── quiz_answers/
├── static/
|       ├── script.js
|       └── styles.cc
├── templates/
|       └── index.html
├── README.md
├── gitignore
├── app.py
├── attempts.json
├── embeddings_data.py
├── gpt3.5
├── graph.py
├── levels.py
├── p_db.py
├── p_db_functions.py
└── pinecone_test.py

```
## Challenges
One of the biggest challenges we faced during this project was a lack of previous knowledge on data poisoning attacks. It is a complex topic that previous classes have not discussed. Thus, we spent a large portion of the term researching the topic by reading academic papers and watching informational videos.

Additionally, it took some time to find the perfect Large Language Model for our project. We first used experimented with a few different pre-built models from hugging face and other services, before eventually deciding to go with OpenAI's GPT-3.5 turbo. Though the model is not free to use, its cost of three dollars per one million tokens is very reasonable for our uses. We found this model to be our best option after seeing that many of the cheaper options, such as GPT-2.0, often weren’t able to provide relevant or helpful output, often outputting what seemed to be quotes from sections of text somewhat related to the question prompted to the model.

## Future Improvements
In the future we plan to introduce additional levels that are more complex attack scenarios. Possibly also moving beyond data poisoning attacks and teaching the user different cybersecurity topics involving AI.

In addition, we would like to enhance the research methodology. Future studies should aim to expand the testing to further validate the findings of this evaluation. To achieve this, a larger and more diverse sample of at least 50 participants should be recruited, ensuring greater representation across different backgrounds, age groups, education levels, and technical knowledge. This change would improve the generalizability of the result and reduce biases that exist in the current sample. This experiment would utilize the between-subject experimental design where the subjects are randomly split into two groups. One group would be assigned to learning about data poisoning attacks through the game, while the other group would be taught using the traditional lecture-based approach. Both groups would complete an identical pre-assessment quiz to evaluate their prior knowledge, followed by a post-assessment to measure their learning after the experiment. Additionally, the quiz would also be expanded with more questions to gain a deeper understanding of the learning process. This enhanced methodology would provide stronger evidence regarding the effectiveness of game-based learning compared to conventional teaching methods in regard to cybersecurity.  

## Credits
Developed by Ryan Dallimore and Amelia Bates 

Project requirements were defined by Professor Jun Li

Inspired by Lakera's game titled "Gandalf"
