import uuid
import streamlit as st
from backend import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage, AIMessage

# '''
# TASK:

# 1. Add a sidebar with title, a start chat button and a title named 'My Conversations'
# 2. Generate dynamic thread ID and add it to the session
# 3. Display the thread ID in the sidebar

# ---------------------------------------------------------------

# 4. Add a new chat button
# 5. On click of new chat, open a new chat window
#     * Generate a new thread_id
#     * Save it in session
#     * Reset message history

# ----------------------------------------------------------------

# 6. Create a list to store all thread_id's
# 7. Load all the thread ids in the sidebar
# 8. Convert the side bar text to clickable buttons.

# -----------------------------------------------------------------

# 9. On click of a particular thread id load that particular conversation

# '''


# Utility functions

def generate_thread_id():
    return uuid.uuid4()


def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []


def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)


def load_conversations(thread_id):
    state = chatbot.get_state(
        {'configurable': {'thread_id': thread_id}}
    ).values
    if 'messages' not in state:
        return []
    return state['messages']


# Session Setup
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()

add_thread(st.session_state['thread_id'])


# Sidebar UI
st.sidebar.title('LangGraph Chatbot')
if st.sidebar.button('New chat'):
    reset_chat()
st.sidebar.header('My conversations')

for thread_id in st.session_state['chat_threads']:
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversations(thread_id)
        temp_messages = []

        for message in messages:
            if isinstance(message, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'
            temp_messages.append({'role': role, 'content': message.content})

        st.session_state['message_history'] = temp_messages


CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}


# Chat

# Loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here')

if user_input:
    # First add the message to message_history
    st.session_state['message_history'].append(
        {'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # First add the message to message_history
    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            )
        )
    st.session_state['message_history'].append(
        {'role': 'assistant', 'content': ai_message})
