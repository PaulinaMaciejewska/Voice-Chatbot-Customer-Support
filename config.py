import azure.cognitiveservices.speech as speechsdk
from azure.storage.blob import BlobServiceClient
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()


class Config: 
    SPEECH_KEY = os.getenv('AZURE_SPEECH_KEY')
    SERVICE_REGION = os.getenv('AZURE_SERVICE_REGION')
    BLOB_STORAGE_CONNECTION_STRING = os.getenv('BLOB_STORAGE_CONNECTION_STRING')
    BLOB_CONTAINER_NAME= os.getenv('BLOB_CONTAINER_NAME')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_ENDPOINT = os.getenv('OPENAI_ENDPOINT')
    OPENAI_DEPLOYMENT_NAME = os.getenv('OPENAI_DEPLOYMENT_NAME')
    OPENAI_API_VERSION = os.getenv('OPENAI_API_VERSION', '2025-01-01-preview' )
    
    @staticmethod
    def get_openai_client():
        openai_client = AzureOpenAI(
            azure_endpoint=Config.OPENAI_ENDPOINT,
            api_key=Config.OPENAI_API_KEY,
            api_version=Config.OPENAI_API_VERSION
        )
        return openai_client
        
    @staticmethod
    def get_speech_config(): 
        speech_config = speechsdk.SpeechConfig(
            subscription=Config.SPEECH_KEY,
            region=Config.SERVICE_REGION
        )
        
        speech_config.speech_recognition_language = "pl-PL"
        speech_config.speech_synthesis_language = "pl-PL"
        speech_config.speech_synthesis_voice_name = "pl-PL-MarekNeural"
        
        return speech_config
    
    @staticmethod
    def setup_speech_synthesizer():
        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=Config.get_speech_config(),
            audio_config=None
        )
        return speech_synthesizer

    @staticmethod
    def get_blob_storage_client(): 
        
        blob_storage_client = BlobServiceClient.from_connection_string(
            Config.BLOB_STORAGE_CONNECTION_STRING
        )
        
        return blob_storage_client
    
    


    