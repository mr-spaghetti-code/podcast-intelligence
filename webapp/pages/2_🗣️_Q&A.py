import os
import streamlit as st

from langchain.chains import RetrievalQA
from langchain.chat_models import ChatAnthropic
from langchain.document_loaders import JSONLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import DeepLake
from storage3 import create_client

st.set_page_config(page_title="Q&A Podcast", page_icon="🗣️")

st.markdown("# Podcast Q&A Demo")
st.sidebar.header("Podcast Q&A Demo")

st.write(
    """This demo illustrates how we can use an LLM to ask questions about a specific podcast.
    Select an episode of the Delphi podcast, write a question and hit 'Submit'."""
)


os.environ['ACTIVELOOP_TOKEN'] = st.secrets.activeloop_api_key
os.environ['OPENAI_API_KEY'] = st.secrets.openai_api_key
os.environ['ANTHROPIC_API_KEY'] = st.secrets.anthropic_api_key

headers = {"apiKey": st.secrets.supabase_key, "Authorization": f"Bearer {st.secrets.supabase_key}"}
storage_client = create_client(st.secrets.supabase_url, headers, is_async=False)

if "podcast_selected" not in st.session_state:
    st.session_state["podcast_selected"] = ''


def get_available_episodes(podcast_title):
    bucket = storage_client.from_('transcripts')
    response = bucket.list(f'{podcast_title}/output/processed')
    episode_list = [dir["name"].split(".")[0] for dir in response]
    while("" in episode_list):
        episode_list.remove("")
    return episode_list

def get_docs(podcast_title, episode_title):
    bucket = storage_client.from_('transcripts')
    name = f'{podcast_title}/output/processed/{episode_title}.json'
    with open(f'{episode_title}.json', 'wb+') as f:
        res = bucket.download(name)
        f.write(res)
    loader = JSONLoader(
        file_path=f'{episode_title}.json',
        jq_schema='.chunks[]'
    )
    docs = loader.load()
    os.remove(f'{episode_title}.json')
    return docs

if st.session_state["podcast_selected"]:
    available_episodes = get_available_episodes(st.session_state["podcast_selected"])

    episode_selected = st.selectbox(
        label="Pick a podcast episode",
        options=available_episodes
    )

    query = st.text_input(
        label="Ask a question."
    )
else:
    st.warning("Please select a podcast from the 'Home' page.")



if st.button("Submit"):
    docs = []
    with st.spinner("Retrieving docs..."):
        docs = get_docs(st.session_state["podcast_selected"], episode_selected)
    if docs:
        with st.spinner("Thinking"):
            chat = ChatAnthropic(
                temperature=0,
                verbose=True,
                max_tokens_to_sample=2048
            )
            embeddings = OpenAIEmbeddings(disallowed_special=())
            dataset_path = f'hub://mrspaghetticode/{episode_selected}'
            db = DeepLake.from_documents(docs, embeddings, dataset_path=dataset_path)
            retriever = db.as_retriever()
            retriever.search_kwargs["distance_metric"] = "cos"
            retriever.search_kwargs["fetch_k"] = 100
            retriever.search_kwargs["maximal_marginal_relevance"] = True
            retriever.search_kwargs["k"] = 20


            qa = RetrievalQA.from_chain_type(
                llm=chat,
                chain_type="stuff",
                verbose=True, 
                retriever=db.as_retriever())

            results = qa.run(query)
            st.write(results)