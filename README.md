# Voice Chatbot Customer Support

## Cel
Asystent głosowy analizujący pytania i generujący odpowiedzi.

## Zakres
- Speech-to-Text i Text-to-Speech z Cognitive Services SDK.
- OpenAI completions (GPT-4o-mini).
- Logowanie rozmów do Azure Blob.
- Interfejs webowy – z gradio
- Demo końcowe.

**Usługi:** Azure Speech SDK, Azure OpenAI SDK, Azure Blob Storage.

**Rezultat:** prosty voicebot obsługujący rozmowy użytkowników.

## Opis

- Aplikacja umożliwia korzystanie z chatbota firmy elektronicznej do wsparcia klienta. Można zadawać pytania odnośnie produktów z zakresu elektroniki. 

- Bot posługuje się językiem polskim. 

- Użytkownik może zadać pytanie w postaci nagrania lub tekstowo, a asystent zawsze odpowie na wiadomość głosowo. 

- Nagrania są zapisywane do Azure Blob Storage.


# Uruchomienie programu

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt 
python voice_bot.py
```
