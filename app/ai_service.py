import google.generativeai as genai
from .config import Config
import logging
from .models import TaskPriority
from typing import List

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
            
            import json
            tags = json.loads(response.text.strip())
            valid_tags = ['work', 'personal', 'health', 'finance', 'learning', 'urgent', 'shopping']
            tags = [tag.lower() for tag in tags if isinstance(tag, str) and tag.lower() in valid_tags]
            logger.info(f"Tags generated: {tags}")
            return tags[:3]
            
        except Exception as e:
            logger.error(f"Gemini API tag generation failed: {str(e)}", exc_info=True)
            return []

    async def generate_subtasks(self, title: str, description: str = "") -> List[str]:
        """Generate sub-tasks for a given task using Gemini 1.5 Flash API."""
        try:
            prompt = (
                f"You are a project manager. Break down the following task into a list of smaller, actionable sub-tasks. "
                f"Return the result as a JSON array of simple task titles. "
                f"Task Title: {title}, Description: {description}."
            )
            logger.info(f"Sending sub-task prompt to Gemini: {prompt}")
            
            response = await self.model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 200,
                    "response_mime_type": "application/json"
                }
            )
            
            import json
            subtasks = json.loads(response.text.strip())
            if not isinstance(subtasks, list) or not all(isinstance(t, str) for t in subtasks):
                logger.warning(f"Invalid sub-tasks format received: {subtasks}, returning empty list")
                return []
            logger.info(f"Sub-tasks generated: {subtasks}")
            return subtasks[:5]
            
        except Exception as e:
            logger.error(f"Gemini API sub-task generation failed: {str(e)}", exc_info=True)
            return []