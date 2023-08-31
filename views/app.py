import streamlit as st
import pandas as pd
import time
import os
import openai
import json
import datetime
from services.spotify import get_top_tracks

errors = {}
openai.api_key = os.getenv("OPENAI_API_KEY")

# mongo_uri = f"mongodb+srv://{os.environ['MONGO_USERNAME']}:{os.environ['MONGO_PASSWORD']}@{os.environ['MONGO_HOST']}"

# @st.cache_resource
# def init_db_connection():
#     return pymongo.MongoClient(
#          mongo_uri,
#          server_api=ServerApi('1')
#     )

# mongo_client = init_db_connection()



def get_all_states():
    df = pd.read_csv('data/all-states.csv')
    return df.apply(lambda x: x['name'] + ' (' + x['country_name'] + ')', axis=1).to_list()
    
def find_country_code(country_name):
    with open('data/country-codes.csv', 'r') as db:
        while True:
            line = db.readline()
            if country_name in line:
                values = line.split(',')
                if values[0] == country_name:
                    return values[1]
            elif not line:
                break

def parse_location(location):
    if not location:
        return

    start_idx = location.index('(')
    end_idx = location.index(')')
    state = location[0: start_idx].strip()
    country = location[start_idx + 1: end_idx].strip()
    country_code = find_country_code(country)
    return {
        'state': state,
        'country': country,
        'country_code': country_code
    }


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
            if 'languages' in errors:
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

def load_artists():
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
        frequency_penalty=1,
        presence_penalty=0
    )
    # st.write(response.choices[0].message.content)
    try:
        st.session_state['artists'] = json.loads(response.choices[0].message.content)
    except:
        pass # TODO have better error handling

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

def add_top_tracks():
    if 'playlist' not in st.session_state:
        get_top_tracks()

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

def load_music():
    show_snow = False
    if 'profile_tracks' not in st.session_state:
        show_snow = True
    st.session_state['profile_tracks'] = []
    st.session_state['tracks'] = []
    _locations = map(lambda x: parse_location(x), st.session_state['locations'])
    for _location in _locations:
        for artist in st.session_state['profile_artists']:
            _tracks = get_top_tracks(artist, _location.get('country_code', 'US'))
            _tracks_data = map(
                lambda x: {
                    'name': x['name'],
                    'preview_url': x['preview_url'],
                    'href': x['href'],
                    'artists': ','.join(list(map(
                        lambda y: y['name'],
                        x['artists']
                    )))
                },
                _tracks
            )
            st.session_state['tracks'].extend(_tracks)
            st.session_state['profile_tracks'].extend(_tracks_data)
            time.sleep(0.2) # to avoid any throttle
    if show_snow:
        st.snow()
        next_step()

