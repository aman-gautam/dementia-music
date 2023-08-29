import streamlit as st
import pandas as pd
import time
import os
import openai
import json
import pymongo
from pymongo.server_api import ServerApi

errors = {}
openai.api_key = os.getenv("OPENAI_API_KEY")

mongo_uri = f"mongodb+srv://{os.environ['MONGO_USERNAME']}:{os.environ['MONGO_PASSWORD']}@{os.environ['MONGO_HOST']}"

@st.cache_resource
def init_db_connection():
    return pymongo.MongoClient(
         mongo_uri,
         server_api=ServerApi('1')
    )

mongo_client = init_db_connection()



def get_all_states():
    df = pd.read_csv('data/all-states.csv')
    return df.apply(lambda x: x['name'] + ' (' + x['country_name'] + ')', axis=1).to_list()
    
def load_languages():
    if len(st.session_state['locations']) < 1:
        errors['languages'] = 'You need to select the locations before we can suggest you the languages'
    with st.spinner('Loading'):
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
        try:
            original_list = json.loads(response.choices[0].message.content)
            st.session_state['languages'] = sort_languages(original_list)
            del(errors['languages'])
        except Exception as err:
            st.write(err)

def sort_languages(languages):
    languages.sort(key=lambda x: x['population'], reverse=True)
    _result = []
    for language in languages:
        if language.get('language') not in _result:
            _result.append(language.get('language'))
    return _result

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
    st.session_state['artists'] = json.loads(response.choices[0].message.content)

def on_language_checkbox_change():
    pass

def next_step():
    print('next step')
    if 'step' not in st.session_state:
        st.session_state['step'] = 2
    else:
        st.session_state['step'] = st.session_state['step'] + 1

def add_custom_language():
    if 'languages' not in st.session_state:
        st.session_state['languages'] = []
    
    if 'profile_languages' not in st.session_state:
        st.session_state['profile_languages'] = set()
    
    st.session_state['languages'].append(st.session_state['custom_language'])
    st.session_state['profile_languages'].add(st.session_state['custom_language'])
    st.session_state['custom_language'] = ''
        

