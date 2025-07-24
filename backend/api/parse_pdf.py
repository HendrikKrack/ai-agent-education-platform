import os
import asyncio
import json
import re
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import httpx
from dotenv import load_dotenv
import openai
from typing import List
from PyPDF2 import PdfReader
from datetime import datetime
import string

from database.connection import get_db
from database.models import Scenario, ScenarioPersona, ScenarioScene, ScenarioFile, scene_personas

# Explicitly load the .env file from the backend directory (parent of api)
backend_env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../.env'))
load_dotenv(backend_env_path)
print(f"[DEBUG] Loading .env from: {backend_env_path}")

LLAMAPARSE_API_KEY = os.getenv("LLAMAPARSE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if LLAMAPARSE_API_KEY:
    print(f"[DEBUG] LLAMAPARSE_API_KEY loaded: {LLAMAPARSE_API_KEY[:6]}...{LLAMAPARSE_API_KEY[-4:]}")
else:
    print("[DEBUG] LLAMAPARSE_API_KEY loaded: None")
if OPENAI_API_KEY:
    print(f"[DEBUG] OPENAI_API_KEY loaded: {OPENAI_API_KEY[:6]}...{OPENAI_API_KEY[-4:]}")
else:
    print("[DEBUG] OPENAI_API_KEY loaded: None")

router = APIRouter()

LLAMAPARSE_API_URL = "https://api.cloud.llamaindex.ai/api/parsing/upload"
LLAMAPARSE_JOB_URL = "https://api.cloud.llamaindex.ai/api/parsing/job"

async def extract_text_from_context_files(context_files: List[UploadFile]) -> str:
    """Extract text from context files (PDFs and TXT files)"""
    context_texts = []
    for file in context_files:
        filename = file.filename.lower()
        contents = await file.read()
        if filename.endswith('.pdf'):
            try:
                import io
                reader = PdfReader(io.BytesIO(contents))
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
                context_texts.append(f"[Context File: {file.filename}]\n{text.strip()}\n")
            except Exception as e:
                context_texts.append(f"[Context File: {file.filename}]\n[Could not extract PDF text: {e}]\n")
        elif filename.endswith('.txt'):
            try:
                text = contents.decode('utf-8', errors='ignore')
                context_texts.append(f"[Context File: {file.filename}]\n{text.strip()}\n")
            except Exception as e:
                context_texts.append(f"[Context File: {file.filename}]\n[Could not extract TXT text: {e}]\n")
        else:
            context_texts.append(f"[Context File: {file.filename}]\n[Unsupported file type]\n")
    return "\n".join(context_texts)

async def parse_with_llamaparse(file: UploadFile) -> str:
    """Send a file to LlamaParse and return the parsed markdown content."""
    if not LLAMAPARSE_API_KEY:
        raise HTTPException(status_code=500, detail="LlamaParse API key not configured.")
    
    try:
        # Read file contents once and store them
        contents = await file.read()
        headers = {"Authorization": f"Bearer {LLAMAPARSE_API_KEY}"}
        files = {"file": (file.filename, contents, file.content_type)}
        
        print(f"[DEBUG] Sending {file.filename} to LlamaParse...")
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            upload_response = await client.post(LLAMAPARSE_API_URL, headers=headers, files=files)
            upload_response.raise_for_status()
            
            job_data = upload_response.json()
            print(f"[DEBUG] LlamaParse upload response: {job_data}")
            
            if not job_data or not isinstance(job_data, dict):
                raise HTTPException(status_code=500, detail="Invalid response from LlamaParse")
            
            # Get job ID
            job_id = job_data.get("id") or job_data.get("job_id") or job_data.get("jobId")
            if not job_id:
                raise HTTPException(status_code=500, detail=f"No job ID in LlamaParse response. Got keys: {list(job_data.keys())}")
            
            print(f"[DEBUG] Got job ID: {job_id}")
            
            # Poll for completion
            for attempt in range(60):
                print(f"[DEBUG] Polling attempt {attempt + 1}/60 for job {job_id}")
                status_response = await client.get(f"{LLAMAPARSE_JOB_URL}/{job_id}", headers=headers)
                status_response.raise_for_status()
                status_data = status_response.json()
                
                status = status_data.get("status")
                if status in ["COMPLETED", "SUCCESS"]:
                    print(f"[DEBUG] Job {job_id} completed, retrieving result...")
                    # Try to get markdown result
                    try:
                        markdown_response = await client.get(f"{LLAMAPARSE_JOB_URL}/{job_id}/result/markdown", headers=headers)
                        markdown_response.raise_for_status()
                        result = markdown_response.text
                        print(f"[DEBUG] Retrieved markdown result, length: {len(result)}")
                        return result
                    except Exception as e:
                        print(f"[DEBUG] Markdown retrieval failed: {e}")
                    
                    # Fallback: try text
                    try:
                        result_response = await client.get(f"{LLAMAPARSE_JOB_URL}/{job_id}/result", headers=headers)
                        result_response.raise_for_status()
                        parsed_content = result_response.json()
                        result = parsed_content.get("text", "")
                        print(f"[DEBUG] Retrieved text result, length: {len(result)}")
                        return result
                    except Exception as e:
                        print(f"[DEBUG] Text retrieval failed: {e}")
                    
                    # Final fallback: check if result is in status_data
                    if "parsed_document" in status_data:
                        parsed_doc = status_data["parsed_document"]
                        if isinstance(parsed_doc, dict) and "text" in parsed_doc:
                            result = parsed_doc["text"]
                            print(f"[DEBUG] Retrieved result from status_data, length: {len(result)}")
                            return result
                    
                    print(f"[DEBUG] No result found in any format")
                    return ""
                    
                elif status == "FAILED":
                    error_msg = status_data.get("error", "Unknown error")
                    print(f"[DEBUG] Job {job_id} failed: {error_msg}")
                    raise HTTPException(status_code=500, detail=f"LlamaParse job failed for {file.filename}: {error_msg}")
                elif status in ["PENDING", "PROCESSING"]:
                    print(f"[DEBUG] Job {job_id} still {status}, waiting 3s...")
                    await asyncio.sleep(3)
                else:
                    print(f"[DEBUG] Unknown status '{status}', waiting 3s...")
                    await asyncio.sleep(3)
            
            raise HTTPException(status_code=500, detail=f"LlamaParse job timed out for {file.filename}")
    
    except Exception as e:
        print(f"[ERROR] Exception in parse_with_llamaparse for {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to parse {file.filename}: {str(e)}")

@router.post("/api/parse-pdf/")
async def parse_pdf(
    file: UploadFile = File(...), 
    context_files: List[UploadFile] = File(default=[]),
    save_to_db: bool = False,  # Changed to False - don't auto-save
    user_id: int = 1,  # TODO: Get from authentication
    db: Session = Depends(get_db)
):
    """Main endpoint: Parse PDF and context files, then process with AI"""
    print("[DEBUG] /api/parse-pdf/ endpoint hit")
    if not LLAMAPARSE_API_KEY:
        raise HTTPException(status_code=500, detail="LlamaParse API key not configured.")
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        # Process all files in parallel
        print("[DEBUG] Starting parallel processing of all files...")
        
        # Create tasks for all files (main PDF + context files)
        tasks = []
        
        # Add main PDF task
        main_task = parse_with_llamaparse(file)
        tasks.append(("main_pdf", main_task))
        
        # Add context file tasks
        for ctx_file in context_files:
            ctx_task = parse_with_llamaparse(ctx_file)
            tasks.append((ctx_file.filename, ctx_task))
        
        print(f"[DEBUG] Created {len(tasks)} parallel tasks")
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        # Process results
        main_markdown = ""
        context_markdowns = []
        
        for i, (name, result) in enumerate(zip([name for name, _ in tasks], results)):
            if isinstance(result, Exception):
                print(f"[ERROR] Failed to process {name}: {result}")
                if name == "main_pdf":
                    raise result  # Main PDF failure is critical
                else:
                    context_markdowns.append(f"[Context File: {name}]\n[Could not extract context: {result}]\n")
            else:
                print(f"[DEBUG] Successfully processed {name}, content length: {len(result)}")
                if name == "main_pdf":
                    main_markdown = result
                else:
                    context_markdowns.append(f"[Context File: {name}]\n{result.strip()}\n")
        
        context_text = "\n".join(context_markdowns)
        print(f"[DEBUG] All files processed in parallel. Main content length: {len(main_markdown)}, Context content length: {len(context_text)}")
        
        # Pass both to process_with_ai
        print("[DEBUG] Calling process_with_ai...")
        ai_result = await process_with_ai(main_markdown, context_text)
        print("[DEBUG] AI processing completed successfully")

        # Debug: Log personas_involved for all scenes and scene_cards before saving
        for key in ["scenes", "scene_cards"]:
            if key in ai_result:
                for scene in ai_result[key]:
                    print(f"[DEBUG] Scene '{scene.get('title', scene.get('scene_title', ''))}' personas_involved: {scene.get('personas_involved', [])}")
        
        # Save to database if requested
        scenario_id = None
        if save_to_db:
            print("[DEBUG] Saving AI results to database...")
            scenario_id = await save_scenario_to_db(
                ai_result, file, context_files, main_markdown, context_text, user_id, db
            )
            print(f"[DEBUG] Scenario saved with ID: {scenario_id}")
        return {
            "status": "completed",
            "ai_result": ai_result,
            "scenario_id": scenario_id
        }
            
    except Exception as e:
        print(f"[ERROR] Exception in parse_pdf endpoint: {str(e)}")
        import traceback
        print(f"[ERROR] Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to parse PDF: {str(e)}")

def preprocess_case_study_content(raw_content: str) -> dict:
    """Pre-process the parsed content to extract clean case study information"""
    print("[DEBUG] Pre-processing case study content")
    
    # If content is a dict with markdown, extract the markdown
    if isinstance(raw_content, dict) and "markdown" in raw_content:
        content = raw_content["markdown"]
    elif isinstance(raw_content, str):
        # Check if it's a JSON string with markdown
        try:
            import json
            parsed_json = json.loads(raw_content)
            if isinstance(parsed_json, dict) and "markdown" in parsed_json:
                content = parsed_json["markdown"]
            else:
                content = raw_content
        except (json.JSONDecodeError, TypeError):
            content = raw_content
    else:
        content = raw_content
    
    print(f"[DEBUG] Raw content length: {len(content)}")
    
    # Clean up formatting artifacts
    content = content.replace('  ', ' ')  # Remove double spaces
    content = content.replace(' \n', '\n')  # Remove trailing spaces
    content = content.replace('\n ', '\n')  # Remove leading spaces
    
    # Split into lines and process
    lines = content.split('\n')
    cleaned_lines = []
    title = None
    
    # First pass: extract title from markdown headers
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Look for markdown headers (e.g., "# Title")
        if line.startswith('# '):
            title = line.replace('# ', '').strip()
            print(f"[DEBUG] Found title in markdown header: {title}")
            break
    
    # If no title found in headers, look for the first meaningful line
    if not title:
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip metadata and formatting artifacts
            if any(skip_pattern in line.upper() for skip_pattern in [
                'HARVARD BUSINESS SCHOOL', 'REV:', 'PAGE', '©', 'COPYRIGHT', 'ALL RIGHTS RESERVED',
                'DOCUMENT ID:', 'FILE:', 'CREATED:', 'MODIFIED:', '9-', 'R E V :'
            ]):
                continue
                
            # Skip lines that are just numbers, dates, or formatting
            if re.match(r'^[\d\s\-\.]+$', line):  # Just numbers, spaces, dashes, dots
                continue
                
            # Skip very short lines or all-uppercase lines
            if len(line) < 5 or line.isupper():
                continue
                
            # This looks like a title
            title = line
            print(f"[DEBUG] Found title in content: {title}")
            break
    
    # Fallback title
    if not title:
        title = "Business Case Study"

    # Clean content (only remove obvious metadata)
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Skip only the most obvious metadata lines
        if any(skip_pattern in line.upper() for skip_pattern in [
            'COPYRIGHT ENCODED', 'DOCUMENT ID:', 'FILE:', 'CREATED:', 'MODIFIED:', 
            'AUTHORIZED FOR USE ONLY', 'THIS DOCUMENT IS FOR USE ONLY BY'
        ]):
            continue
            
        # Skip lines that are just formatting artifacts
        if len(line) == 0 or re.match(r'^[\s\-\_\.]+$', line):
            continue
            
        # Keep everything else
        cleaned_lines.append(line)
    
    cleaned_content = '\n'.join(cleaned_lines)
    
    print(f"[DEBUG] Extracted title: {title}")
    print(f"[DEBUG] Cleaned content length: {len(cleaned_content)}")
    
    return {
        "title": title,
        "cleaned_content": cleaned_content
    }

async def generate_scene_image(scene_description: str, scene_title: str, scenario_id: int = 0) -> str:
    """Generate an image for a scene using OpenAI's DALL-E API"""
    print(f"[DEBUG] Generating image for scene: {scene_title}")
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # Create a focused prompt for image generation
        image_prompt = f"""
Create a professional, business-focused illustration for a business case study scenario. 
Scene: {scene_title}
Description: {scene_description}

Style: Clean, modern business illustration with professional lighting. 
Focus on the business environment and key elements mentioned in the scene.
Avoid specific faces or identifiable people - use silhouettes or generic figures.
Make it suitable for educational/corporate use.
"""
        
        print(f"[DEBUG] DALL-E prompt: {image_prompt[:200]}...")
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: client.images.generate(
                model="dall-e-3",
                prompt=image_prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
        )
        
        image_url = response.data[0].url
        print(f"[DEBUG] Generated image URL: {image_url}")
        
        # Download and save image locally if we have a scenario ID
        if scenario_id > 0:
            from utils.image_storage import download_and_save_image
            local_path = await download_and_save_image(image_url, scene_title, scenario_id)
            if local_path:
                print(f"[DEBUG] Image saved locally: {local_path}")
                return local_path
        
        return image_url
        
    except Exception as e:
        print(f"[ERROR] Image generation failed for scene '{scene_title}': {str(e)}")
        return ""  # Return empty string on failure

async def generate_scenes_with_ai(base_result: dict) -> list:
    """Generate scenes using a separate AI call based on the base case study analysis"""
    print("[DEBUG] Generating scenes with separate AI call...")
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # Extract context from the base result
        title = base_result.get("title", "Business Case Study")
        description = base_result.get("description", "")
        student_role = base_result.get("student_role", "Manager")
        key_figures = base_result.get("key_figures", [])
        
        # Create persona names list for easy reference
        persona_names = [fig.get("name", "") for fig in key_figures if fig.get("name")]
        
        scenes_prompt = f"""
Create exactly 4 interactive scenes for this business case study. Output ONLY a JSON array of scenes.

CASE CONTEXT:
Title: {title}
Student Role: {student_role}
Description: {description[:500]}...

AVAILABLE PERSONAS: {', '.join(persona_names)}

Create 4 scenes following this progression:
1. Crisis Assessment/Initial Briefing
2. Investigation/Analysis Phase  
3. Solution Development
4. Implementation/Approval

Each scene MUST have:
- title: Short descriptive name
- description: 2-3 sentences with vivid setting details for image generation
- personas_involved: Array of 2-4 actual persona names from the list above
- user_goal: Specific objective the student must achieve
- sequence_order: 1, 2, 3, or 4

Output format - ONLY this JSON array:
[
  {{
    "title": "Scene Title",
    "description": "Detailed setting description with visual elements...",
    "personas_involved": ["Actual Name 1", "Actual Name 2"],
    "user_goal": "Specific actionable goal",
    "sequence_order": 1
  }},
  ...4 scenes total
]
"""
        
        print("[DEBUG] Sending scenes generation prompt to OpenAI...")
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You generate JSON arrays of scenes. Output ONLY valid JSON array, no extra text."},
                    {"role": "user", "content": scenes_prompt}
                ],
                max_tokens=2048,
                temperature=0.3,
            )
        )
        
        scenes_text = response.choices[0].message.content.strip()
        print(f"[DEBUG] Scenes AI response: {scenes_text[:200]}...")
        
        # Extract JSON array from response
        import re
        json_match = re.search(r'(\[[\s\S]*\])', scenes_text)
        if json_match:
            scenes_json = json_match.group(1)
            scenes = json.loads(scenes_json)
            print(f"[DEBUG] Successfully parsed {len(scenes)} scenes")
            return scenes
        else:
            print("[WARNING] No JSON array found in scenes response")
            return []
            
    except Exception as e:
        print(f"[ERROR] Scene generation failed: {str(e)}")
        return []

