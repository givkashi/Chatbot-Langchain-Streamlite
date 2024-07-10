import streamlit as st
import sqlite3
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

# Initialize the conversation chain
llm = ChatOpenAI(api_key="...")
memory = ConversationBufferMemory()
conversation = ConversationChain(llm=llm, memory=memory)

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
