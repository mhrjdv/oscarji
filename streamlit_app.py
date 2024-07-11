import streamlit as st
import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import json

# Initialize the AWS client
def initialize_bedrock_client():
    try:
        client = boto3.client(
            'bedrock-agent-runtime',
            st.write("aws_access_key_id", st.secrets["aws_access_key_id"])
            st.write("aws_secret_access_key", st.secrets["aws_secret_access_key"])
            region_name='us-east-1',

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
            inputText=input_text,
        )

        completion = ""
        for event in response['completion']:
            chunk = event['chunk']
            completion += chunk['bytes'].decode()

        return completion
    except Exception as e:
        st.error(f"Error calling the agent: {e}")
        return None

# Streamlit app
def main():
    st.title("AWS Bedrock Agent with Streamlit")

    input_text = st.text_area("Enter your text input:", height=200)

    if st.button("Submit"):
        client = initialize_bedrock_client()
        if client:
            session_id = "10"
            agent_id = "F9JRBHFNPU"
            agent_alias_id = "KS59ZQYFEJ"
            result = invoke_bedrock_agent(client, agent_id, agent_alias_id, input_text, session_id)
            if result:
                st.write("Agent Response:")
                st.write(result)

if __name__ == "__main__":
    main()