async def process_with_ai(parsed_content: str, context_text: str = "") -> dict:
    """Process the parsed PDF content with OpenAI to extract business case study information"""
    print("[DEBUG] Processing content with OpenAI LLM")
    try:
        preprocessed = preprocess_case_study_content(parsed_content)
        title = preprocessed["title"]
        cleaned_content = preprocessed["cleaned_content"]
        
        # Prepend context files' content as most important
        if context_text.strip():
            combined_content = f"""
IMPORTANT CONTEXT FILES (most authoritative, follow these first):
{context_text}

CASE STUDY CONTENT (main PDF):
{cleaned_content}
"""
        else:
            combined_content = cleaned_content
            
        # --- AI Prompt for Scenario Extraction ---
        prompt = f"""
You are a highly structured JSON-only generator trained to analyze business case studies for college business education.

CRITICAL: You must identify ALL named individuals, companies, organizations, and significant unnamed roles mentioned within the case study narrative. Focus ONLY on characters and entities that are part of the business story being told.

Instructions for key_figures identification:
- Find ALL types of key figures that can be turned into personas, including:
  * Named individuals who are characters in the case study (people with first and last names like "John Smith", "Mary Johnson", "Wanjohi", etc.)
  * Companies and organizations mentioned in the narrative (e.g., "Kaskazi Network", "Competitors", "Suppliers")
  * Unnamed but important roles within the story (e.g., "The CEO", "The Board of Directors", "The Marketing Manager")
  * Groups and stakeholders in the narrative (e.g., "Customers", "Employees", "Shareholders", "Partners")
  * External entities mentioned in the story (e.g., "Government Agencies", "Regulatory Bodies", "Industry Analysts")
  * Any entity that influences the narrative or decision-making process within the case study
- Look for names in the format: "FirstName LastName" or "Title LastName" or "FirstName Title"
- Focus ONLY on the case study narrative content - ignore author sections, acknowledgments, footnotes, or other metadata
- Include both named and unnamed entities that are part of the business story - do not prioritize one over the other
- Even if someone/thing is mentioned only once or briefly, include them if they have a discernible role in the narrative
- Do not skip anyone/anything based on perceived importance - include ALL relevant figures and entities from the story
- CRITICAL: Do NOT include the student, the player, or the role/position the student is playing (as specified in "student_role") in the key_figures array. Only include non-player characters (NPCs) and entities from the business narrative. The player/student role must be excluded even if mentioned by name or title in the content.

IMPORTANT SCENE GENERATION RULES:
- For each scene:
  * The personas_involved array must list only non-student figures (from key_figures) who are actively referenced in the scene_description.
  * The scene_description must always mention, in-depth and narratively, at least one non-student persona from the personas/key_figures list. The figure(s) must be woven into the scene in a way that makes narrative sense and advances the business scenario. The description should be multi-paragraph, detailed, and immersive, not superficial.
  * Do not include the main character (student role) in personas_involved.

Your task is to analyze the following business case study content and return a JSON object with exactly the following fields:

{{
  "title": "<The exact title of the business case study>",
  "description": "<A highly comprehensive, multi-paragraph, and in-depth background that includes: 1) the business context, history, and market environment, 2) the main challenges, decisions, and their implications, 3) an explicit and prominent statement that the student will be tackling the case study as the primary decision-maker or central figure (include their name/title if available), 4) clear references to the key figures, their roles, and their relationships to the student’s role, and 5) a synthesis of deeper context, connections, and business analysis inferred from the case study. The description should be analytical, engaging, and written in a professional tone suitable for business education.>",
  "student_role": "<The specific role or position the student will assume in this case study. This should be the primary decision-maker or central figure in the case study (e.g., 'CEO', 'Marketing Manager', 'Consultant', 'Founder', etc.). This person/role will NOT be included in key_figures since the student will be playing this role.>",
  "key_figures": [
    {{
      "name": "<Full name of figure (e.g., 'John Smith', 'Wanjohi', 'Lisa Mwezi Schuepbach'), or descriptive title if unnamed (e.g., 'The Board of Directors', 'Competitor CEO', 'Industry Analyst')>",
      "role": "<Their role or inferred role. If unknown, use 'Unknown'>",
      "correlation": "<A brief explanation of this figure's relationship to the narrative of the case study>",
      "background": "<A 2-3 sentence background/bio of this person/entity based on the case study content>",
      "primary_goals": [
        "<Goal 1>",
        "<Goal 2>",
        "<Goal 3>"
      ],
      "personality_traits": {{
        "analytical": <0-10 rating>,
        "creative": <0-10 rating>,
        "assertive": <0-10 rating>,
        "collaborative": <0-10 rating>,
        "detail_oriented": <0-10 rating>
      }},
      "is_main_character": <true if this figure matches the student_role, otherwise false or omit>
    }}
  ],
  "learning_outcomes": [
    "1. <Outcome 1>",
    "2. <Outcome 2>",
    "3. <Outcome 3>",
    "4. <Outcome 4>",
    "5. <Outcome 5>"
  ],
  "scene_cards": [
    {{
      "scene_title": "<Short, clear title for this scene (e.g., 'Executive Team Faces Budget Cuts')>",
      "goal": "<What the characters or learners are trying to accomplish in this scene. Reference or support one or more of the main learning outcomes in the way this goal is written, but do not list them explicitly.>",
      "core_challenge": "<The main business dilemma, conflict, or tradeoff happening in this scene. Reference or support the learning outcomes in the narrative, but do not list them explicitly.>",
      "scene_description": "<A highly detailed, immersive, and at least 200-word, multi-paragraph narrative summary of what happens in this scene. Write in the second person, always centering the experience around the main character (the student role) as the decision-maker. Explicitly mention and involve all personas_involved by name, describing their actions, dialogue, and interactions with the main character. Make the narrative realistic, in-depth, and grounded in the case study context.>",
      "success_metric": "<A clear, measurable way to determine if the student (main character) has accomplished the specific goal of the scene, written in a way that is directly tied to the actions and decisions required in the narrative. Focus on what the student must do or achieve in the context of this scene, not just a generic outcome.>",
      "personas_involved": [
        "<Persona Name 1>",
        "<Persona Name 2>"
      ]
    }}
  ]
}}

Scene Card generation instructions:
- Break the case into 4–6 important scenes.
- Each scene_card MUST be unique: do not repeat or duplicate scene_title, goal, core_challenge, scene_description, success_metric, or personas_involved across different scenes. Each scene must cover a different part of the narrative or a different business challenge/decision.
- If the case study content is limited, synthesize plausible but non-repetitive scenes based on the available information, but do not copy or repeat any field between scenes.
- Each scene should align to one of the following simplified stages of business case analysis:
  * Context & Setup
  * Analysis & Challenges
  * Decisions & Tradeoffs
  * Actions & Outcomes
- For each scene_card, ensure the goal, core_challenge, scene_description, and success_metric are written in a way that references or supports the main learning outcomes, but do not embed or list the learning outcomes directly in the scene_card fields.
- The scene_title must NOT include stage names, numbers, or generic labels (such as “Context & Setup”, “Analysis & Challenges”, “Decisions & Tradeoffs”, “Actions & Outcomes”, or similar). The title should be a concise, descriptive summary of the scene’s unique content only.
- For each scene_card, include a personas_involved field listing the names of personas (from the key_figures array) who are actively participating in or relevant to the scene. The scene_description and goal should narratively reference these personas.
- Do not invent facts; only use what is in the case study content.
- Each scene_card object must include exactly those 6 fields listed above. 
- The success_metric field is required for every scene and must be a clear, measurable metric but make sure to avoid anything numeric related (not vague like “learn something”).

Important generation rules:
- Output ONLY a valid JSON object. Do not include any extra commentary, markdown, or formatting.
- All fields are required.
- The "scene_cards" field must be an array of 4–6 complete, well-structured scene card objects.

CASE STUDY CONTENT (context files first, then main PDF):
{combined_content}
"""
        
        print("[DEBUG] Combined content length:", len(combined_content))
        print("[DEBUG] Prompt sent to OpenAI")
        
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # Try with high token limit first, fallback to lower if needed
        max_tokens_attempts = [16384, 12288, 8192]
        response = None
        for attempt, max_tokens in enumerate(max_tokens_attempts):
            try:
                print(f"[DEBUG] Attempting OpenAI call with max_tokens={max_tokens} (attempt {attempt + 1})")
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "You are a JSON generator for business case study analysis. Extract comprehensive information about key figures and their relationships."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=max_tokens,
                        temperature=0.2,
                    )
                )
                break  # Success, exit the retry loop
            except Exception as api_error:
                print(f"[DEBUG] OpenAI call failed with max_tokens={max_tokens}: {str(api_error)}")
                if attempt == len(max_tokens_attempts) - 1:  # Last attempt
                    raise api_error  # Re-raise the last error
                # Try next lower token limit
                continue
        if response is None:
            raise Exception("OpenAI call failed for all token limits.")
        generated_text = response.choices[0].message.content
        print(f"[DEBUG] Raw OpenAI response length: {len(generated_text)} characters")
        print(f"[DEBUG] First 500 characters of response: {generated_text[:500]}...")
        print(f"[DEBUG] Last 500 characters of response: ...{generated_text[-500:]}")
        # Check if response was likely truncated
        finish_reason = response.choices[0].finish_reason
        print(f"[DEBUG] OpenAI finish_reason: {finish_reason}")
        if finish_reason == "length":
            print("[WARNING] OpenAI response was truncated due to max_tokens limit!")
            print("[WARNING] Consider using a more concise prompt or higher token limit")
        # Check if response contains key fields
        if '"key_figures"' in generated_text:
            print("[DEBUG] ✓ Response contains 'key_figures' field")
        else:
            print("[WARNING] ✗ Response does NOT contain 'key_figures' field")
        
        # Try to extract JSON from the response using regex
        match = re.search(r'({[\s\S]*})', generated_text)
        if match:
            json_str = match.group(1)
            
            # Try to fix incomplete JSON by adding missing closing brackets
            if not json_str.rstrip().endswith('}'):
                print("[DEBUG] JSON appears incomplete, attempting to fix...")
                # Count open braces and brackets to determine what's missing
                open_braces = json_str.count('{') - json_str.count('}')
                open_brackets = json_str.count('[') - json_str.count(']')
                
                # Add missing closing brackets and braces
                json_str += ']' * open_brackets + '}' * open_braces
                print(f"[DEBUG] Added {open_brackets} closing brackets and {open_braces} closing braces")
            
            try:
                ai_result = json.loads(json_str)
                print("[DEBUG] First AI call successful, now generating scenes...")
                print(f"[DEBUG] First AI result keys: {list(ai_result.keys())}")
                print(f"[DEBUG] Number of key figures: {len(ai_result.get('key_figures', []))}")
                
                # Second AI call to generate scenes
                try:
                    scenes = await generate_scenes_with_ai(ai_result)
                    print(f"[DEBUG] Second AI call returned {len(scenes) if isinstance(scenes, list) else 0} scenes")
                except Exception as scenes_error:
                    print(f"[ERROR] Second AI call failed: {scenes_error}")
                    scenes = []
                processed_scenes = []
                
                # If no scenes were generated by AI, create fallback scenes
                if not scenes:
                    print("[WARNING] No scenes generated by second AI call, using fallback...")
                    key_figures = ai_result.get("key_figures", [])
                    student_role = ai_result.get("student_role", "Manager")
                    
                    # Extract key personas for scenes
                    senior_figures = [fig["name"] for fig in key_figures if any(word in fig.get("role", "").lower() for word in ["vp", "vice", "president", "senior", "global"])]
                    team_figures = [fig["name"] for fig in key_figures if any(word in fig.get("role", "").lower() for word in ["manager", "engineer", "support", "advocate"])]
                    all_names = [fig["name"] for fig in key_figures]
                    
                    # Create case-specific scenes based on context
                    fallback_scenes = [
                        {
                            "title": "Crisis Assessment Meeting",
                            "description": "You are in the main conference room with senior leadership, reviewing the urgent situation that requires immediate attention. The atmosphere is tense with incident reports and client communications displayed on screens around the room.",
                            "personas_involved": senior_figures[:3] if len(senior_figures) >= 3 else all_names[:3],
                            "user_goal": f"As the {student_role}, assess the scope of the crisis and understand the immediate risks to the organization.",
                            "sequence_order": 1
                        },
                        {
                            "title": "Team Investigation",
                            "description": "You are conducting interviews with team members across different locations to understand what went wrong. The setting varies from video calls to in-person meetings as you piece together the timeline of events.",
                            "personas_involved": team_figures[:4] if len(team_figures) >= 4 else all_names[1:5],
                            "user_goal": "Identify the root causes of the issues and gather perspectives from team members.",
                            "sequence_order": 2
                        },
                        {
                            "title": "Solution Development Workshop",
                            "description": "You are leading a collaborative session with team members present and others joining virtually. Whiteboards are filled with process diagrams and improvement plans as you work to develop solutions.",
                            "personas_involved": (team_figures + senior_figures)[:4] if len(key_figures) >= 4 else all_names[:4],
                            "user_goal": "Develop concrete solutions and create an implementation plan.",
                            "sequence_order": 3
                        },
                        {
                            "title": "Implementation Approval Meeting",
                            "description": "You are presenting your comprehensive action plan to leadership in the boardroom. Charts showing your recommendations and success metrics are displayed as you seek approval.",
                            "personas_involved": senior_figures[:3] if len(senior_figures) >= 3 else all_names[-3:],
                            "user_goal": "Secure approval for your plan and establish clear success metrics and timelines.",
                            "sequence_order": 4
                        }
                    ]
                    scenes = fallback_scenes[:4]
                
                if scenes:
                    print(f"[DEBUG] Processing {len(scenes)} scenes for image generation...")
                    
                    # Generate images for each scene in parallel
                    image_tasks = []
                    for scene in scenes:
                        if isinstance(scene, dict) and "description" in scene and "title" in scene:
                            task = generate_scene_image(scene["description"], scene["title"])
                            image_tasks.append(task)
                        else:
                            # Create a simple async function that returns empty string
                            async def empty_task():
                                return ""
                            image_tasks.append(empty_task())
                    
                    # Wait for all image generations to complete
                    image_urls = await asyncio.gather(*image_tasks, return_exceptions=True)
                    
                    # Combine scenes with their generated images
                    for i, scene in enumerate(scenes):
                        if isinstance(scene, dict):
                            processed_scene = {
                                "title": scene.get("title", f"Scene {i+1}"),
                                "description": scene.get("description", ""),
                                "personas_involved": scene.get("personas_involved", []),
                                "user_goal": scene.get("user_goal", ""),
                                "sequence_order": scene.get("sequence_order", i+1),
                                "image_url": image_urls[i] if i < len(image_urls) and not isinstance(image_urls[i], Exception) else "",
                                "successMetric": scene.get("success_metric", "")
                            }
                            processed_scenes.append(processed_scene)
                            print(f"[DEBUG] Scene {i+1}: {processed_scene['title']} - Image: {'Generated' if processed_scene['image_url'] else 'Failed'}")
                
                final_result = {
                    "title": ai_result.get("title") or title,
                    "description": ai_result.get("description") or (cleaned_content[:1500] + "..." if len(cleaned_content) > 1500 else cleaned_content),
                    "student_role": ai_result.get("student_role") or "",
                    "key_figures": ai_result.get("key_figures") if "key_figures" in ai_result else [],
                    "scenes": processed_scenes,
                    "learning_outcomes": ai_result.get("learning_outcomes") or [
                        "1. Analyze the business situation presented in the case study",
                        "2. Identify key stakeholders and their interests",
                        "3. Develop strategic recommendations based on the analysis",
                        "4. Evaluate the impact of decisions on organizational performance",
                        "5. Apply business concepts and frameworks to real-world scenarios"
                    ]
                }
                print(f"[DEBUG] Successfully parsed JSON! Final AI result sent to frontend with {len(final_result.get('key_figures', []))} key figures and {len(processed_scenes)} scenes")
                print("[DEBUG] Key figures names:", [fig.get('name', 'Unknown') for fig in final_result.get('key_figures', [])])
                print("[DEBUG] Scene titles:", [scene.get('title', 'Unknown') for scene in processed_scenes])
                print(f"[DEBUG] Final result keys: {list(final_result.keys())}")
                print(f"[DEBUG] Scenes in final result: {len(final_result.get('scenes', []))}")
                print("[DEBUG] Raw AI scenes:", ai_result.get("scene_cards", []))
                
                # Post-processing validation to ensure student role is not in key_figures
                student_role = final_result.get("student_role", "").lower()
                key_figures = final_result.get("key_figures", [])

                # After parsing key_figures, filter out any with is_main_character true
                filtered_key_figures = []
                for fig in key_figures:
                    if fig.get("is_main_character", False):
                        print(f"[DEBUG] Removing main character from key_figures: {fig.get('name', '')}")
                        continue
                    filtered_key_figures.append(fig)
                final_result["key_figures"] = filtered_key_figures

                # Ensure every scene has personas_involved and successMetric (fallback to scene_cards if needed)
                if "scenes" in final_result and "scene_cards" in ai_result:
                    scene_cards = ai_result["scene_cards"]
                    key_figure_names = [fig["name"] for fig in final_result["key_figures"]]
                    student_role = final_result.get("student_role", "").strip().lower()
                    for i, scene in enumerate(final_result["scenes"]):
                        # Fallback for personas_involved
                        if (not scene.get("personas_involved") or len(scene.get("personas_involved", [])) == 0) and i < len(scene_cards):
                            pi = scene_cards[i].get("personas_involved", [])
                            if pi:
                                scene["personas_involved"] = pi
                        # --- ENFORCE: At least one non-student persona in personas_involved ---
                        personas = scene.get("personas_involved", [])
                        # Remove main character if present
                        personas = [p for p in personas if p.strip().lower() != student_role]
                        # Parse description for persona names
                        desc = scene.get("description", "")
                        mentioned = [name for name in key_figure_names if name in desc and name.strip().lower() != student_role]
                        for name in mentioned:
                            if name not in personas:
                                personas.append(name)
                        # If still empty, add the first non-student persona
                        if not personas and key_figure_names:
                            first_non_student = next((n for n in key_figure_names if n.strip().lower() != student_role), None)
                            if first_non_student:
                                personas.append(first_non_student)
                                # Optionally, append a sentence to the description
                                scene["description"] = desc + f"\n\n{first_non_student} is present in this scene."
                        scene["personas_involved"] = personas
                        # Fallback for successMetric
                        if not scene.get("successMetric") and i < len(scene_cards):
                            metric = scene_cards[i].get("success_metric")
                            if metric:
                                scene["successMetric"] = metric
                print("[DEBUG] Final processed scenes:", final_result.get("scenes", []))
                
                # Robustly remove main character from personas_involved in all scenes (final step)
                def normalize_name(name):
                    return ''.join(c for c in name.lower().strip() if c.isalnum())

                def is_likely_same_person(student_role, persona_name):
                    n_role = normalize_name(student_role)
                    n_name = normalize_name(persona_name)
                    if not n_role or not n_name:
                        return False
                    if n_role == n_name:
                        return True
                    # Split into words and check for overlap
                    role_words = n_role.split()
                    name_words = n_name.split()
                    overlap = [w for w in role_words if w in name_words]
                    return len(overlap) >= 1  # At least one word matches

                student_role = final_result.get("student_role", "")
                student_role_norm = normalize_name(student_role)
                key_figures = final_result.get("key_figures", [])

                # Mark main character in key_figures
                for fig in key_figures:
                    fig_name = fig.get("name", "")
                    fig_role = fig.get("role", "")
                    fig["is_main_character"] = (
                        is_likely_same_person(student_role, fig_name) or
                        is_likely_same_person(student_role, fig_role)
                    )

                main_character_names = {fig["name"] for fig in final_result["key_figures"] if fig.get("is_main_character", False)}

                # Fallback: if main_character_names is empty, try to detect it
                if not main_character_names:
                    student_role = final_result.get("student_role", "")
                    student_role_norm = normalize_name(student_role)
                    for fig in final_result["key_figures"]:
                        if student_role_norm in normalize_name(fig.get("name", "")) or student_role_norm in normalize_name(fig.get("role", "")):
                            main_character_names.add(fig.get("name", ""))
                            print(f"[DEBUG] Fallback: Detected main character as {fig.get('name', '')}")

                for scene in final_result.get("scenes", []):
                    before = list(scene.get("personas_involved", []))
                    scene["personas_involved"] = [
                        p for p in scene.get("personas_involved", [])
                        if normalize_name(p) not in {normalize_name(n) for n in main_character_names}
                    ]
                    print(f"[DEBUG] Filtering personas_involved: {before} | main_character_names: {main_character_names} | after: {scene['personas_involved']}")
                
                return final_result
            except json.JSONDecodeError as e:
                print(f"[ERROR] Failed to parse JSON from AI response even after fixing: {e}")
                print(f"[ERROR] Fixed JSON attempt: {json_str[:500]}...")
        else:
            print("[ERROR] No JSON object found in OpenAI response.")
            
            # Fallback: return structured content
            return {
                        "title": title,
                        "description": cleaned_content[:1500] + "..." if len(cleaned_content) > 1500 else cleaned_content,
                "key_figures": [],
            "scenes": [],
                        "learning_outcomes": [
                            "1. Analyze the business situation presented in the case study",
                            "2. Identify key stakeholders and their interests",
                            "3. Develop strategic recommendations based on the analysis",
                            "4. Evaluate the impact of decisions on organizational performance",
                            "5. Apply business concepts and frameworks to real-world scenarios"
                        ]
                    }
    
    except Exception as e:
        print(f"[ERROR] AI processing failed: {str(e)}")
        # Return fallback content
        return {
            "title": "Business Case Study",
            "description": "Failed to process case study content",
            "key_figures": [],
            "scenes": [],
            "learning_outcomes": [
                "1. Analyze the business situation presented in the case study",
                "2. Identify key stakeholders and their interests"
            ]
        }

