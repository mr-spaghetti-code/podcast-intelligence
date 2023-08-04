import streamlit as st
from storage3 import create_client

headers = {"apiKey": st.secrets.supabase_key, "Authorization": f"Bearer {st.secrets.supabase_key}"}
storage_client = create_client(st.secrets.supabase_url, headers, is_async=False)

def get_available_titles():
    bucket = storage_client.from_('transcripts')
    response = bucket.list()
    podcast_list = [dir["name"] for dir in response]
    return podcast_list

if "podcast_selected" not in st.session_state:
    st.session_state["podcast_selected"] = ''

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome to PODemos! 🎧")

st.markdown(
    """
    PODemos is a demo tool for analyzing podcasts.

    Please refer to [Github](x) for more information.

    PODemos allows you to do two things:
    - Summarize a podcast.
    - Question & Answer with a podcast.
    - To get started, pick a podcast from the dropdown below and hit "Start".

"""
)

available_podcasts = get_available_titles()

podcast_selected = st.selectbox(
    label="Pick a podcast",
    options=available_podcasts
)

status = st.info(f'Select a podcast from the list...', icon="ℹ️")

if st.button("Start"):
    status.success(f"Selected {podcast_selected}")
    st.session_state["podcast_selected"] = podcast_selected





