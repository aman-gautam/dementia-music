import streamlit as st
import datetime
from services.llm import openai
import json

def load_artists(errors):
    yob = datetime.date.today().year - st.session_state['profile_age']
    cut_off_year = yob + 50 if st.session_state['profile_age'] > 50 else st.session_state['profile_age']
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Your task is to predict some music artists that a given person may like.\n\nYou will be provided details such as genres of choice, the languages spoken by the person, and the cut-off year.\n\nHere is how you can find singers and music composers.\n\n[Step 1]: Create combinations of language and genres\n\n[Step 2]: For each language-genre pair, find up to  15 singers and composers who gave the maximum number of hit songs till the given year. Please ensure that you're considering artists from the start year till the cut-off year.\n\nFor each artist also include the year of their first major hit song.\n\nPrint the step 2 response in the following JSON format:\n\n[\n  {\n    \"glp\": \"genre-language-pair-name\",\n    \"artists\": [\n       { \"n\": \"name of the artist\", \"f\": year_of_first_hit}\n    ]\n  }\n]"
            },
            {
                "role": "user",
                "content": f"""Genres: {', '.join(st.session_state['profile_genres'])}
                Languages: {', '.join(st.session_state['profile_languages'])}
                Cut-Off Year: { cut_off_year }
                Start Year: { yob - 30 }"""
            }
        ],
        temperature=0,
        max_tokens=3000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    st.write(response.choices[0].message.content)
    try:
        st.session_state['artists'] = json.loads(response.choices[0].message.content)
    except Exception as err:
        st.write(response.choices[0].message.content)
        st.write(err)

 
def add_custom_artist():
    if 'custom_artist' not in st.session_state:
        return

    if 'artists' not in st.session_state:
        st.session_state['artists'] = []
    
    if 'profile_artists' not in st.session_state:
        st.session_state['profile_artists'] = set()
    
    # find custom glp
    custom_glp = list(filter(lambda x: x['glp'] == 'Custom', st.session_state['artists']))
    if not custom_glp:
        st.session_state['artists'].append({
            'glp': 'Custom',
            'artists': [
                {
                    'n': st.session_state['custom_artist'],
                    'f': 2023 # placeholder
                }
            ]
        })
    else:
        custom_glp['artists'].append({
            'n': st.session_state['custom_artist'],
            'f': 2023 # placeholder
        })
    st.session_state['profile_artists'].add(st.session_state['custom_artist'])
    st.session_state['custom_artist'] = ''
