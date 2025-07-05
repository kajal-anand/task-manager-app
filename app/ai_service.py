# import openai
# from .config import Config
# import logging
# from .models import TaskPriority

# logger = logging.getLogger(__name__)

# class AIService:
#     def __init__(self):
#         openai.api_key = Config.OPENAI_API_KEY

#     async def prioritize_task(self, title: str, description: str = "") -> TaskPriority:
#         """Analyze task and assign priority using OpenAI API."""
#         try:
#             prompt = (
#                 f"Analyze the following task and classify its priority as 'Low', 'Medium', "
#                 f"'High', or 'Critical'. Task Title: {title}, Description: {description}. "
#                 f"Return only the priority level."
#             )
#             print("PROMPT FOR OPENai : \n", prompt)
            
#             response = await openai.ChatCompletion.acreate(
#                 model="gpt-3.5-turbo",
#                 messages=[{"role": "user", "content": prompt}],
#                 timeout=Config.API_TIMEOUT
#             )
#             print("response from OPENAI :---\n", response)
#             priority = response.choices[0].message.content.strip().lower()
#             if priority not in [e.value for e in TaskPriority]:
#                 logger.warning(f"Invalid priority received: {priority}, defaulting to LOW")
#                 return TaskPriority.LOW
#             return TaskPriority(priority)
            
#         except Exception as e:
#             logger.error(f"AI prioritization failed: {str(e)}", exc_info=True)
#             return TaskPriority.LOW












# import logging
# import asyncio
# from enum import Enum
# from openai import AsyncOpenAI

# # Setup Logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Dummy Config
# class Config:
#     OPENAI_API_KEY = ""
#     API_TIMEOUT = 15

# # Enum for task priority
# class TaskPriority(str, Enum):
#     LOW = "low"
#     MEDIUM = "medium"
#     HIGH = "high"
#     CRITICAL = "critical"

# # AI Service
# class AIService:
#     def __init__(self):
#         self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)

#     async def prioritize_task(self, title: str, description: str = "") -> TaskPriority:
#         try:
#             prompt = (
#                 f"Analyze the following task and classify its priority as 'Low', 'Medium', "
#                 f"'High', or 'Critical'. Task Title: {title}, Description: {description}. "
#                 f"Return only the priority level."
#             )
#             print("PROMPT:\n", prompt)

#             response = await self.client.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 messages=[{"role": "user", "content": prompt}],
#                 timeout=Config.API_TIMEOUT
#             )
#             print("RESPONSE:\n", response)

#             priority = response.choices[0].message.content.strip().lower()
#             if priority not in [e.value for e in TaskPriority]:
#                 logger.warning(f"Invalid priority received: {priority}, defaulting to LOW")
#                 return TaskPriority.LOW

#             return TaskPriority(priority)

#         except Exception as e:
#             logger.error(f"AI prioritization failed: {str(e)}", exc_info=True)
#             return TaskPriority.LOW

# # Usage Example
# if __name__ == "__main__":
#     async def main():
#         ai_service = AIService()
#         title = "Fix production server outage"
#         description = "Client has reported that their production environment is down since morning."
#         priority = await ai_service.prioritize_task(title, description)
#         print(f"\nPredicted Priority: {priority}")

#     asyncio.run(main())



import google.generativeai as genai
from .config import Config
import logging
from .models import TaskPriority

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        """Initialize the Gemini API client with API key from configuration."""
        try:
            genai.configure(api_key=Config.GEMINI_API_KEY)  # Using same env variable for compatibility
            self.primary_model = genai.GenerativeModel('gemini-2.5-pro')
            self.fallback_model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Gemini API clients initialized successfully (primary: gemini-2.5-pro, fallback: gemini-1.5-flash)")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API client: {str(e)}", exc_info=True)
            raise

    async def prioritize_task(self, title: str, description: str = "") -> TaskPriority:
        """Analyze task and assign priority using Gemini 2.5 Pro API, with fallback to 1.5 Flash."""
        prompt = (
            f"Analyze the following task and classify its priority as 'Low', 'Medium', "
            f"'High', or 'Critical'. Task Title: {title}, Description: {description}. "
            f"Return only the priority level."
        )
        
        for model, model_name in [(self.primary_model, "gemini-2.5-pro"), (self.fallback_model, "gemini-1.5-flash")]:
            try:
                logger.info(f"Sending prompt to {model_name}: {prompt}")
                response = await model.generate_content_async(
                    prompt,
                    generation_config={
                        "temperature": 0.7,
                        "max_output_tokens": 20,
                        "response_mime_type": "text/plain"
                    }
                )
                
                priority = response.text.strip().lower()
                if priority not in [e.value for e in TaskPriority]:
                    logger.warning(f"Invalid priority received from {model_name}: {priority}, defaulting to LOW")
                    return TaskPriority.LOW
                logger.info(f"Priority assigned by {model_name}: {priority}")
                return TaskPriority(priority)
                
            except Exception as e:
                logger.error(f"{model_name} API prioritization failed: {str(e)}", exc_info=True)
                if "429" in str(e):
                    logger.warning(f"Quota exceeded for {model_name}. Trying next model." if model_name == "gemini-2.5-pro" else "All models exceeded quota.")
                if model_name == "gemini-1.5-flash":
                    logger.error("Fallback model failed. Defaulting to LOW priority.")
                    return TaskPriority.LOW
                continue
                
        return TaskPriority.LOW

