# app/profile_builder.py Extracts structured profile from candidate resume using LLM.

import logging
import json
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfileBuilder:
    def __init__(self):
        logger.info("Initializing ProfileBuilder...")

        try:
            self.llm = ChatOpenAI(
                base_url="http://host.docker.internal:8001/v1",
                api_key="llama",  # ignored, but required by interface
                temperature=0.1,
                max_tokens=512,
                model="mistral"
            )
            logger.info("Connected to local LLM server (ChatOpenAI with llama.cpp backend).")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise

        try:
            self.template = PromptTemplate.from_template(
                """
                You are an expert resume analyst. Extract this resume into structured JSON with keys:
                "name", "email", "skills", "education", "experience", "projects", "certifications"

                Resume:
                {resume_text}
                """
            )
            logger.info("Prompt template initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize prompt template: {e}")
            raise

    def build_profile(self, resume_text):
        logger.info("Building profile from resume text...")
        
        try:
            prompt = self.template.format(resume_text=resume_text)
            logger.debug(f"Generated prompt: {prompt[:500]}...")  # First 500 chars
        except Exception as e:
            logger.error(f"Failed to format prompt: {e}")
            raise

        try:
            response = self.llm.invoke(prompt)
            logger.info("Received response from LLM.")
            logger.debug(f"LLM raw response: {getattr(response, 'content', str(response))}")
        except Exception as e:
            logger.error(f"Failed to invoke LLM: {e}")
            raise

        try:
            if isinstance(response, AIMessage):
             response_text = response.content
            else:
             response_text = str(response)

            profile = json.loads(response_text)
            logger.info("LLM response successfully parsed as JSON.")
            logger.debug(f"Structured profile: {profile}")
            return profile
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response into JSON: {e}")
            raise ValueError("LLM response was not valid JSON.") from e



