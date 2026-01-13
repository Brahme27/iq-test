"""
MISIC AI Grader
===============
LangChain + Gemini Pro integration for advisory scoring.

This module provides AI-assisted scoring suggestions for verbal subtests.
The AI is ADVISORY ONLY - the examiner must confirm all final scores.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class AIGraderConfig:
    """Configuration for the AI grader."""
    api_key: str
    model_name: str = "gemini-1.5-flash"
    temperature: float = 0.1  # Low temperature for consistent scoring
    max_tokens: int = 500


@dataclass
class ScoringCriteria:
    """Scoring criteria for a subtest item."""
    item_number: int
    question: str
    max_score: int
    score_0_criteria: str
    score_1_criteria: str
    score_2_criteria: Optional[str] = None
    examples: Optional[Dict[int, list]] = None


@dataclass
class AIGraderResponse:
    """Response from the AI grader."""
    suggested_score: int
    rationale: str
    confidence: str  # "high", "medium", "low"
    raw_response: Optional[str] = None


class AIGrader:
    """
    AI-assisted grading for MISIC verbal subtests.
    
    Uses LangChain with Google Gemini to analyze responses and suggest scores.
    All suggestions must be confirmed by the examiner.
    """
    
    def __init__(self, config: AIGraderConfig):
        """
        Initialize the AI grader.
        
        Args:
            config: Configuration including API key and model settings
        """
        self.config = config
        self._model = None
        self._chain = None
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Initialize the LangChain + Gemini model."""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import StrOutputParser
            
            # Set API key
            os.environ["GOOGLE_API_KEY"] = self.config.api_key
            
            # Initialize model
            self._model = ChatGoogleGenerativeAI(
                model=self.config.model_name,
                temperature=self.config.temperature,
                max_output_tokens=self.config.max_tokens,
            )
            
            # Create prompt template
            self._prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert clinical psychologist assistant helping to score MISIC (Malin's Intelligence Scale for Indian Children) verbal responses.

Your task is to analyze a child's response and suggest an appropriate score based on the provided criteria.

IMPORTANT RULES:
1. Be conservative in scoring - when in doubt, suggest the lower score
2. Consider cultural context for Indian children
3. Provide clear rationale for your suggestion
4. Your suggestion is ADVISORY ONLY - the examiner makes the final decision

Respond in this exact format:
SUGGESTED_SCORE: [0, 1, or 2]
CONFIDENCE: [high/medium/low]
RATIONALE: [Your explanation]"""),
                ("human", """Subtest: {subtest_name}
Question #{item_number}: {question}

Scoring Criteria:
- Score 0: {score_0}
- Score 1: {score_1}
{score_2_line}

Child's Response: "{response}"

Please analyze and provide your scoring suggestion.""")
            ])
            
            # Create chain
            self._chain = self._prompt | self._model | StrOutputParser()
            
        except ImportError as e:
            print(f"Warning: LangChain/Gemini imports failed: {e}")
            self._model = None
            self._chain = None
    
    def is_available(self) -> bool:
        """Check if the AI grader is available and properly configured."""
        return self._chain is not None and bool(self.config.api_key)
    
    def grade_response(
        self,
        subtest_name: str,
        item_number: int,
        question: str,
        response: str,
        score_0: str,
        score_1: str,
        score_2: Optional[str] = None
    ) -> AIGraderResponse:
        """
        Get an AI scoring suggestion for a response.
        
        Args:
            subtest_name: Name of the subtest (e.g., "Vocabulary")
            item_number: Item number being scored
            question: The question asked
            response: The child's response
            score_0: Criteria for score of 0
            score_1: Criteria for score of 1
            score_2: Criteria for score of 2 (optional, for 0-2 items)
            
        Returns:
            AIGraderResponse with suggested score and rationale
        """
        if not self.is_available():
            return AIGraderResponse(
                suggested_score=0,
                rationale="AI grader not available. Please score manually.",
                confidence="low",
                raw_response=None
            )
        
        try:
            # Prepare score 2 line
            score_2_line = f"- Score 2: {score_2}" if score_2 else ""
            
            # Invoke chain
            result = self._chain.invoke({
                "subtest_name": subtest_name,
                "item_number": item_number,
                "question": question,
                "response": response,
                "score_0": score_0,
                "score_1": score_1,
                "score_2_line": score_2_line
            })
            
            # Parse response
            return self._parse_response(result)
            
        except Exception as e:
            return AIGraderResponse(
                suggested_score=0,
                rationale=f"AI grader error: {str(e)}. Please score manually.",
                confidence="low",
                raw_response=str(e)
            )
    
    def _parse_response(self, response: str) -> AIGraderResponse:
        """Parse the AI response into structured format."""
        suggested_score = 0
        confidence = "low"
        rationale = response
        
        lines = response.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith("SUGGESTED_SCORE:"):
                try:
                    score_str = line.replace("SUGGESTED_SCORE:", "").strip()
                    suggested_score = int(score_str)
                except ValueError:
                    pass
            elif line.startswith("CONFIDENCE:"):
                confidence = line.replace("CONFIDENCE:", "").strip().lower()
            elif line.startswith("RATIONALE:"):
                rationale = line.replace("RATIONALE:", "").strip()
        
        return AIGraderResponse(
            suggested_score=suggested_score,
            rationale=rationale,
            confidence=confidence,
            raw_response=response
        )


# Fallback for when AI is not available
class ManualGrader:
    """Fallback grader when AI is not available."""
    
    @staticmethod
    def get_suggestion(score_options: list) -> str:
        """Return a prompt for manual scoring."""
        options = ", ".join(str(s) for s in score_options)
        return f"Please select a score from: {options}"


def create_grader(api_key: Optional[str] = None) -> AIGrader:
    """
    Factory function to create an AI grader.
    
    Args:
        api_key: Google Gemini API key (optional)
        
    Returns:
        AIGrader instance (may be inactive if no API key)
    """
    config = AIGraderConfig(
        api_key=api_key or "",
        model_name="gemini-1.5-flash",
        temperature=0.1
    )
    return AIGrader(config)
