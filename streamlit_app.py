import streamlit as st
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
import uuid
import os
import random


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
        session_id = str(random.randint(100000, 999999))
        agent_id = 'F9JRBHFNPU'
        agent_alias_id = 'KS59ZQYFEJ'
        response = invoke_bedrock_agent(client, agent_id, agent_alias_id, prompt, session_id)

        if response:
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
