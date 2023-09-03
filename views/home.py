import streamlit as st

def get_styles():
    styles = None
    with open('styles/home.css', 'r') as css:
        styles = css.read()
    return f"""
        <style>
            {styles}
        </style>
    """

def render():
    st.set_page_config(layout='wide', initial_sidebar_state='expanded')
    # st.markdown(get_styles(), unsafe_allow_html=True)

    st.image('images/home-cover.jpg')
    
    st.markdown("""
        # 
        The prevalence of dementia has touched countless lives, reshaping the way we care for our loved ones. At Life's Playlist, we understand the challenges that both professional caregivers and families face in providing the best care possible. Our mission is to harness the power of music to transform caregiving moments into cherished interactions, allowing individuals with dementia to reconnect with their past and create new moments of joy.

        ## **About Life's Playlist**

        Life's Playlist is a revolutionary tool designed with the needs of professional caregivers and families of dementia patients in mind. Our platform combines cutting-edge technology with the timeless magic of music to create personalized experiences that uplift mood, ignite memories, and enhance the overall quality of life for patients and their families.
    """)

    st.video('https://youtu.be/oIGkoxzdvHw')
    st.markdown("""
        ## **Key Features**

        ### ✅ Mapping Life's Journey Through Music

        Every life is a unique journey, filled with moments that shape who we are. With Life's Playlist, we help you map the life journey of your loved one or patient. By understanding their music preferences, favorite songs, and significant life events, we curate a personalized playlist that resonates with their soul.

        ### ✅ Documenting the Impact [Coming Soon]

        Life's Playlist doesn't just stop at creating playlists. Our platform lets you document the impact of each song on the patient. As caregivers, you can track changes in mood, moments of recognition, and even improvements in cognitive functions. This documentation not only helps in understanding your loved one better but also aids medical professionals in providing tailored care.

        ## **Uplifting Lives, One Song at a Time**

        ### 🪄🪄 Music's Miraculous Effects

        Scientific research has shown that music has a profound impact on individuals with dementia. It reaches deep into the recesses of memory, evoking emotions, and rekindling connections thought to be lost. At Life's Playlist, we believe that each playlist is a journey through time, a chance to relive beautiful memories and create new ones.

        ### ❄️❄️ Personalized Playlists That Matter

        Our platform goes beyond generic playlists. We consider the patient's musical journey, their likes, and their life events to curate a selection that's truly personal. The power of a familiar melody can soothe anxieties, bring back a smile, and provide comfort like nothing else.

        ### 💖 Compassionate Care, Empowered Families

        For professional caregivers, Life's Playlist streamlines your efforts, making each interaction with your patient more meaningful. For families, it's an opportunity to connect on a deeper level, even in the face of cognitive challenges. Our platform becomes a bridge that spans generations, igniting conversations and preserving legacies.

        ## See the Difference
       
        
    """)

    # Print a grid of videos

    cols = st.columns(3)
    with cols[0]:
        st.video('https://youtu.be/aKQsxKhtDos?si=lzLQVbgQf34akcUj')
    with cols[1]:
        st.video('https://youtu.be/QiPoo4zwnIo?si=OpgQC3KRasmSfLZq&t=13')
    with cols[2]:
        st.video('https://youtu.be/Fm_Qglpoaiw?si=ggB9f3_4HCUvG45A')
    
    with cols[0]:
        st.video('https://youtu.be/jOxP3BEgVtQ?si=weJdiCyZqySH17zh')
    with cols[1]:
        st.video('https://youtu.be/G7vkKHYosuQ?si=PYq-tadLaXwJg_pD')
    with cols[2]:
        st.video('https://youtu.be/8HLEr-zP3fc?si=0fkmtwD-T6aKt37b')

    st.markdown("""
    
    <a href="https://www.youtube.com/results?search_query=dementia+music" target="_blank">See More</a>

    ## 🙌 Join the Journey

    Every individual deserves a life filled with moments of joy, even in the face of dementia. With Life's Playlist, you're not just playing music – you're composing a symphony of memories, emotions, and connections. Join us in revolutionizing dementia care, one song at a time.

    """, unsafe_allow_html=True)