import streamlit as st
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
import uuid
import os
import random
import time

# Initialize the AWS Bedrock Runtime client
def initialize_bedrock_client():
    try:
        client = boto3.client(
            'bedrock-agent-runtime',
            aws_access_key_id = st.secrets["aws_access_key_id"],
            aws_secret_access_key = st.secrets["aws_secret_access_key"],
            region_name='us-east-1'
        )
        return client
    except NoCredentialsError:
        st.error("Credentials not available")
        return None
    except PartialCredentialsError:
        st.error("Incomplete credentials")
        return None

# Function to call your AWS Bedrock agent
def invoke_bedrock_agent(client, agent_id, agent_alias_id, input_text, session_id):
    try:
        response = client.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText=input_text
        )

        completion = ""
        for event in response['completion']:
            chunk = event['chunk']
            completion += chunk['bytes'].decode()

        return completion
    except ClientError as e:
        st.error(f"Couldn't invoke agent: {e}")
        return None

# Streamlit app
st.title("Chat with OSCAR: Oneapp Smart Companion and Advisor")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("You:"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Initialize Bedrock client and get response
    client = initialize_bedrock_client()
    if client:
        session_id = str(random.randint(100000, 999999))  # Generate a random 6-digit session ID
        agent_id = 'JLOADNTHHV'
        agent_alias_id = 'QN5XHU3UCC'

        response_container = st.empty()  # Create an empty container for streaming response
        partial_response = ""  # Variable to hold partial response
        
        with st.spinner("Waiting for response..."):  # Add spinner here
            response = invoke_bedrock_agent(client, agent_id, agent_alias_id, prompt, session_id)

        if response:
            # Simulate streaming by progressively displaying the response
            chunk_size = 2  # Smaller chunk size for smoother streaming
            delay = 0.02  # Shorter delay for smoother streaming
            for i in range(0, len(response), chunk_size):
                partial_response = response[:i+chunk_size]
                response_container.markdown(partial_response)
                time.sleep(delay)  # Simulate delay for streaming effect

            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
