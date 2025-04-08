import nltk
from nltk.tokenize import sent_tokenize
nltk.download('punkt_tab')


def split_into_chunks(text: str, chunk_size: int) -> list[str]:
    sentences = sent_tokenize(text)
    current_chunk = ''
    text_chunks = []

    if len(text) <= chunk_size:
        return [text]

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence
        else:
            if current_chunk:
                text_chunks.append(current_chunk)
                current_chunk = sentence
            else:
                text_chunks.append(sentence)

    if text_chunks:
        text_chunks.append(current_chunk)


    return text_chunks
