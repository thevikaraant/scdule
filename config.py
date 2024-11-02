from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys and Authentication
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# LangChain Configuration
LANGCHAIN_CONFIG: Dict[str, Any] = {
    "model_name": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 150
}

# Messaging Platform Settings
PLATFORMS = {
    "whatsapp": {
        "enabled": True,
        "api_url": "https://api.whatsapp.com/v1/messages",
        "retry_attempts": 3,
        "timeout": 30
    },
    "telegram": {
        "enabled": False,
        "api_url": f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}",
        "retry_attempts": 3,
        "timeout": 30
    }
}

# Scheduling Configuration
SCHEDULE_CONFIG = {
    "timezone": "UTC",
    "max_scheduled_messages": 100,
    "min_schedule_interval": 5,  # minimum minutes between scheduled messages
    "max_days_ahead": 7  # maximum days in advance to schedule
}

# Error Messages
ERROR_MESSAGES = {
    "invalid_time": "Invalid time format. Please use HH:MM or HH:MM AM/PM format.",
    "scheduling_failed": "Failed to schedule message. Please try again.",
    "platform_error": "Error connecting to messaging platform.",
    "missing_recipient": "Please specify a recipient for the message.",
    "future_only": "Messages can only be scheduled for future times.",
    "too_far_ahead": f"Messages cannot be scheduled more than {SCHEDULE_CONFIG['max_days_ahead']} days in advance."
}

# Logging Configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
        "file": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.FileHandler",
            "filename": "chatbot.log",
            "mode": "a",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default", "file"],
            "level": "INFO",
            "propagate": True
        }
    }
}

# Development/Production environment
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
ENV = os.getenv("ENV", "development")

def validate_config() -> bool:
    """Validate that all required configuration is present and valid"""
    try:
        # Validate API Keys
        required_vars = [
            ("OPENAI_API_KEY", OPENAI_API_KEY),
        ]
        
        if PLATFORMS["whatsapp"]["enabled"]:
            required_vars.append(("WHATSAPP_API_KEY", WHATSAPP_API_KEY))
        
        if PLATFORMS["telegram"]["enabled"]:
            required_vars.append(("TELEGRAM_BOT_TOKEN", TELEGRAM_BOT_TOKEN))
        
        missing_vars = [var_name for var_name, var_value in required_vars if not var_value]
        
        if missing_vars:
            print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
            return False
            
        # Validate LangChain Configuration
        if LANGCHAIN_CONFIG["max_tokens"] <= 0:
            print("ERROR: max_tokens must be greater than 0")
            return False
            
        if not (0 <= LANGCHAIN_CONFIG["temperature"] <= 1):
            print("ERROR: temperature must be between 0 and 1")
            return False
            
        # Validate Schedule Configuration
        if SCHEDULE_CONFIG["min_schedule_interval"] < 1:
            print("ERROR: min_schedule_interval must be at least 1 minute")
            return False
            
        if SCHEDULE_CONFIG["max_days_ahead"] < 1:
            print("ERROR: max_days_ahead must be at least 1 day")
            return False
            
        # Validate Platform Settings
        for platform, settings in PLATFORMS.items():
            if settings["enabled"]:
                if settings["retry_attempts"] < 1:
                    print(f"ERROR: {platform} retry_attempts must be at least 1")
                    return False
                if settings["timeout"] < 1:
                    print(f"ERROR: {platform} timeout must be at least 1 second")
                    return False
                
        print("Config validation successful!")
        return True
        
    except Exception as e:
        print(f"ERROR: Configuration validation failed: {str(e)}")
        return False

def get_debug_info() -> dict:
    """Return debug information about the current configuration"""
    return {
        "environment": ENV,
        "debug_mode": DEBUG,
        "enabled_platforms": [
            platform for platform, settings in PLATFORMS.items() 
            if settings["enabled"]
        ],
        "timezone": SCHEDULE_CONFIG["timezone"],
        "logging_handlers": list(LOGGING_CONFIG["handlers"].keys()),
        "model": LANGCHAIN_CONFIG["model_name"]
    }

if __name__ == "__main__":
    # Run validation when config is run directly
    if validate_config():
        debug_info = get_debug_info()
        print("\nCurrent Configuration:")
        for key, value in debug_info.items():
            print(f"{key}: {value}")

