import streamlit as st
import pandas as pd
import time
import os
import openai
import json

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_all_states():
    df = pd.read_csv('data/all-states.csv')
    return df.apply(lambda x: x['name'] + ' (' + x['country_name'] + ')', axis=1).to_list()
    
def load_languages():
    messages=[
        {
            "role": "system",
            "content": "Your task is to list down all the major languages spoken in the given locations in the last 80 years. \n\n[step 1]\nFor each location include the top 5 local, regional, national, and international languages popularly spoken in the given locations.\n\n[step 2]\nInclude the estimated percentage of people who may speak the given language in the given locations. Do it for each of the locations.\n\n[Step 3]\nReturn the response in the following JSON format:\n\n[ \n  {\n    language: language_name, \n    population: 10%,\n    location: location_name\n  }\n ]\n\nPlease ensure that the response is strictly in the format shared above"
        },
        {
            "role": "user",
            "content": "Locations: " + ', '.join(st.session_state['locations'])
        }
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = messages,
        temperature = 0,
        max_tokens = 512,
        top_p = 1,
        frequency_penalty = 0,
        presence_penalty = 0
    )
    st.write(response.choices[0].message.content)
    try:
        original_list = json.loads(response.choices[0].message.content)
        st.session_state['languages'] = list(set(map(lambda x: x['language'], original_list)))
    except Exception as err:
        st.write(err)


def load_genres():
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
        temperature=1,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    # st.write(response.choices[0].message.content)
    st.session_state['genres'] = json.loads(response.choices[0].message.content)

def load_artists():
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Your task is to predict some music artists that a given person may like.\n\nYou will be provided details such as genres of choice, the languages spoken by the person, and the cut-off year.\n\nHere is how you can find singers and music composers.\n\n[Step 1]: Create combinations of language and genres\n\n[Step 2]: For each language-genre pair, find up to  15 singers and composers who gave the maximum number of hit songs till the given year. Please ensure that you're considering artists from the start year till the cut-off year.\n\nFor each artist also include the year of their first major hit song.\n\nPrint the step 2 response in the following JSON format:\n\n[\n  {\n    \"glp\": \"genre-language-pair-name\",\n    \"artists\": [\n       { \"n\": \"name of the artist\", \"f\": year_of_first_hit}\n    ]\n  }\n]"
            },
            {
                "role": "user",
                "content": "Genres: Bollywood, Ghazals, Kumaoni Folk Music, Devotional Music\nLanguages: Hindi, Kumaoni\nCut-Off Year: 2010\nStart Year: 1910"
            }
        ],
        temperature=1,
        max_tokens=2900,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    st.write(response.choices[0].message.content)

def on_language_checkbox_change():
    pass

def main():
    st.write(os.environ)
    left, right = st.columns(2)
    with left:
        st.text_input('Identifier', key='profile_name')
        st.number_input('Age', key='profile_age', step=1, min_value=40, max_value=120)
        st.multiselect(label='Locations', options=get_all_states(), key='locations')

        st.button('Load Language Suggestions', on_click=load_languages)
        if 'languages' in st.session_state:
            if 'profile_languages' not in st.session_state:
                        st.session_state['profile_languages'] = set([])
            for (idx, language) in enumerate(st.session_state['languages']):
                if st.checkbox(language) == True:
                    st.session_state['profile_languages'].add(language)
                elif language in st.session_state['profile_languages']:
                    st.session_state['profile_languages'].remove(language)
        
        st.button('Load Genres', on_click=load_genres)
        if 'genres' in st.session_state:
            if 'profile_genres' not in st.session_state:
                        st.session_state['profile_genres'] = set([])
            for (idx, genre) in enumerate(st.session_state['genres']):
                if st.checkbox(genre) == True:
                    st.session_state['profile_genres'].add(genre)
                elif genre in st.session_state['profile_genres']:
                    st.session_state['profile_genres'].remove(genre)

        st.button('Load Artists', on_click=load_artists)
        if 'artists' in st.session_state:
            if 'profile_artists' not in st.session_state:
                        st.session_state['profile_artists'] = set([])
            for (idx, artist) in enumerate(st.session_state['artists']):
                if st.checkbox(artist) == True:
                    st.session_state['profile_artists'].add(artist)
                elif artist in st.session_state['profile_artists']:
                    st.session_state['profile_artists'].remove(artist)
        
        # st.write(get_all_states())

        # location = st.text_input('Location', key='location', on_change=show_filtered_results)

        # if st.session_state['location'] and len(st.session_state['location_results']) > 0:
        #     for (idx, result) in enumerate(st.session_state['location_results']):
        #         if st.button(result):
        #             if 'locations' not in st.session_state:
        #                 st.session_state['locations'] = set([])
        #             st.session_state['locations'].add(result)
    with right:
        st.write(st.session_state)