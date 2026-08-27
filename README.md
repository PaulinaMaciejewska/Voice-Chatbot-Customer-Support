# Voice Chatbot Customer Support

## Objective
A voice assistant that analyzes questions and generates answers.

## Scope
- Speech-to-Text and Text-to-Speech using the Cognitive Services SDK.
- OpenAI completions (GPT-4o-mini).
- Conversation logging to Azure Blob.
- Web interface – using Gradio.

**Services:** Azure Speech SDK, Azure OpenAI SDK, Azure Blob Storage.

**Outcome:** A simple voicebot handling user conversations.

## Description

- The application enables the use of an electronics company's customer support chatbot. Users can ask questions about electronic products.

- The bot communicates in Polish.

- Users can submit questions via audio recording or text, while the assistant always responds with a voice message.

- Recordings are saved to Azure Blob Storage.


# Getting started

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt 
python voice_bot.py
```