def render():
    st.set_page_config(layout='wide')
    # st.markdown('<h1 style="text-align:center; font-weight:400;">Setup Patient’s profile</h1>', unsafe_allow_html=True)
    st.header('Setup Profile')
    if 'step' in st.session_state:
        st.sidebar.markdown('Recommender Progress')
        st.sidebar.progress(st.session_state['step'] * 20)
    else:
        st.sidebar.markdown('Recommender Progress')
        st.sidebar.progress(20)

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
        st.button('Go to next step', on_click=next_step, type='primary')

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
                if len(st.session_state.get('profile_languages', [])) > 0 and st.session_state['step'] == 2:
                    st.button('Go to next step', on_click=next_step, type='primary')
        
        st.divider()

    if st.session_state.get('step', 1) > 2:
        st.markdown(f"### Step 3 : Favorite Genres")

        st.markdown(f'**Languages in which {st.session_state["profile_name"]} listens to music**')
        st.markdown(
            f'Are there any languages from below that {st.session_state["profile_name"]} prefers listening\
            to in music? You can select from below or add a new one in case our predictions missed something. '
        )
        # st.button('Load Genres', on_click=load_genres)
        if 'genres' not in st.session_state:
            st.text_input('Add Genre', key='custom_genre', on_change=add_custom_genre)
            if 'genres' in errors:
                st.error(errors['genres'])
            cols = st.columns(3)
            with cols[-1]:
                st.button('Get Suggested Genres', on_click=load_genres, type='primary')
        if 'genres' in st.session_state:
            cols = st.columns(4)
            if 'profile_genres' not in st.session_state:
                        st.session_state['profile_genres'] = set([])
            for (idx, genre) in enumerate(st.session_state['genres']):
                with cols[idx % 4]:
                    try:
                        if st.checkbox(genre) == True:
                            st.session_state['profile_genres'].add(genre)
                        elif genre in st.session_state['profile_genres']:
                            st.session_state['profile_genres'].remove(genre)
                    except Exception as err:
                        print(err)
            
            if 'genres' in errors:
                st.error(errors['genres'])

            st.text_input('Did we miss some genre? Add it here.', key='custom_genre', on_change=add_custom_genre)

            cols = st.columns(3)
            with cols[-1]:
                st.button('Get Suggested Genres', on_click=load_genres)
            with cols[0]:
                if len(st.session_state.get('profile_genres', [])) > 0 and st.session_state['step'] == 3:
                    st.button('Go to next step', on_click=next_step, type='primary')

    if st.session_state.get('step', 1) > 3:
        st.markdown(f"### Step 4 : Favorite Artists")

        st.markdown(f'**Languages in which {st.session_state["profile_name"]} listens to music**')
        st.markdown(
            f'Are there any languages from below that {st.session_state["profile_name"]} prefers listening\
            to in music? You can select from below or add a new one in case our predictions missed something. '
        )
        if 'profile_artists' not in st.session_state:
            st.session_state['profile_artists'] = set()

        if 'artists' not in st.session_state:
            st.text_input('Add Artist', key='custom_artist', on_change=add_custom_artist)
            if 'artists' in errors:
                st.error(errors['artists'])
            cols = st.columns(3)
            with cols[-2]:
                st.markdown('WARNING: This can be a little slow 👉')
            with cols[-1]:
                st.button('Get Suggested Artists', on_click=load_artists, type='primary')
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
                    try:
                        if st.checkbox(_label) == True:
                            st.session_state['profile_artists'].add(key)
                        elif key in st.session_state['profile_artists']:
                            st.session_state['profile_artists'].remove(key)
                    except Exception as err:
                        print(err)
            
            st.text_input('Did we miss some artist? Add it here.', key='custom_artist', on_change=add_custom_artist)

            cols = st.columns(3)
            with cols[-1]:
                st.button('Get Suggested Artists', on_click=load_artists)
            with cols[0]:
                st.button('Load Playlist Suggestions', on_click=load_music, type='primary')

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

    st.divider()
    if 'profile_tracks' in st.session_state and type(st.session_state['profile_tracks'] == list):
        cols = st.columns([2, 3, 4, 1])
        for (_idx, col) in enumerate(cols):
            with col:
                if _idx == 0:
                    st.markdown('**Song**')
                if _idx == 1:
                    st.markdown('**Artists**')
                if _idx == 2:
                    st.markdown('**Preview**')
                if _idx == 0:
                    st.markdown('**Selected**')
        for (_idx, _track) in enumerate(st.session_state['profile_tracks']):
            cols = st.columns([0.2, 0.3, 0.4, 0.1])
            with cols[0]:
                st.markdown(_track['name'])
            with cols[1]:
                st.markdown(_track['artists'])
            with cols[2]:
                st.audio(_track['preview_url'])
            with cols[3]:
                st.checkbox(str(_idx), value=True)
    
    # st.button('Save Playlist', type='primary')
    # st.write(get_all_states())
    
    # location = st.text_input('Location', key='location', on_change=show_filtered_results)

    # if st.session_state['location'] and len(st.session_state['location_results']) > 0:
    #     for (idx, result) in enumerate(st.session_state['location_results']):
    #         if st.button(result):
    #             if 'locations' not in st.session_state:
    #                 st.session_state['locations'] = set([])
    #             st.session_state['locations'].add(result)
    # st.write(st.session_state)