def main():
    # st.markdown('<h1 style="text-align:center; font-weight:400;">Setup Patient’s profile</h1>', unsafe_allow_html=True)
    st.header('Setup Profile')
    if 'step' in st.session_state:
        st.progress(st.session_state['step'] * 20)
    else:
        st.progress(20)

    st.markdown("### Step 1 : Basic Information")
    st.markdown("**What is the Name of the patient?**")
    st.text_input(
        'What would you like to call the patient? The value you provide here can be used to search for the patient later', 
        key='profile_name',
        placeholder='Patient Name or Identifier'
    )

    st.markdown("**Age of the patient?**")
    st.number_input('This is used to calculate the approximate year of birth of the patient and help us predict the years in which the patient developed a taste in music.', key='profile_age', step=1, min_value=40, max_value=120)

    st.markdown('**Location**')
    st.multiselect(
        label='Each individual\'s Taste in music is heavily influenced by the places they have lived and traveled. This information is crucial to predict the patient’s preference in music.', 
        options=get_all_states(), 
        key='locations'
    )

    if st.session_state.get('step', 1) == 1:
        st.button('Go to next step', on_click=next_step)

    st.divider()

    if st.session_state.get('step', 1) > 1:
        st.markdown(f"### Step 2 : Language Preferences")

        st.markdown(f'**Languages in which {st.session_state.get("profile_name", "the patient")} listens to music**')
        st.markdown(
            f'Are there any languages from below that {st.session_state.get("profile_name", "the patient")} prefers listening\
            to in music? You can select from below or add a new one in case our predictions missed something. '
        )
        if 'languages' not in st.session_state:
            st.text_input('Add Language', key='custom_language', on_change=add_custom_language)
            if 'languages' in errors:
                st.error(errors['languages'])
            cols = st.columns(3)
            with cols[-1]:
                st.button('Get Suggested Languages', on_click=load_languages, type='primary')
        else:
            cols = st.columns(4)
            if 'profile_languages' not in st.session_state:
                        st.session_state['profile_languages'] = set([])
            for (idx, language) in enumerate(st.session_state['languages']):
                with cols[idx % 4]:
                    if st.checkbox(language) == True:
                        st.session_state['profile_languages'].add(language)
                    elif language in st.session_state['profile_languages']:
                        st.session_state['profile_languages'].remove(language)
            
            if 'languages' in errors:
                st.error(errors['languages'])

            st.text_input('Did we miss some language? Add it here.', key='custom_language', on_change=add_custom_language)

            cols = st.columns(3)
            with cols[-1]:
                st.button('Get Suggested Languages', on_click=load_languages)
            with cols[0]:
                if len(st.session_state.get('profile_languages', [])) > 0:
                    st.button('Go to next step', on_click=next_step, type='primary')
        
        st.divider()

    if st.session_state.get('step', 1) > 2:
        st.markdown(f"### Step 3 : Favorite Genres")

        st.markdown(f'**Languages in which {st.session_state["profile_name"]} listens to music**')
        st.markdown(
            f'Are there any languages from below that {st.session_state["profile_name"]} prefers listening\
            to in music? You can select from below or add a new one in case our predictions missed something. '
        )
        st.button('Load Genres', on_click=load_genres)
        if 'genres' in st.session_state:
            cols = st.columns(4)
            if 'profile_genres' not in st.session_state:
                        st.session_state['profile_genres'] = set([])
            for (idx, genre) in enumerate(st.session_state['genres']):
                with cols[idx % 4]:
                    if st.checkbox(genre) == True:
                        st.session_state['profile_genres'].add(genre)
                    elif genre in st.session_state['profile_genres']:
                        st.session_state['profile_genres'].remove(genre)

    if st.session_state.get('step', 1) > 3:
        st.button('Load Artists', on_click=load_artists)
    

    if 'profile_artists' not in st.session_state:
        st.session_state['profile_artists'] = set()

    if 'artists' in st.session_state:
        all_artists = dict()
        artists = st.session_state['artists']
        for glp in artists:
            _lang = glp['glp'].split('-')[-1]
            for _artist in glp['artists']:
                all_artists[_artist['n']] = _lang
        cols = st.columns(3)
        for (idx, key) in enumerate(all_artists):
            with cols[idx % 3]:
                _label = f"{key} ({all_artists[key]})"
                if st.checkbox(_label) == True:
                    st.session_state['profile_artists'].add(key)
                elif key in st.session_state['profile_artists']:
                    st.session_state['profile_artists'].remove(key)

        # print(all_artists)
        # titles = map(lambda x: x['glp'], st.session_state['artists'])
        # tabs = st.tabs(list(titles))
        # cols = st.columns(4)
        # for (idx, tab) in enumerate(tabs):
        # #     with tab:
        #     for _artist in st.session_state['artists'][idx]['artists']:
        #         if _artist['n'] not in all_artists:
        #             all_artists.add(_artist['n'])
        #             with cols[idx % 4]:
        #                 if st.checkbox(_artist['n']) == True:
        #                     st.session_state['profile_artists'].add(_artist['n'])
        #                 elif _artist['n'] in st.session_state['profile_artists']:
        #                     st.session_state['profile_artists'].remove(_artist['n'])

    
    # st.write(get_all_states())
    

    # location = st.text_input('Location', key='location', on_change=show_filtered_results)

    # if st.session_state['location'] and len(st.session_state['location_results']) > 0:
    #     for (idx, result) in enumerate(st.session_state['location_results']):
    #         if st.button(result):
    #             if 'locations' not in st.session_state:
    #                 st.session_state['locations'] = set([])
    #             st.session_state['locations'].add(result)
    st.write(st.session_state)