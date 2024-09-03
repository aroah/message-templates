import streamlit as st

from openai import OpenAI # used to access openai api
import json # used to create a json to store snippets and embeddings
from numpy import dot # used to match user questions with snipp
import requests

openai_token = st.secrets["OPENAI_KEY"] # replace this with your openai api key or store the api key in env

GPT_MODEL = "gpt-3.5-turbo" # gpt model used. alternatively you can use gpt-4 or other models.

gpt_endpoint = "https://api.openai.com/v1/chat/completions"

def get_response_from_gpt(context, prompt, timeout_parameter=30):
    gpt_response=""

    params = {"model": "gpt-4o-mini", "temperature":0, "messages":[{"role": "user", "content": prompt + context}]}
    try:
        # Call the OpenAI GPT API to generate a location answer
        # Set the request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer "+ openai_token
        }
        # Set parameters
        # Send the API request
        response = requests.post(gpt_endpoint, headers=headers, data=json.dumps(params), timeout=timeout_parameter)
        gpt_response = response.json()
        return gpt_response
    except Exception as er:
        return str(er)


def rewrite_message_with_gpt(context):
    gpt_response = ""
    prompt = "rewrite message that avoids any references to SHAFT - Sex, Hate, Alcohol, Firearms, and Tobacco  words "


    try:
        gpt_response = get_response_from_gpt(context, prompt)

        if 'choices' in gpt_response:
            rewritten_message = str(gpt_response['choices'][0]['message']['content']).replace("\n", "")
            return rewritten_message
        else: 
            return "gpt error"
    except Exception as er:
            return str(er)

    return gpt_response 
                
def detect_SHAFT_violation(context):
    sanitized_message = ""
    prompt = "Does this message contain any SHAFT - Sex, Hate, Alcohol, Firearms, and Tobacco words? Respond with 1 word - yes or no."
    response = get_response_from_gpt(context, prompt)
    if 'choices' in response:
        is_shaft_message = str(response['choices'][0]['message']['content']).lower().replace("\n", "")
        if is_shaft_message=='yes':
                sanitized_message = rewrite_message_with_gpt(context)
                return "yes", sanitized_message
        else: 
                return "no", context    


    

# Streamlit app interface
st.title('Sanitize my message')
st.info("Disclaimer: This is a Minimum Viable Product (MVP) built in a few hours and is provided 'as-is' for testing and feedback purposes only. It may contain bugs, errors, or incomplete features.")
#question = """JACKSONVILLE BEACH, Fla. - Flyers for "Drunk Day at the Beach" drew hundreds of young people to Jacksonville Beach on Sunday before the three separate shootings that left three people injured and one person dead. People at the beach report multiple guns were used in the shootings at jacksonville beach during busy St. Patrick's Day """
st.markdown(
    """
    <style>
    .stTextArea [data-baseweb=base-input] {
        background-image: linear-gradient(140deg, rgb(159, 205, 246) 0%, rgb(136, 131, 171) 80%, rgb(62, 131, 220) 99%);
        -webkit-text-fill-color: black; 
    }
    </style>
    """,
    unsafe_allow_html=True,
)
message = st.text_area("Enter the message you wish to check")

if message:
    SHAFT_words_in_message, sanitized_message = detect_SHAFT_violation(message)
    if SHAFT_words_in_message == "yes":
        st.warning("We detected some references to SHAFT - Sex, Hate, Alcohol, Firearms, and Tobacco words. There are restrictions on content that could be deemed offensive when sending text messages via carriers or messaging platforms. We have sanitized your message to avoid penalties or your message being blocked by carriers.")
        st.subheader("Original message")
        st.write(f"{message}")
        st.subheader("We have sanitized your message")
        st.write(f"{sanitized_message}")
    else:
        st.info("Your original message does not have any SHAFT- Sex, Hate, Alcohol, Firearms, and Tobacco words.")
        st.subheader("Original message")
        st.write(f"{message}")   
