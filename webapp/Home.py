import streamlit as st

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
    **👈 Get started ** by selecting a demo from the sidebar.

"""
)
