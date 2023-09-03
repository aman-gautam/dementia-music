import json
from services.llm import openai
import streamlit as st

def load_genres(errors):
    locations = ', '.join(st.session_state['locations'])
    languages = ', '.join(st.session_state['profile_languages'])
    age = st.session_state['profile_age']
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                      "content": "Your task is to predict the top 15 music genres that a given person may like.\n\nYou will be provided details such as the age of the person, locations in which the person has lived, and the languages spoken by the person. \n\nInclude music genres that were famous in the specified years as well. \n\nYour response should be as a JSON in the following format\n\n[ \n    // list of genres\n ]"
            },
            {
                "role": "user",
                "content": f"""
                    Locations: {locations}
                    Age: {age} years
                    Languages: {languages}
                """
            }
        ],
        temperature=0,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    # st.write(response.choices[0].message.content)
    if 'genres' in st.session_state and type(st.session_state.get('genres') == list):
        st.session_state['genres'].extend(json.loads(response.choices[0].message.content))
    else:
        st.session_state['genres'] = json.loads(response.choices[0].message.content)
    # try:
        
    # except Exception as err:
    #     print(err)



def add_custom_genre():
    if 'custom_genre' not in st.session_state:
        return

    if 'genres' not in st.session_state:
        st.session_state['genres'] = []
    
    if 'profile_genres' not in st.session_state:
        st.session_state['profile_genres'] = set()
    
    st.session_state['genres'].append(st.session_state['custom_genre'])
    st.session_state['profile_genres'].add(st.session_state['custom_genre'])
    st.session_state['custom_genre'] = ''
