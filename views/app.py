import streamlit as st
import time
import os
import json
import datetime
from services.locations import get_all_states, parse_location
from services.languages import load_languages, add_custom_language
from services.genres import load_genres, add_custom_genre
from services.artists import load_artists, add_custom_artist
from services.music import load_music
import openai

openai.api_key = os.getenv("OPENAIAPIKEY")

errors = {}

def _load_languages():
    return load_languages(errors)

def _load_genres():
    return load_genres(errors)

def _load_artists():
    return load_artists(errors)

def _load_music():
    music = load_music(errors)
    next_step()

def next_step():
    print('next step')
    if 'step' not in st.session_state:
        st.session_state['step'] = 2
    else:
        st.session_state['step'] = st.session_state['step'] + 1

def render_sidebar():
    if 'step' in st.session_state:
        st.sidebar.markdown(f"Progress: Step {st.session_state.get('step', 1)} of 5")
        st.sidebar.progress(st.session_state['step'] * 20)
    else:
        st.sidebar.markdown('Progress: Step 1 of 5')
        st.sidebar.progress(20)

def render_basic_info():
    st.divider()
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

def render_language_prefs():
    st.divider()

    if st.session_state.get('step', 1) > 1:
        st.markdown(f"### Step 2 : Language Preferences")

        st.markdown(f'**Languages in which {st.session_state.get("profile_name", "the patient")} listens to music**')
        st.markdown(
            f'Click on *Get Suggested Languages* to get a list of suggested languages. In case the language of choice is not there, you can add it manually.'
        )
        if 'languages' not in st.session_state:
            st.text_input('Add Language', key='custom_language', on_change=add_custom_language)
            if 'languages' in errors:
                st.error(errors['languages'])
            cols = st.columns(3)
            with cols[0]:
                st.button('Get Suggested Languages', on_click=_load_languages, type='primary')
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
            with cols[0]:
                st.button('Get Suggested Languages', on_click=_load_languages)
            with cols[-1]:
                if len(st.session_state.get('profile_languages', [])) > 0 and st.session_state['step'] == 2:
                    st.button('Go to next step', on_click=next_step, type='primary')
        
        st.divider()

def render_genre_prefs():
    if st.session_state.get('step', 1) > 2:
        st.markdown(f"### Step 3 : Favorite Genres")

        st.markdown(f'**Genres that move {st.session_state["profile_name"]}**')
        st.markdown(
            f'What are {st.session_state["profile_name"]}\'s favorite genres?\
            You can click *Get Suggested Genres* to get some suggestions or add a new one manually in case our predictions missed something. '
        )
        # st.button('Load Genres', on_click=load_genres)
        if 'genres' not in st.session_state:
            st.text_input('Add Genre', key='custom_genre', on_change=add_custom_genre)
            if 'genres' in errors:
                st.error(errors['genres'])
            cols = st.columns(3)
            with cols[0]:
                st.button('Get Suggested Genres', on_click=_load_genres, type='primary')
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
            with cols[0]:
                st.button('Get Suggested Genres', on_click=_load_genres)
            with cols[-1]:
                if len(st.session_state.get('profile_genres', [])) > 0 and st.session_state['step'] == 3:
                    st.button('Go to next step', on_click=next_step, type='primary')

def render_favorite_artists():
    if st.session_state.get('step', 1) > 3:
        st.divider()
        st.markdown(f"### Step 4 : Favorite Artists")

        st.markdown(f'**Who are the favorite artists of {st.session_state.get("profile_name", "the patient")}?**')
        st.markdown(
            f'Knowing these artists will help us predict some songs which may have a deeper meaning for {st.session_state.get("profile_name", "the patient")}'
        )
        if 'profile_artists' not in st.session_state:
            st.session_state['profile_artists'] = set()

        if 'artists' not in st.session_state:
            st.text_input('Add Artist', key='custom_artist', on_change=add_custom_artist)
            if 'artists' in errors:
                st.error(errors['artists'])
            cols = st.columns(3)
            with cols[0]:
                st.button('Get Suggested Artists', on_click=_load_artists, type='primary')
                st.markdown('WARNING: This can be a little slow 👆')
        if 'artists' in st.session_state:
            all_artists = dict()
            artists = st.session_state['artists']
            for glp in artists:
                _lang = glp['glp'].split('-')[-1]
                for _artist in glp['artists']:
                    if 'n' in _artist and _artist['n'] not in all_artists:
                        all_artists[_artist['n']] = _lang
            cols = st.columns(3)
            # st.write(all_artists)
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
            with cols[0]:
                st.button('Get Suggested Artists', on_click=_load_artists)
            with cols[2]:
                st.button('Load Playlist Suggestions', on_click=_load_music, type='primary')

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

def render_playlist():
    if st.session_state.get('step', 1) > 4:
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
                    st.markdown(f'<a href="{_track["href"]}" target="_blank">{_track["name"]}</a>', unsafe_allow_html=True)
                with cols[1]:
                    st.markdown(_track['artists'])
                with cols[2]:
                    st.audio(_track['preview_url'])
                with cols[3]:
                    st.checkbox(str(_idx), value=True)

def render():
    st.set_page_config(layout='wide')
    st.header('Map The Journey')

    render_sidebar()
    render_basic_info()
    render_language_prefs()
    render_genre_prefs()
    render_favorite_artists()
    render_playlist()