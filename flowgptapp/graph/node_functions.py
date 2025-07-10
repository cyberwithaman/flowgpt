"""
Node functions for FlowGPT LangGraph implementation.
These functions implement various text processing operations.
They are designed to be used as nodes in a LangGraph workflow.
"""
import re
import json
import datetime
from typing import Dict, Any, Optional


def clean_text(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cleans the text by:
    - Removing extra whitespace
    - Removing special characters if specified in config
    - Removing URLs if specified in config
    """
    text = state.get("text", "")
    config = state.get("config", {})
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove special characters if configured
    if config.get("remove_special_chars", False):
        text = re.sub(r'[^\w\s]', '', text)
    
    # Remove URLs if configured
    if config.get("remove_urls", False):
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Update state with processed text
    state["text"] = text
    
    # Add processing metadata
    state.setdefault("metadata", {}).update({
        "clean_text_applied": True,
        "clean_text_timestamp": str(datetime.datetime.now())
    })
    
    return state


def convert_to_uppercase(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts text to uppercase.
    """
    text = state.get("text", "")
    state["text"] = text.upper()
    
    # Add processing metadata
    state.setdefault("metadata", {}).update({
        "uppercase_applied": True,
        "uppercase_timestamp": str(datetime.datetime.now())
    })
    
    return state


def basic_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates a basic summary by taking the first N sentences or characters.
    This is a rule-based approach, not using any NLP/AI.
    """
    text = state.get("text", "")
    config = state.get("config", {})
    
    # Default to first 2 sentences if not specified
    num_sentences = config.get("num_sentences", 2)
    max_chars = config.get("max_chars", None)
    
    # Simple sentence splitting (this is a basic implementation)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    if num_sentences and num_sentences > 0:
        summary = ' '.join(sentences[:min(num_sentences, len(sentences))])
    else:
        summary = text
    
    # Truncate to max_chars if specified
    if max_chars and len(summary) > max_chars:
        summary = summary[:max_chars] + "..."
    
    # Store the summary while preserving original text
    state["summary"] = summary
    
    # Add processing metadata
    state.setdefault("metadata", {}).update({
        "summary_applied": True,
        "summary_timestamp": str(datetime.datetime.now()),
        "summary_config": {
            "num_sentences": num_sentences,
            "max_chars": max_chars
        }
    })
    
    return state


def translate(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Translates text using a simple dictionary mapping.
    This is a mock function that only supports a few hardcoded translations.
    """
    text = state.get("text", "")
    config = state.get("config", {})
    target_lang = config.get("target_language", "spanish")
    
    # Mock translations for a few common phrases
    translations = {
        "english": {
            "spanish": {
                "hello": "hola",
                "world": "mundo",
                "welcome": "bienvenido",
                "thank you": "gracias",
                "goodbye": "adiós"
            },
            "french": {
                "hello": "bonjour",
                "world": "monde",
                "welcome": "bienvenue",
                "thank you": "merci",
                "goodbye": "au revoir"
            },
            "german": {
                "hello": "hallo",
                "world": "welt",
                "welcome": "willkommen",
                "thank you": "danke",
                "goodbye": "auf wiedersehen"
            }
        }
    }
    
    source_lang = "english"  # Assume English as source for this demo
    
    if target_lang in translations.get(source_lang, {}):
        words = text.lower().split()
        translated_words = []
        
        for word in words:
            # Remove punctuation for lookup
            clean_word = re.sub(r'[^\w\s]', '', word)
            
            # Try to translate the word
            if clean_word in translations[source_lang][target_lang]:
                translated_word = translations[source_lang][target_lang][clean_word]
                
                # Preserve capitalization
                if word[0].isupper():
                    translated_word = translated_word.capitalize()
                
                translated_words.append(translated_word)
            else:
                # Keep original word if no translation available
                translated_words.append(word)
        
        translated_text = ' '.join(translated_words)
        state["translated_text"] = translated_text
    else:
        # If target language not supported, keep original
        state["translated_text"] = text
    
    # Add processing metadata
    state.setdefault("metadata", {}).update({
        "translation_applied": True,
        "translation_timestamp": str(datetime.datetime.now()),
        "translation_config": {
            "source_language": source_lang,
            "target_language": target_lang
        }
    })
    
    return state


def send_email(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mock email sending function.
    In a real application, this would connect to an email API.
    """
    config = state.get("config", {})
    text = state.get("text", "")
    
    # Get email parameters from config
    recipient = config.get("recipient", "user@example.com")
    subject = config.get("subject", "Message from FlowGPT")
    
    # Mock sending email
    email_result = {
        "success": True,
        "recipient": recipient,
        "subject": subject,
        "body": text,
        "sent_at": str(datetime.datetime.now())
    }
    
    # Add email result to state
    state["email_result"] = email_result
    
    # Add processing metadata
    state.setdefault("metadata", {}).update({
        "email_sent": True,
        "email_timestamp": str(datetime.datetime.now()),
    })
    
    return state


# Function mapping for node types
NODE_FUNCTIONS = {
    "clean_text": clean_text,
    "uppercase": convert_to_uppercase,
    "summary": basic_summary,
    "translate": translate,
    "email": send_email,
} 