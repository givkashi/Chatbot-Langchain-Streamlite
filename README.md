# Chatbot with Streamlit, LangChain, and SQLite <a href="https://medium.com/@givkashi/building-an-intelligent-chatbot-with-streamlit-langchain-and-sqlite-70236e0e9e76" target="blank"><img align="center" src="https://raw.githubusercontent.com/rahuldkjain/github-profile-readme-generator/master/src/images/icons/Social/medium.svg" alt="@_giaabaoo_" height="30" width="40" /></a>

Welcome to the Chatbot repository! This project demonstrates how to build an intelligent chatbot using Streamlit, LangChain, and SQLite. The chatbot provides real-time responses and allows users to manage and retrieve past conversations.

<img src="https://github.com/givkashi/Chatbot-Langchain-Streamlite/blob/main/img.png" width="70%" height="70%"/>

## Features

- **Interactive UI**: Built with Streamlit for a user-friendly interface.
- **Conversation Management**: Stores and retrieves past conversations using SQLite.
- **Advanced Language Model**: Utilizes LangChain for conversational AI tasks.
- **Real-time Responses**: Provides instant replies to user queries.

## Installation

To get started with the project, follow these steps:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/givkashi/Chatbot-Langchain-Streamlite.git
    cd chatbot-streamlit-langchain-sqlite
    ```

2. **Install the required libraries**:
    ```bash
    pip install streamlit sqlite3 langchain
    ```

3. **Set up the environment**:
    - Obtain an API key for LangChain.
    - Replace the placeholder `"..."` in the code with your actual API key.

## Usage

1. **Run the Streamlit app**:
    ```bash
    streamlit run app.py
    ```

2. **Interact with the chatbot**:
    - Open the app in your browser.
    - Use the sidebar to start a new conversation or load a past conversation.
    - Type your messages in the input field and receive real-time responses from the chatbot.

## Code Overview

The project consists of a single `app.py` file that contains all the necessary code.

### Initializing the Conversation Model

The LangChain library is used to set up the conversation model. A buffer memory is used to maintain the context of the conversation.

```python
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

# Initialize the conversation chain
llm = ChatOpenAI(api_key="...")
memory = ConversationBufferMemory()
conversation = ConversationChain(llm=llm, memory=memory)
```

### Setting Up SQLite Database

SQLite is used to store conversation histories and messages. The database schema consists of two tables: `conversations` and `messages`.

```python
import sqlite3

# Initialize SQLite database
conn = sqlite3.connect('conversations.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')
c.execute('''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    sender TEXT,
    message TEXT,
    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
)
''')
conn.commit()
```

### Functions to Manage Conversations

Helper functions are provided to save conversations and messages to the database, and to delete conversations.

```python
# Function to save conversation and message to the database
def save_conversation(topic):
    c.execute('''
    INSERT INTO conversations (topic)
    VALUES (?)
    ''', (topic,))
    conn.commit()
    return c.lastrowid

def save_message(conversation_id, sender, message):
    c.execute('''
    INSERT INTO messages (conversation_id, sender, message)
    VALUES (?, ?, ?)
    ''', (conversation_id, sender, message))
    conn.commit()

# Function to delete a conversation
def delete_conversation(conversation_id):
    c.execute('DELETE FROM messages WHERE conversation_id = ?', (conversation_id,))
    c.execute('DELETE FROM conversations WHERE id = ?', (conversation_id,))
    conn.commit()
```

### Building the Streamlit UI

The Streamlit UI is set up to provide an interactive interface for the chatbot. The sidebar displays past conversations and allows users to start new ones or delete existing ones.

```python
import streamlit as st

# Streamlit UI setup
st.set_page_config(page_title="Chatbot", layout="wide")
st.title("Chatbot UI")

# Sidebar for past conversations
st.sidebar.header("Conversation History")

# Start new conversation
new_conversation = st.sidebar.text_input("New Conversation Topic")
if st.sidebar.button("Start New Conversation"):
    if new_conversation:
        conversation_id = save_conversation(new_conversation)
        st.session_state.conversation_id = conversation_id
        st.session_state.topic = new_conversation
        st.session_state.messages = []

# Delete conversation
conversation_to_delete = st.sidebar.selectbox("Select Conversation to Delete", [None] + [row[0] for row in c.execute('SELECT topic FROM conversations').fetchall()])
if st.sidebar.button("Delete Selected Conversation"):
    if conversation_to_delete:
        conversation_id_to_delete = c.execute('SELECT id FROM conversations WHERE topic = ?', (conversation_to_delete,)).fetchone()[0]
        delete_conversation(conversation_id_to_delete)

# Display past conversations
past_conversations = c.execute('SELECT id, topic, timestamp FROM conversations ORDER BY timestamp DESC').fetchall()
for conversation_id, topic, timestamp in past_conversations:
    st.sidebar.write(f"**{timestamp}**")
    st.sidebar.write(f"**Topic:** {topic}")
    st.sidebar.write("---")

    if st.sidebar.button(f"Load {topic}", key=f"load_{conversation_id}"):
        st.session_state.conversation_id = conversation_id
        st.session_state.topic = topic
        st.session_state.messages = c.execute('SELECT sender, message FROM messages WHERE conversation_id = ? ORDER BY timestamp', (conversation_id,)).fetchall()
```

### Main Chat Area

The main chat area allows users to interact with the chatbot and displays the conversation history.

```python
# Main chat area
if 'conversation_id' not in st.session_state:
    st.session_state.conversation_id = None
    st.session_state.topic = None
    st.session_state.messages = []

if st.session_state.conversation_id:
    st.header(f"Topic: {st.session_state.topic}")
    user_input = st.text_input("You: ", key="input")

    if st.button("Send"):
        if user_input:
            bot_response = conversation.predict(input=user_input)
            save_message(st.session_state.conversation_id, "User", user_input)
            save_message(st.session_state.conversation_id, "Bot", bot_response)
            st.session_state.messages.append(("User", user_input))
            st.session_state.messages.append(("Bot", bot_response))
            user_input = ""

    # Display the chat history
    st.header("Conversation")
    for sender, message in st.session_state.messages:
        st.write(f"**{sender}:** {message}")
        st.write("---")
else:
    st.header("Start a new conversation or select an existing one from the sidebar.")
```

