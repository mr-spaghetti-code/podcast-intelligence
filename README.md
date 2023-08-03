# PODemos

PODemos is a tool for AI-powered podcast intelligence. It means "We can" in Portuguese. The goal is to help busy podcast lovers summarize and make sense of their favorite content without having to listen to hours of audio.

It is currently deployed at https://podemos.streamlit.app/ (I cannot guarantee it will stay up...)

## Download podcasts
`get_podcasts.py` allows you to download the audio for any RSS feed you provide. You can find the RSS feed URLs in https://podcastindex.org/

Example usage:
```
python get_podcasts.py \
--rss_feed 'https://anchor.fm/s/89f4aa68/podcast/rss' \
--podcast_title 'delphi'txlq1ktw2nl.cloudfront.net%2Fstaging%2F2022-2-14%2F253700471-44100-2-9e33bc130af86081.mp3
```

## Transcribe podcasts
`transcribe_podcasts.py` will use Whisper to transcribe your audio and chunk the segments into a coherent sections which are useful for LLMs.

You can install Whisper by running the command below if `pip install openai-whisper` doesn't work.
`pip install git+https://github.com/openai/whisper.git`

## PODemos Tool
You can run the web app using the command: `starlit run Home.py`. It does two things:
- Podcast summarization: summarize the podcast selected.
- Podcast Q&A: query the content of a podcast using natural language.

### Installation notes
To run locally or deploy from Github will need to create a folder called `.streamlit` and a file inside called `secrets.toml` that contains your API keys. This project requires API access and keys to:
- OpenAI
- Anthropic
- ActiveLoop
- Supabase

