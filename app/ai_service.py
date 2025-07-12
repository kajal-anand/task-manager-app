import google.generativeai as genai
from .config import Config
import logging
from .models import TaskPriority
from typing import List
import json

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        """Initialize the Gemini API client with API key from configuration."""
        try:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Gemini API client initialized successfully (model: gemini-1.5-flash)")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API client: {str(e)}", exc_info=True)
            raise

    async def prioritize_task(self, title: str, description: str = "") -> TaskPriority:
        """Analyze task and assign priority using Gemini 1.5 Flash API."""
        try:
            prompt = (
                f"Analyze the following task and classify its priority as 'Low', 'Medium', "
                f"'High', or 'Critical'. Task Title: {title}, Description: {description}. "
                f"Return only the priority level."
            )
            logger.info(f"Sending priority prompt to Gemini: {prompt}")
            
            response = await self.model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 20,
                    "response_mime_type": "text/plain"
                }
            )
            
            priority = response.text.strip().lower()
            if priority not in [e.value for e in TaskPriority]:
                logger.warning(f"Invalid priority received: {priority}, defaulting to LOW")
                return TaskPriority.LOW
            logger.info(f"Priority assigned: {priority}")
            return TaskPriority(priority)
            
        except Exception as e:
            logger.error(f"Gemini API prioritization failed: {str(e)}", exc_info=True)
            return TaskPriority.LOW

    async def generate_tags(self, title: str, description: str = "") -> List[str]:
        """Generate up to 3 relevant tags using Gemini 1.5 Flash API."""
        try:
            prompt = (
                f"Based on the following task, generate up to 3 relevant one-word tags from the "
                f"following list: [Work, Personal, Health, Finance, Learning, Urgent, Shopping]. "
                f"Return them as a JSON array of strings. Task Title: {title}, Description: {description}."
            )
            logger.info(f"Sending tag prompt to Gemini: {prompt}")
            
            response = await self.model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 50,
                    "response_mime_type": "application/json"
                }
            )
            
            
            tags = json.loads(response.text.strip())
            valid_tags = ['work', 'personal', 'health', 'finance', 'learning', 'urgent', 'shopping']
            tags = [tag.lower() for tag in tags if isinstance(tag, str) and tag.lower() in valid_tags]
            logger.info(f"Tags generated: {tags}")
            return tags[:3]  # Ensure max 3 tags
            
        except Exception as e:
            logger.error(f"Gemini API tag generation failed: {str(e)}", exc_info=True)
            return []