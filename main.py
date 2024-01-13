import textwrap
import re
import requests
from config import TXT_ANALYSIS_API_KEY, PPLX_API_KEY
import sys


def extract_text(file_path, api_key):
    try:
        url = 'https://text-analysis12.p.rapidapi.com/text-mining/api/v1.1'
        headers = {
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': 'text-analysis12.p.rapidapi.com'
        }
        file = {
            'input_file': open(file_path, 'rb')
        }
        response = requests.post(url=url, headers=headers, files=file)
        result = response.json()
        if result['ok']:
            text = result['text']
            return text
        else:
            raise ValueError("Text extraction failed.")
    except Exception as e:
        print(f"Error extracting text: {e}")
        sys.exit(1)


def clean_text(text):
    text = text.replace('\n', ' ').replace('- ', '')
    pattern = re.compile(r'(?i)(REFERENCES|Bibliography|BIBLIOGRAPHY).*')
    text = re.sub(pattern, '', text)
    pattern = re.compile(r'\[\d+\]')
    result = re.sub(pattern, ' ', text)
    return result


def summarize(api_key, text):
    try:
        url = "https://api.perplexity.ai/chat/completions"
        middle_point = int(len(text) / 2)

        payload = {
            "model": "llama-2-70b-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "Be precise and concise."
                },
                {
                    "role": "user",
                    "content": f" Summarize the article for me: {text[:middle_point]}, Sum up the most important results and implications"
                }
            ],
        }
        payload2 = {
            "model": "llama-2-70b-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "Be precise and concise."
                },
                {
                    "role": "user",
                    "content": f" Summarize the article for me: {text[:middle_point]},Sum up the most important results and implications"
                }
            ],
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            'Authorization': f'Bearer {api_key}'}
        response1 = requests.post(url, json=payload, headers=headers).json()['choices'][0]['message']['content']
        response2 = requests.post(url, json=payload2, headers=headers).json()['choices'][0]['message']['content']
        text = response1 + response2
        return text
    except Exception as e:
        print(f"Error summarizing text: {e}")
        sys.exit(1)


def save_to_file(text, pdf_path):
    try:
        text = textwrap.fill(text, width=100)
        filename = pdf_path.split('/')[-1][:-4]
        file_path = f"{filename}.txt"
        with open(file_path, "w") as file:
            file.write(text)
    except Exception as e:
        print(f"Error saving to file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    extracted = extract_text(pdf_path, TXT_ANALYSIS_API_KEY)
    cleaned = clean_text(extracted)
    summarized = summarize(PPLX_API_KEY, cleaned)
    save_to_file(summarized, pdf_path)