async def save_scenario_to_db(
    ai_result: dict,
    main_file: UploadFile,
    context_files: List[UploadFile],
    main_content: str,
    context_content: str,
    user_id: int,
    db: Session
) -> int:
    """
    Save AI processing results to database
    Creates scenario with personas, scenes, and files
    """
    
    try:
        # Extract title from AI result or filename
        title = ai_result.get("title", main_file.filename.replace(".pdf", ""))
        
        # Create scenario record
        scenario = Scenario(
            title=title,
            description=ai_result.get("description", ""),
            challenge=ai_result.get("description", ""),  # Use description as challenge for now
            industry="Business",  # Default industry
            learning_objectives=ai_result.get("learning_outcomes", []),
            student_role=ai_result.get("student_role", "Business Analyst"),
            source_type="pdf_upload",
            pdf_content=main_content,
            pdf_title=title,
            pdf_source="Uploaded PDF",
            processing_version="1.0",
            is_public=False,  # Start as private draft
            allow_remixes=True,
            created_by=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(scenario)
        db.flush()  # Get scenario ID
        
        print(f"[DEBUG] Created scenario with ID: {scenario.id}")
        
        # Save personas
        persona_mapping = {}  # name -> persona_id for scene relationships
        key_figures = ai_result.get("key_figures", [])
        
        for figure in key_figures:
            if isinstance(figure, dict) and figure.get("name"):
                persona = ScenarioPersona(
                    scenario_id=scenario.id,
                    name=figure.get("name", ""),
                    role=figure.get("role", ""),
                    background=figure.get("background", ""),
                    correlation=figure.get("correlation", ""),
                    primary_goals=figure.get("primary_goals", []),
                    personality_traits=figure.get("personality_traits", {}),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(persona)
                db.flush()
                persona_mapping[figure["name"]] = persona.id
                print(f"[DEBUG] Created persona: {figure['name']} with ID: {persona.id}")
        
        # Save scenes
        scenes = ai_result.get("scenes", [])
        for i, scene in enumerate(scenes):
            if isinstance(scene, dict) and scene.get("title"):
                scene_record = ScenarioScene(
                    scenario_id=scenario.id,
                    title=scene.get("title", ""),
                    description=scene.get("description", ""),
                    user_goal=scene.get("user_goal", ""),
                    scene_order=i + 1,
                    estimated_duration=scene.get("estimated_duration", 30),
                    image_url=scene.get("image_url", ""),
                    image_prompt=f"Business scene: {scene.get('title', '')}",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(scene_record)
                db.flush()
                print(f"[DEBUG] Created scene: {scene['title']} with ID: {scene_record.id}")
                # Link personas to scene (if personas_involved exists)
                personas_involved = scene.get("personas_involved", [])
                unique_persona_names = set(personas_involved)
                for persona_name in unique_persona_names:
                    if persona_name in persona_mapping:
                        pid = persona_mapping[persona_name]
                        db.execute(
                            scene_personas.insert().values(
                                scene_id=scene_record.id,
                                persona_id=pid,
                                involvement_level="participant"
                            )
                        )
        
        # Save file metadata
        scenario_file = ScenarioFile(
            scenario_id=scenario.id,
            filename=main_file.filename,
            file_type="pdf",
            original_content=main_content[:10000],  # Truncate for storage
            processed_content=main_content,
            processing_status="completed",
            processing_log={
                "personas_count": len(key_figures),
                "scenes_count": len(scenes),
                "processing_timestamp": datetime.utcnow().isoformat()
            },
            uploaded_at=datetime.utcnow(),
            processed_at=datetime.utcnow()
        )
        db.add(scenario_file)
        
        # Save context files if any
        for ctx_file in context_files:
            context_file_record = ScenarioFile(
                scenario_id=scenario.id,
                filename=f"context_{ctx_file.filename}",
                file_type=ctx_file.filename.split(".")[-1] if "." in ctx_file.filename else "txt",
                original_content=context_content[:5000],  # Truncate for storage
                processed_content=context_content,
                processing_status="completed",
                uploaded_at=datetime.utcnow(),
                processed_at=datetime.utcnow()
            )
            db.add(context_file_record)
        
        # Commit all changes
        db.commit()
        print(f"[DEBUG] Successfully saved scenario {scenario.id} to database")
        
        return scenario.id
        
    except Exception as e:
        print(f"[ERROR] Failed to save scenario to database: {e}")
        db.rollback()
        raise e 