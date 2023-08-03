import os
import streamlit as st

from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatAnthropic
from langchain.docstore.document import Document
from langchain.document_loaders import JSONLoader

from langchain import PromptTemplate
from storage3 import create_client

os.environ['ANTHROPIC_API_KEY'] = st.secrets.anthropic_api_key

st.set_page_config(page_title="Summarize Podcast", page_icon="📚")

st.markdown("# Podcast Summarization Demo")
st.sidebar.header("Podcast Summarization Demo")

st.write(
    """This demo illustrates how we can use an LLM to summarize a podcast.
    Pick an episode of the Delphi Podcast and hit 'Submit'."""
)

headers = {"apiKey": st.secrets.supabase_key, "Authorization": f"Bearer {st.secrets.supabase_key}"}
storage_client = create_client(st.secrets.supabase_url, headers, is_async=False)

map_prompt = """
Write a concise summary of the text in enclosed in <content></content>. Be specific and factual.
Add detail where appropriate. The summary will be used to write an article. Do not write anything before your response.
<content>
{text}
</content>
CONCISE SUMMARY:
"""
map_prompt_template = PromptTemplate(template=map_prompt, input_variables=["text"])

combine_prompt = """
You are a technical writing expert who writes highly engaging, informative, and creative blog posts. 
Write a long-form blog post about the topic below using the content enclosed in <content></content>
It contains information extracted from a podcast. Be detailed and thorough. Do not write anything before your response.
Use markdown to format the article.

<content>
{text}
</content>

Article:
"""
combine_prompt_template = PromptTemplate(template=combine_prompt, input_variables=["text"])

def get_available_titles():
    bucket = storage_client.from_('transcripts')
    response = bucket.list()
    podcast_list = [dir["name"] for dir in response]
    return podcast_list

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

def combine_chunks(docs, combine_chunks_n):
    combined_docs = []
    for i in range(0, len(docs), combine_chunks_n):
        group = docs[i:i+combine_chunks_n]
        new_content = ""
        for doc in group:
            new_content += doc.page_content
        new_doc = Document(page_content=new_content, metadata={"source": group[0].metadata["source"]})
        combined_docs.append(new_doc)
    return combined_docs

def generate_summary(chat, docs, combine_chunks_n=None):
    if combine_chunks_n:
        docs = combine_chunks(docs, combine_chunks_n)
    summarize_chain = load_summarize_chain(
        llm=chat, 
        chain_type="map_reduce",
        map_prompt=map_prompt_template,
        combine_prompt=combine_prompt_template,
        return_intermediate_steps=True,
        verbose=True
        )
    
    results = summarize_chain({"input_documents": docs}, return_only_outputs=True)

    output = {
        "intermediate_steps" : results['intermediate_steps'],
        "output_text" : results['output_text']
    }
    
    return output


available_episodes = get_available_episodes('delphi_podcast')

episode_selected = st.selectbox(
    label="Pick a podcast episode",
    options=available_episodes
)


chat = ChatAnthropic(
    temperature=0,
    verbose=True,
    max_tokens_to_sample=2048
    )

if st.button("Summarize"):
    docs = []
    with st.spinner("Retrieving docs..."):
        docs = get_docs("delphi_podcast", episode_selected)
    if docs:
        with st.spinner("Generating summary. This might take a while."):
            results = generate_summary(chat, docs, 8)
            st.write("---\n### Key notes and takeaways:")
            st.write(results['output_text'])
            for step in results['intermediate_steps']:
                step = step.replace("Here is a concise summary of the key points from the text:", "")
                st.write(f"{step}---\n")
