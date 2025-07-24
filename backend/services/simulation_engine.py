"""
AI Simulation Engine
Handles complex AI logic for multi-persona interactions, goal validation, and adaptive hints
"""

import openai
import json
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import os

class SimulationEngine:
    """Core AI engine for sequential timeline simulations"""
    
    def __init__(self):
        self.openai_client = openai
        self.openai_client.api_key = os.getenv("OPENAI_API_KEY")
        self.default_model = "gpt-4o"
        
    def generate_persona_response(
        self,
        persona_data: Dict[str, Any],
        scene_data: Dict[str, Any],
        user_message: str,
        conversation_history: List[Dict[str, str]],
        attempt_number: int = 1
    ) -> Tuple[str, float]:
        """Generate AI persona response with context awareness"""
        
        start_time = time.time()
        
        # Build persona context
        persona_context = self._build_persona_context(persona_data, scene_data, attempt_number)
        
        # Build conversation context
        messages = [{"role": "system", "content": persona_context}]
        
        # Add conversation history (limit to last 8 messages for context window)
        for msg in conversation_history[-8:]:
            messages.append(msg)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.default_model,
                messages=messages,
                max_tokens=400,
                temperature=0.7,
                presence_penalty=0.1,  # Encourage varied responses
                frequency_penalty=0.1
            )
            
            ai_response = response.choices[0].message.content
            processing_time = time.time() - start_time
            
            return ai_response, processing_time
            
        except Exception as e:
            raise Exception(f"AI persona response generation failed: {str(e)}")
    
    def validate_goal_achievement(
        self,
        scene_data: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        current_attempt: int,
        max_attempts: int
    ) -> Dict[str, Any]:
        """Validate if scene goal has been achieved using AI evaluation"""
        
        # Build evaluation context
        evaluation_prompt = self._build_goal_evaluation_prompt(
            scene_data, conversation_history, current_attempt, max_attempts
        )
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": evaluation_prompt}],
                max_tokens=300,
                temperature=0.2,  # Lower temperature for more consistent evaluation
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate response structure
            required_fields = ["goal_achieved", "confidence_score", "reasoning", "next_action"]
            if not all(field in result for field in required_fields):
                raise ValueError("Invalid AI evaluation response structure")
            
            # Ensure confidence score is within valid range
            result["confidence_score"] = max(0.0, min(1.0, float(result["confidence_score"])))
            
            return result
            
        except Exception as e:
            # Fallback evaluation if AI fails
            return {
                "goal_achieved": False,
                "confidence_score": 0.0,
                "reasoning": f"AI evaluation failed: {str(e)}",
                "next_action": "continue",
                "hint_message": None
            }
    
    def generate_adaptive_hint(
        self,
        scene_data: Dict[str, Any],
        persona_data: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        attempt_number: int,
        hint_level: str = "subtle"
    ) -> str:
        """Generate contextual hints based on user progress"""
        
        hint_prompt = f"""As {persona_data['name']}, a {persona_data['role']}, provide a helpful hint to guide the user toward the scene goal.

SCENE GOAL: {scene_data.get('user_goal', 'Not specified')}

SCENE CONTEXT: {scene_data.get('description', '')}

CONVERSATION SO FAR:
{self._format_conversation_for_ai(conversation_history)}

ATTEMPT NUMBER: {attempt_number}
HINT LEVEL: {hint_level} (subtle, direct, explicit)

Guidelines:
- Stay in character as {persona_data['name']}
- Provide a hint that matches the hint level:
  * subtle: Gentle nudge through natural conversation
  * direct: Clear guidance without giving away the answer
  * explicit: More specific direction when user is really stuck
- Keep it conversational and realistic
- Don't break the business simulation immersion
- Limit to 2-3 sentences

Generate a helpful hint:"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": hint_prompt}],
                max_tokens=200,
                temperature=0.6
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            # Fallback hint
            return f"As {persona_data['name']}, I'd suggest taking a step back and thinking about what information you might need to achieve your goal in this situation."
    
    def generate_scene_summary(
        self,
        scene_data: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        goal_achieved: bool,
        forced_progression: bool = False
    ) -> str:
        """Generate a summary when transitioning between scenes"""
        
        summary_prompt = f"""Generate a brief summary of the user's performance in this business simulation scene.

SCENE: {scene_data.get('title', 'Unknown Scene')}
GOAL: {scene_data.get('user_goal', 'Not specified')}
GOAL ACHIEVED: {goal_achieved}
FORCED PROGRESSION: {forced_progression}

CONVERSATION SUMMARY:
{self._format_conversation_for_ai(conversation_history[-10:])}  # Last 10 messages

Create a 2-3 sentence summary that:
- Acknowledges what the user accomplished
- Notes key insights or missed opportunities
- Encourages progression to the next scene
- Maintains a supportive, educational tone

