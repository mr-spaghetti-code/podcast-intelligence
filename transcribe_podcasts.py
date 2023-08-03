import argparse
import json
import os
import whisper

from utils import (
    str2bool,
)


def transcribe_audio(path_to_files, segments_dir, processed_dir):
    print(f"Transcribing audio in: {path_to_files}")
    inputs_mp3 = os.listdir(path_to_files)
    for audio_file in inputs_mp3:
        name = audio_file.split(".")[0]
        source = f"{path_to_files}/{audio_file}"
        print(f"Processing {name} -- Path: {source}")

        segments_path = f"{segments_dir}/{name}_segments.json"
        processed_path = f"{processed_dir}/{name}.json"
                
        if not os.path.isfile(processed_path):
            result = model.transcribe(source,
                                      verbose = verbose)
            
            chunks = processTranscript(result["segments"])
            
            json_chunks = json.dumps({
                        "title:" : name,
                        "chunks" : chunks
                    })
            
            with open(processed_path, "w") as outfile:
                outfile.write(json_chunks)

            if not os.path.isfile(segments_path):
                with open(segments_path, "w") as txt:
                    json_segments = json.dumps({
                        "title:" : name,
                        "segments" : result["segments"]
                    })
                    txt.write(json_segments)

def processTranscript(segments):
    docs = []
    suffixes = ("?", ".",'"',)
    chunk_size_chars = 1024
    segment_queue = []

    for i, segment in enumerate(segments):
        text = segment["text"].strip()
        if segment["text"].endswith(suffixes):
            if len(segment_queue) > 0:
                docs.append(" ".join(segment_queue) + " " + text)
                segment_queue = []
            else:
                docs.append(text)
        else:
            segment_queue.append(text)

    chunked_docs = []
    running_char_count = 0
    new_queue = []

    for i, segment in (enumerate(docs)):
        # print([i, segment])
        chunk_length = len(segment)
        if running_char_count <= chunk_size_chars:
            new_queue.append(segment)
            running_char_count += chunk_length
        else:
            chunk = " ".join(new_queue)
            chunked_docs.append(chunk)
            new_queue = []
            running_char_count = 0
    
    return chunked_docs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--model", type=str, help="The Whisper model you wan to use (eg. base, small, medium, large)")
    parser.add_argument("--audio_path", type=str, help="That path to the folder containing your audio")
    parser.add_argument("--podcast_title", type=str, help="The title of your podcast")
    parser.add_argument("--verbose", type=str2bool, default=False, help="Whether to output extra information when Whisper does its job")
    
    args = parser.parse_args().__dict__
    
    model: str = args.pop("model")
    audio_path: str = args.pop("audio_path")
    podcast_title: str = args.pop("podcast_title")
    verbose: bool = args.pop("verbose")

    model = whisper.load_model(model)

    output_dir = f"{podcast_title}/mp3"
    transcripts_dir = f"{podcast_title}/output"
    segments_dir = f"{transcripts_dir}/segments"
    processed_dir = f"{transcripts_dir}/processed"


    if not os.path.exists(transcripts_dir):
        os.makedirs(transcripts_dir, exist_ok=True)
        os.makedirs(segments_dir, exist_ok=True)
        os.makedirs(processed_dir, exist_ok=True)

    transcribe_audio(audio_path, segments_dir, processed_dir)
