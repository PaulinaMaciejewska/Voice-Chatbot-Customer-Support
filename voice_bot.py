import os
import gradio as gr
from datetime import datetime
from config import Config
import azure.cognitiveservices.speech as speechsdk
from azure.core.exceptions import ResourceExistsError
import soundfile as sf
import io

class VoiceBot: 
    def __init__(self): 
        self.speech_config = Config.get_speech_config()
        self.speech_synthesizer = Config.setup_speech_synthesizer()
        self.openai_client = Config.get_openai_client()
        self.blob_storage_client = Config.get_blob_storage_client()
        self.conversation = []
        
    def handle_text_message(self, user_text, history): 
    
        if not user_text:
            return "Wpisz wiadomość tekstową.", history

        openai_response = self.create_bot_response(user_text)

        bot_audio = self.generate_bot_audio(openai_response)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        local_bot_path = self.save_audio_locally(bot_audio, f"bot_{timestamp}.wav", dir_path='bot')
        
        bot_audio_url = self.upload_to_blob(bot_audio, f"bot_{timestamp}.wav")
        
        self.conversation.append({
            "role": "assistant",
            "type": "audio",
            "url": bot_audio_url,
            "text": openai_response
        })

        history.append((
            user_text, 
            {
            "path": local_bot_path,
            "mime_type": "audio/wav"
            }
        ))
            
        return history

    def generate_bot_audio(self, text):
        result = self.speech_synthesizer.speak_text_async(text).get()
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return result.audio_data
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation = result.cancellation_details
            print(f"⚠️ TTS anulowane: {cancellation.reason}")
            if cancellation.error_details:
                print(f"Szczegóły błędu: {cancellation.error_details}")
    
    def create_bot_response(self, user_text):
        content = """
            Jesteś asystentem klienta dla firmy zajmującej się sprzedażą elektroniki. Twoim zadaniem jest pomaganie klientom w rozwiązywaniu problemów związanych z produktami, udzielanie informacji o produktach oraz wspieranie ich w procesie zakupowym. Odpowiadaj w sposób uprzejmy, profesjonalny i pomocny. Jeśli nie znasz odpowiedzi na pytanie, zasugeruj skontaktowanie się z działem obsługi klienta firmy.
            """
        
        messages = [{"role": "system", "content": content}]
        for message in self.conversation:
            messages.append({"role": message["role"], "content": message["text"]})
        messages.append({"role": "user", "content": user_text})
        
        try:
            response = self.openai_client.chat.completions.create(
                model=Config.OPENAI_DEPLOYMENT_NAME,
                messages=messages,
                max_tokens=500,
            )
        except Exception as e:
            print(f"⚠️ Błąd podczas tworzenia odpowiedzi: {e}")
            return "Przepraszam, wystąpił błąd podczas generowania odpowiedzi.", []
        
        bot_reply = response.choices[0].message.content.strip()
        return bot_reply       
    
          
    def handle_voice_message(self, audio_file, history):
        
        text = self.recognize_audio(audio_file)
        if not text:
            return history + [("⚠️ Nie rozpoznano mowy. Proszę spróbuj ponownie.", None)]

        openai_response = self.create_bot_response(text)

        bot_audio = self.generate_bot_audio(openai_response)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        local_user_path = self.save_audio_locally(audio_file, f"user_{timestamp}.wav", dir_path='user')
        local_bot_path = self.save_audio_locally(bot_audio, f"bot_{timestamp}.wav", dir_path='bot')
        
        user_audio_url = self.upload_to_blob(audio_file, f"user_{timestamp}.wav")
        bot_audio_url = self.upload_to_blob(bot_audio, f"bot_{timestamp}.wav")

        
        self.conversation.append({
            "role": "user",
            "type": "audio",
            "url": user_audio_url,
            "text": text
        })
        self.conversation.append({
            "role": "assistant",
            "type": "audio",
            "url": bot_audio_url,
            "text": openai_response
        })

        history.append((
            {
            "path": local_user_path,
            "mime_type": "audio/wav"
            },
            {
            "path": local_bot_path,
            "mime_type": "audio/wav"
            }
            ))
        
        return history

    def recognize_audio(self, audio_file):

        audio_config = speechsdk.AudioConfig(filename=audio_file)
        recognizer = speechsdk.SpeechRecognizer(self.speech_config, audio_config)
        result = recognizer.recognize_once()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return result.text
        else:
            print("⚠️ Nie rozpoznano mowy:", result.reason)
            return None
        
    def save_audio_locally(self, audio_data, filename, dir_path='user'):
        import os, io, shutil

        local_dir = f"local_audio/{dir_path}"
        os.makedirs(local_dir, exist_ok=True)
        local_path = os.path.join(local_dir, filename)

        if isinstance(audio_data, bytes):
            with open(local_path, 'wb') as f:
                f.write(audio_data)
        elif isinstance(audio_data, str) and os.path.exists(audio_data):
            shutil.copy(audio_data, local_path)
        else:
            raise ValueError(f"Nieobsługiwany typ audio_data: {type(audio_data)}")
        
        return local_path.replace('\\', '/')

    def upload_to_blob(self, audio_file, filename): 
        try:

            try:
                container_client = self.blob_storage_client.get_container_client(Config.BLOB_CONTAINER_NAME)
                container_client.create_container()
            except ResourceExistsError:
                pass
            except Exception as e:
                print(f"Error creating container: {e}")
                        
            blob_client = self.blob_storage_client.get_blob_client(
                container=Config.BLOB_CONTAINER_NAME, 
                blob=filename
            )
            
            if isinstance(audio_file, bytes):
                blob_client.upload_blob(audio_file, overwrite=True)
                return blob_client.url
            
            with open(audio_file, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            
            return blob_client.url
        
        except Exception as e:
            print(f"Błąd uploadowania plików audio do Azure: {e}")
            return None
        
        
    def clear_all(self): 
        return [], None, ""
        


with gr.Blocks() as demo:
    voice_bot = VoiceBot()
    
    gr.Markdown("# 🔊 Voice Chatbot Customer Support for an electronics company - talk to me OR write your message and I will response with audio")
    
    chatbot = gr.Chatbot(label="Voice Chatbot", height=600)
    
    audio_input = gr.Audio(sources=["microphone"], type="filepath", label="Record your voice message")
    send_audio_btn = gr.Button("Send Voice Message")
    
    text_input  = gr.Textbox(label="Or type your message")
    send_text_btn = gr.Button("Send Text Message")
    
    clear_button = gr.Button("Clear Chat")


    send_audio_btn.click(
        fn=voice_bot.handle_voice_message,
        inputs=[audio_input, chatbot],
        outputs=[chatbot]
    )
    
    send_text_btn.click(
        fn=voice_bot.handle_text_message,
        inputs=[text_input, chatbot],
        outputs=[chatbot]
    )
    
    clear_button.click(
    fn=voice_bot.clear_all,
    inputs=[],
    outputs=[chatbot, audio_input, text_input],
    queue=False
    )

demo.launch()