Summary:"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": summary_prompt}],
                max_tokens=150,
                temperature=0.5
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            # Fallback summary
            status = "achieved your goal" if goal_achieved else "made progress"
            return f"You {status} in this scene. Let's continue to the next part of the simulation."
    
    def calculate_interaction_quality(
        self,
        conversation_history: List[Dict[str, str]],
        scene_goal: str
    ) -> float:
        """Calculate the quality of user interactions using AI analysis"""
        
        if not conversation_history:
            return 0.0
        
        quality_prompt = f"""Analyze the quality of the user's interactions in this business simulation.

SCENE GOAL: {scene_goal}

CONVERSATION:
{self._format_conversation_for_ai(conversation_history)}

Rate the interaction quality on a scale of 0.0 to 1.0 based on:
- Relevance of questions and responses to the business context
- Professional communication style
- Strategic thinking demonstrated
- Engagement with the personas
- Progress toward the goal

Respond with only a number between 0.0 and 1.0:"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": quality_prompt}],
                max_tokens=10,
                temperature=0.2
            )
            
            score_text = response.choices[0].message.content.strip()
            score = float(score_text)
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            # Fallback to basic quality calculation
            user_messages = [msg for msg in conversation_history if msg.get("role") == "user"]
            if not user_messages:
                return 0.0
            
            # Simple quality heuristic based on message length and count
            avg_length = sum(len(msg["content"]) for msg in user_messages) / len(user_messages)
            length_score = min(1.0, avg_length / 100)  # Normalize to 0-1
            
            return length_score * 0.7  # Conservative fallback score
    
    def _build_persona_context(
        self,
        persona_data: Dict[str, Any],
        scene_data: Dict[str, Any],
        attempt_number: int
    ) -> str:
        """Build comprehensive persona context for AI"""
        
        personality_traits = persona_data.get('personality_traits', {})
        traits_text = ", ".join([f"{trait}: {score}/10" for trait, score in personality_traits.items()])
        
        context = f"""You are {persona_data['name']}, a {persona_data['role']} in this business simulation.

PERSONA BACKGROUND:
{persona_data.get('background', 'No background provided')}

YOUR RELATIONSHIP TO THIS CASE:
{persona_data.get('correlation', 'No specific correlation provided')}

PERSONALITY TRAITS: {traits_text}

PRIMARY GOALS: {', '.join(persona_data.get('primary_goals', []))}

CURRENT SCENE CONTEXT:
Title: {scene_data.get('title', 'Unknown Scene')}
Description: {scene_data.get('description', 'No description')}
User Goal: {scene_data.get('user_goal', 'No specific goal')}

ATTEMPT NUMBER: {attempt_number}

SIMULATION INSTRUCTIONS:
- Stay completely in character as {persona_data['name']}
- Respond naturally based on your role, background, and personality
- Help guide the user toward their goal through realistic business interaction
- Don't directly give away answers, but provide valuable business insights
- Keep responses concise and professional (2-4 sentences typically)
- If the user seems stuck, provide subtle hints through natural conversation
- Adapt your communication style to your personality traits
- Remember this is attempt #{attempt_number} - adjust your helpfulness accordingly"""
        
        # Add attempt-specific guidance
        if attempt_number > 3:
            context += "\n- The user has made several attempts, so be more helpful and direct"
        elif attempt_number > 1:
            context += "\n- The user has tried before, so provide gentle guidance"
        
        return context
    
    def _build_goal_evaluation_prompt(
        self,
        scene_data: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        current_attempt: int,
        max_attempts: int
    ) -> str:
        """Build comprehensive goal evaluation prompt"""
        
        return f"""Evaluate whether the user has achieved the scene goal based on their conversation with AI personas.

SCENE DETAILS:
Title: {scene_data.get('title', 'Unknown')}
Description: {scene_data.get('description', 'No description')}
User Goal: {scene_data.get('user_goal', 'No specific goal')}

GOAL CRITERIA: {json.dumps(scene_data.get('goal_criteria', []))}

CONVERSATION HISTORY:
{self._format_conversation_for_ai(conversation_history)}

PROGRESS TRACKING:
- Current Attempt: {current_attempt}
- Maximum Attempts: {max_attempts}
- Success Threshold: {scene_data.get('success_threshold', 0.7)}

EVALUATION INSTRUCTIONS:
Analyze the conversation and determine:
1. Has the user achieved the scene goal? Consider both explicit achievements and demonstrated understanding
2. Confidence score (0.0-1.0) - how certain are you about the achievement?
3. Brief reasoning for your decision (2-3 sentences)
4. Next recommended action:
   - "continue": User should keep trying in current scene
   - "progress": User achieved goal, move to next scene
   - "hint": User needs guidance but hasn't reached max attempts
   - "force_progress": Max attempts reached, force progression with summary

5. If next_action is "hint", provide a helpful hint message

Respond in valid JSON format:
{{
    "goal_achieved": boolean,
    "confidence_score": float,
    "reasoning": "string",
    "next_action": "string",
    "hint_message": "string or null"
}}"""
    
    def _format_conversation_for_ai(self, conversation_history: List[Dict[str, str]]) -> str:
        """Format conversation history for AI prompts"""
        
        if not conversation_history:
            return "No conversation yet."
        
        formatted_messages = []
        for msg in conversation_history:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            
            if role == "user":
                formatted_messages.append(f"User: {content}")
            elif role == "assistant":
                sender = msg.get("sender_name", "AI")
                formatted_messages.append(f"{sender}: {content}")
            else:
                formatted_messages.append(f"System: {content}")
        
        return "\n".join(formatted_messages)

# Global simulation engine instance
simulation_engine = SimulationEngine() 