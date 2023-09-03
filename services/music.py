import streamlit as st
from services.locations import parse_location
from services.spotify import get_top_tracks
import time 

def load_music(errors):
    show_snow = False
    if 'profile_tracks' not in st.session_state:
        show_snow = True
    st.session_state['profile_tracks'] = []
    st.session_state['tracks'] = []
    _locations = map(lambda x: parse_location(x), st.session_state['locations'])
    for _location in _locations:
        for artist in st.session_state['profile_artists']:
            _tracks = get_top_tracks(artist, _location.get('country_code', 'US'))
            # print(json.dumps(_tracks, indent=2))
            _tracks_data = map(
                lambda x: {
                    'name': x['name'],
                    'preview_url': x['preview_url'],
                    'href': x['external_urls']['spotify'],
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
