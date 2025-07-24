"use client"


import React, { useState, useRef, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { Progress } from "@/components/ui/progress"
import { Upload, Info, Users, Activity, Sparkles, X, Check } from "lucide-react"
import Link from "next/link"
import PersonaCard from "@/components/PersonaCard";
import SceneCard from "@/components/SceneCard";
import { buildApiUrl } from "@/lib/api";


// Simple Modal component
function Modal({ isOpen, onClose, children }: { isOpen: boolean; onClose: () => void; children: React.ReactNode }) {
 React.useEffect(() => {
   if (isOpen) {
     document.body.classList.add('overflow-hidden');
   } else {
     document.body.classList.remove('overflow-hidden');
   }
   return () => {
     document.body.classList.remove('overflow-hidden');
   };
 }, [isOpen]);
 if (!isOpen) return null;
 return (
   <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900 bg-opacity-60">
     <div className="bg-white rounded-lg shadow-lg w-[760px] h-[80vh] flex flex-col relative p-0 resize-none">
       <button
         className="absolute top-4 right-4 text-gray-400 text-2xl font-bold hover:text-gray-600 z-10"
         onClick={onClose}
         aria-label="Close edit window"
       >
         &times;
       </button>
       {children}
     </div>
   </div>
 );
}

function PersonaModal({ isOpen, onClose, children }: { isOpen: boolean; onClose: () => void; children: React.ReactNode }) {
 React.useEffect(() => {
   if (isOpen) {
     document.body.classList.add('overflow-hidden');
   } else {
     document.body.classList.remove('overflow-hidden');
   }
   return () => {
     document.body.classList.remove('overflow-hidden');
   };
 }, [isOpen]);
 if (!isOpen) return null;
 return (
   <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900 bg-opacity-60">
     <div className="bg-white rounded-lg shadow-lg w-[760px] h-[80vh] flex flex-col relative p-0 resize-none">
       <button
         className="absolute top-4 right-4 text-gray-400 text-2xl font-bold hover:text-gray-600 z-10"
         onClick={onClose}
         aria-label="Close edit window"
       >
         &times;
       </button>
       {children}
     </div>
   </div>
 );
}

function SceneModal({ isOpen, onClose, children }: { isOpen: boolean; onClose: () => void; children: React.ReactNode }) {
 React.useEffect(() => {
   if (isOpen) {
     document.body.classList.add('overflow-hidden');
   } else {
     document.body.classList.remove('overflow-hidden');
   }
   return () => {
     document.body.classList.remove('overflow-hidden');
   };
 }, [isOpen]);
 if (!isOpen) return null;
 return (
   <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900 bg-opacity-60">
     <div className="bg-white rounded-lg shadow-lg w-[1000px] h-[80vh] flex flex-col relative p-0 resize-none">
       <button
         className="absolute top-4 right-4 text-gray-400 text-2xl font-bold hover:text-gray-600 z-10"
         onClick={onClose}
         aria-label="Close edit window"
       >
         &times;
       </button>
       {children}
     </div>
   </div>
 );
}


export default function ScenarioBuilder() {
 const [uploadedFile, setUploadedFile] = useState<File | null>(null)
 const fileInputRef = useRef<HTMLInputElement>(null)
 const [name, setName] = useState("")
 const [description, setDescription] = useState("")
 const [learningOutcomes, setLearningOutcomes] = useState("")
 const [autofillLoading, setAutofillLoading] = useState(false)
 const [autofillError, setAutofillError] = useState<string | null>(null)
 const [autofillResult, setAutofillResult] = useState<any>(null)
 const [autofillStep, setAutofillStep] = useState<string>("")
 const [autofillProgress, setAutofillProgress] = useState(0)
 const [autofillMaxAttempts, setAutofillMaxAttempts] = useState(60)
 const [isDragOver, setIsDragOver] = useState(false)
 const [uploadedFiles, setUploadedFiles] = useState<File[]>([]); // For the "Upload Files" button
 const filesInputRef = useRef<HTMLInputElement>(null);
 const [personas, setPersonas] = useState<any[]>([]);
 const [editingIdx, setEditingIdx] = useState<number | null>(null);
 const [tempPersonas, setTempPersonas] = useState<any[]>([]); // Track temporary personas that haven't been saved yet

 // Timeline/Tasks state
 const [tasks, setTasks] = useState<any[]>([]);
 const [editingTaskIdx, setEditingTaskIdx] = useState<number | null>(null);
 const [scenes, setScenes] = useState<any[]>([]);
 const [editingSceneIdx, setEditingSceneIdx] = useState<number | null>(null);

 // Save status state
 const [isSaved, setIsSaved] = useState(false);
 const [isPublished, setIsPublished] = useState(false);
 const [isSaving, setIsSaving] = useState(false);
 const [isPublishing, setIsPublishing] = useState(false);
 const [savedScenarioId, setSavedScenarioId] = useState<number | null>(null);

 // Save and Publish handlers
 const handleSave = async (): Promise<number | null> => {
   if (!autofillResult) {
     alert("No scenario data to save. Please upload and process a PDF first.");
     return null;
   }

   // Build payload using only the latest user-edited state
   const payload = {
     // Only copy non-scene/persona fields from autofillResult
     title: name || autofillResult.title,
     description: description || autofillResult.description,
     learning_outcomes: learningOutcomes || autofillResult.learning_outcomes,
     student_role: autofillResult.student_role,
     key_figures: autofillResult.key_figures,
     // Use the latest scenes and personas state
     scenes: normalizeScenes(scenes),
     personas,
   };

   // Debug log to check scenes state before saving
   console.log("Scenes state before save:", scenes);
   console.log("Personas state before save:", personas);

   setIsSaving(true);
   try {
     console.log("[DEBUG] Sending to save endpoint:", {
       keys: Object.keys(payload),
       title: payload.title,
       key_figures_count: payload.key_figures?.length || 0,
       scenes_count: payload.scenes?.length || 0
     });
     
     const response = await fetch(buildApiUrl("/api/scenarios/save"), {
       method: "POST",
       headers: {
         "Content-Type": "application/json",
       },
       body: JSON.stringify(payload),
     });

     if (response.ok) {
       const result = await response.json();
       setIsSaved(true);
       setSavedScenarioId(result.scenario_id); // Store the scenario ID
       console.log("Scenario saved:", result);
       
       // Reset save status after 3 seconds to show it's temporary
       setTimeout(() => {
         setIsSaved(false);
       }, 3000);
       
       return result.scenario_id;
     } else {
       console.error("Failed to save scenario");
       alert("Failed to save scenario. Please try again.");
       return null;
     }
   } catch (error) {
     console.error("Error saving scenario:", error);
     alert("Error saving scenario. Please try again.");
     return null;
   } finally {
     setIsSaving(false);
   }
 };

 const handlePublish = async () => {
   if (!autofillResult) {
     alert("No scenario data to publish. Please save the scenario first.");
     return;
   }

   setIsPublishing(true);
   try {
     // First save if not already saved
     let scenarioId = savedScenarioId;
     if (!isSaved || !scenarioId) {
       scenarioId = await handleSave();
     }
     
     if (!scenarioId) {
       alert("Failed to save scenario. Cannot publish.");
       return;
     }
     
     // Actually publish the scenario
     const publishData = {
       category: autofillResult.industry || "Business",
       difficulty_level: "Intermediate",
       tags: ["case-study", "management", "teamwork"],
       estimated_duration: 60
     };
     
           const response = await fetch(buildApiUrl(`/api/scenarios/publish/${scenarioId}`), {
       method: "POST",
       headers: {
         "Content-Type": "application/json",
       },
       body: JSON.stringify(publishData),
     });

     if (response.ok) {
       const result = await response.json();
       setIsPublished(true);
       console.log("Scenario published:", result);
       
       // Reset publish status after 3 seconds
       setTimeout(() => {
         setIsPublished(false);
       }, 3000);
     } else {
       console.error("Failed to publish scenario");
       alert("Failed to publish scenario. Please try again.");
     }
   } catch (error) {
     console.error("Error publishing scenario:", error);
     alert("Error publishing scenario. Please try again.");
   } finally {
     setIsPublishing(false);
   }
 };

 // Reset save status when content changes
 const markAsUnsaved = () => {
   setIsSaved(false);
   setIsPublished(false);
 };

 // Handle Play Scenario - save first if needed, then navigate to chatbox
 const handlePlayScenario = async () => {
   if (!autofillResult) {
     alert("No scenario data to play. Please upload and process a PDF first.");
     return;
   }

   let scenarioId = savedScenarioId;
   
   // Only allow play if scenario is already saved
   if (!scenarioId) {
     alert("Please save the scenario before playing.");
     return;
   }

   // Store scenario ID for chatbox
   const chatboxData = {
     scenario_id: scenarioId,
     title: autofillResult.title || "Untitled Scenario"
   };
   
   localStorage.setItem("chatboxScenario", JSON.stringify(chatboxData));
   
   // Navigate to chatbox
   window.open("/chat-box", "_blank");
 };

 // Transform our scenario data to chatbox format
 const transformTochatboxFormat = (scenarioData: any) => {
   const characters = scenarioData.key_figures?.map((figure: any) => ({
     name: figure.name,
     role: figure.role,
     personality_profile: {
       strengths: [],
       motivations: figure.primary_goals || [],
       leadership_style: figure.background || "",
       key_quote: `As ${figure.role}, I focus on achieving our objectives.`,
       decision_making_approach: "Strategic and analytical",
       risk_tolerance: "Medium",
       communication_style: "Professional and direct",
       background: figure.background || "",
       correlation: figure.correlation || ""
     }
   })) || [];

   const phases = scenarioData.scenes?.map((scene: any, index: number) => ({
     phase: index + 1,
     title: scene.title,
     duration: `${scene.estimated_duration || 30} minutes`,
     goal: scene.user_goal || "Complete the phase objectives",
     activities: [scene.description || "Analyze the situation and make decisions"],
     deliverables: [
       "Analysis summary",
       "Strategic recommendations",
       "Decision rationale"
     ]
   })) || [
     {
       phase: 1,
       title: "Initial Analysis",
       duration: "30 minutes",
       goal: "Analyze the business situation and identify key challenges",
       activities: ["Review case study materials", "Identify stakeholders", "Assess current situation"],
       deliverables: ["Situation analysis", "Stakeholder map", "Problem identification"]
     }
   ];

   return {
     case_study: {
       title: scenarioData.title,
       description: scenarioData.description,
       industry: "Business",
       primary_challenge: "Strategic decision making",
       learning_outcomes: (scenarioData.learning_outcomes || []).map((outcome: string) => ({
         outcome: outcome.replace(/^\d+\.\s*/, ''), // Remove numbering
         description: `Students will ${outcome.toLowerCase()}`
       })),
       characters: characters,
       simulation_timeline: {
         total_duration: `${phases.length * 30} minutes`,
         phases: phases
       },
       teaching_notes: {
         preparation_required: "Students should review the case study materials thoroughly",
         key_concepts: [
           "Strategic analysis",
           "Decision making", 
           "Business problem solving"
         ]
       }
     }
   };
 };

 // Placeholder handlers for personas and timeline
 const handleAddPersona = () => {
   const newPersona = {
     id: `temp-persona-${Date.now()}`,
     name: "New Persona",
     position: "",
     description: "",
     traits: {
       assertiveness: 3,
       cooperativeness: 3,
       openness: 3,
       risk_tolerance: 3,
       emotional_stability: 3
     },
     defaultTraits: {
       assertiveness: 3,
       cooperativeness: 3,
       openness: 3,
       risk_tolerance: 3,
       emotional_stability: 3
     },
     primaryGoals: "",
     isTemp: true // Mark as temporary
   };
   
   // Add to temporary personas at the top
   setTempPersonas(tempPersonas => [newPersona, ...tempPersonas]);
   setEditingIdx(0); // Open the new persona for editing (it's at index 0 now)
 }
 const handleAddScene = () => {
   const newScene = {
     id: `scene-${Date.now()}`,
     title: "New Scene",
     description: "",
     personas_involved: [],
     user_goal: "",
     sequence_order: scenes.length + 1,
     image_url: "",
     timeout_turns: 15
   };
   setScenes(scenes => [...scenes, newScene]);
   setEditingSceneIdx(scenes.length); // Open the new scene for editing
 }


 // Handler to clear the uploaded file and open the file picker
 const handleChooseDifferentFile = (e: React.MouseEvent) => {
   e.preventDefault();
   setUploadedFile(null);
   if (fileInputRef.current) fileInputRef.current.value = "";
 }


 const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
   const file = e.target.files?.[0]
   if (file) setUploadedFile(file)
 }


 const handleDragOver = (e: React.DragEvent) => {
   e.preventDefault()
   setIsDragOver(true)
 }


 const handleDragLeave = (e: React.DragEvent) => {
   e.preventDefault()
   setIsDragOver(false)
 }


 const handleDrop = (e: React.DragEvent) => {
   e.preventDefault()
   setIsDragOver(false)
  
   const files = Array.from(e.dataTransfer.files)
   const pdfFile = files.find(file => file.type === "application/pdf")
  
   if (pdfFile) {
     setUploadedFile(pdfFile)
     // Clear the file input value to ensure it updates
     if (fileInputRef.current) {
       fileInputRef.current.value = ""
     }
   } else {
     alert("Please drop a PDF file")
   }
 }


 // Handler for "Upload Files" button
 const handleFilesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
   if (e.target.files) {
     const filesArray = Array.from(e.target.files);
     setUploadedFiles(filesArray);
     console.log("[DEBUG] Context files selected:", filesArray.map(f => f.name));
   }
 };
 const handleUploadFilesClick = () => {
   filesInputRef.current?.click();
 };


 // Handler to remove a file from uploadedFiles
 const handleRemoveFile = (idx: number) => {
   setUploadedFiles(files => files.filter((_, i) => i !== idx));
 };


 const handleAutofill = async () => {
   if (!uploadedFile) return;
   setAutofillLoading(true);
   setAutofillError(null);
   setAutofillResult(null);
   setAutofillStep("Processing PDF and context files...");
   setAutofillProgress(25);
  
   try {
     const formData = new FormData();
     formData.append("file", uploadedFile);
     
     // Attach context files if any were uploaded via the bottom button
     if (uploadedFiles.length > 0) {
       uploadedFiles.forEach((file) => {
         formData.append("context_files", file);
       });
     }
     console.log("[DEBUG] handleAutofill: PDF file to upload:", uploadedFile.name);
     console.log("[DEBUG] handleAutofill: Context files to upload:", uploadedFiles.map(f => f.name));
     
     setAutofillStep("Sending files to backend...");
     setAutofillProgress(50);
     
     const response = await fetch(buildApiUrl("/api/parse-pdf/"), {
       method: "POST",
       body: formData,
     });
    
     if (!response.ok) {
       throw new Error("Failed to process PDF");
     }
    
     setAutofillStep("Processing with AI...");
     setAutofillProgress(75);
     
     const resultData = await response.json();
     console.log("Backend response:", resultData);
     console.log("Response status:", resultData.status);
     console.log("AI result exists:", !!resultData.ai_result);
     console.log("Response keys:", Object.keys(resultData));
    
     if (resultData.status === "completed" && resultData.ai_result) {
       setAutofillStep("Complete!");
       setAutofillProgress(100);
       setAutofillResult(resultData);
      
       // Populate form fields with AI results
       const aiData = resultData.ai_result;
       console.log("AI Result:", aiData);
       console.log("AI Result keys:", Object.keys(aiData));
      
       // Set the title
       if (aiData.title) {
         console.log("Setting title:", aiData.title);
         setName(aiData.title);
       } else {
         console.log("No title found in AI result");
       }
      
       // Set the description
       if (aiData.description) {
         console.log("Setting description:", aiData.description);
         const formattedDescription = formatDescription(aiData.description);
         console.log("Formatted description:", formattedDescription);
         setDescription(formattedDescription);
       } else {
         console.log("No description found in AI result");
         console.log("Description field value:", aiData.description);
       }
      
       // Set the learning outcomes
       if (aiData.learning_outcomes && Array.isArray(aiData.learning_outcomes)) {
         console.log("Setting learning outcomes:", aiData.learning_outcomes);
         setLearningOutcomes(aiData.learning_outcomes.join('\n'));
       } else {
         console.log("No learning outcomes found in AI result");
       }
       
       // Create personas from key figures (excluding the student role)
       console.log("[DEBUG] Checking for key_figures in aiData:", aiData.key_figures);
       if (aiData.key_figures && Array.isArray(aiData.key_figures)) {
         console.log("=== KEY FIGURES DEBUG ===");
         console.log("Total key figures identified:", aiData.key_figures.length);
         console.log("All key figures:", aiData.key_figures);
         console.log("Student role:", aiData.student_role);
         
         console.log("=== FILTERING PROCESS ===");
         
         // Only exclude the actual main character (student role), not everyone mentioned in the description
         const studentRole = aiData.student_role?.toLowerCase() || '';
         
         console.log(`[DEBUG] Student role: "${studentRole}"`);
         
         const filteredFigures = aiData.key_figures.filter((figure: any) => {
           const figureName = figure.name?.toLowerCase() || '';
           const figureRole = figure.role?.toLowerCase() || '';
           
           console.log(`[DEBUG] Checking figure: "${figure.name}" (role: "${figure.role}")`);
           
           // Check 1: Skip if this figure matches the student role exactly
           if (studentRole && (figureName.includes(studentRole) || figureRole.includes(studentRole))) {
             console.log(`[DEBUG] ❌ EXCLUDING ${figure.name} - matches student role: "${studentRole}"`);
             return false;
           }
           
           // Check 2: Skip if this figure has a role that suggests they're the main protagonist
           // Only exclude if they're clearly the main character, not just mentioned in the description
           const protagonistRoles = ['protagonist', 'main character', 'lead', 'principal', 'central figure'];
           if (protagonistRoles.some(role => figureRole.includes(role))) {
             console.log(`[DEBUG] ❌ EXCLUDING ${figure.name} - has protagonist role: "${figureRole}"`);
             return false;
           }
           
           console.log(`[DEBUG] ✅ KEEPING ${figure.name}`);
           return true;
         });
         
         console.log(`[DEBUG] After filtering: ${filteredFigures.length} figures remain out of ${aiData.key_figures.length} total`);
         
         const newPersonas = filteredFigures
           .map((figure: any, index: number) => {
             console.log(`[DEBUG] Processing key figure ${index + 1}:`, figure);
             console.log(`[DEBUG] Personality traits for ${figure.name}:`, figure.personality_traits);
             console.log(`[DEBUG] Primary goals for ${figure.name}:`, figure.primary_goals);
             
             // Format goals properly
             let formattedGoals = 'Goals not specified in the case study.';
             if (Array.isArray(figure.primary_goals) && figure.primary_goals.length > 0) {
               formattedGoals = figure.primary_goals.map((goal: string) => `• ${goal}`).join('\n');
             } else if (typeof figure.primary_goals === 'string' && figure.primary_goals.trim()) {
               // If it's a string, try to split by common separators and bullet them
               const goals = figure.primary_goals.split(/[;\n]/).map((goal: string) => goal.trim()).filter((goal: string) => goal.length > 0);
               if (goals.length > 1) {
                 formattedGoals = goals.map((goal: string) => `• ${goal}`).join('\n');
               } else {
                 formattedGoals = `• ${figure.primary_goals}`;
               }
             }
             
             console.log(`[DEBUG] Formatted goals for ${figure.name}:`, formattedGoals);
             
             return {
               id: `persona-${Date.now()}-${index}`,
               name: figure.name || `Person ${index + 1}`,
               position: figure.role || 'Unknown',
               description: formatDescription(figure.background || figure.correlation || 'No background information available.'),
               primaryGoals: formattedGoals,
               traits: {
                 assertiveness: Math.max(1, Math.min(5, Math.round((figure.personality_traits?.assertive || 5) / 2))),
                 cooperativeness: Math.max(1, Math.min(5, Math.round((figure.personality_traits?.collaborative || 5) / 2))),
                 openness: Math.max(1, Math.min(5, Math.round((figure.personality_traits?.creative || 5) / 2))),
                 risk_tolerance: Math.max(1, Math.min(5, Math.round((figure.personality_traits?.analytical || 5) / 2))),
                 emotional_stability: Math.max(1, Math.min(5, Math.round((figure.personality_traits?.detail_oriented || 5) / 2)))
               }
             };
           });
         
         console.log("=== FINAL PERSONAS ===");
         console.log(`Total personas created: ${newPersonas.length}`);
         newPersonas.forEach((persona: any, index: number) => {
           console.log(`Persona ${index + 1}: ${persona.name} (${persona.position})`);
           console.log(`  Goals: ${persona.primaryGoals}`);
           console.log(`  Personality:`, persona.traits);
         });
         setPersonas(newPersonas);
       } else {
         console.log("[DEBUG] No key_figures found in aiData, creating empty personas array");
         setPersonas([]);
       }
       
       // Process scenes from AI results
       console.log("[DEBUG] Checking for scenes in aiData:", aiData.scenes);
       if (aiData.scenes && Array.isArray(aiData.scenes)) {
         console.log("=== SCENES DEBUG ===");
         console.log("Total scenes identified:", aiData.scenes.length);
         console.log("All scenes:", aiData.scenes);
         
         const processedScenes = aiData.scenes
           .sort((a: any, b: any) => (a.sequence_order || 0) - (b.sequence_order || 0)) // Sort by sequence order
           .map((scene: any, index: number) => {
             console.log(`[DEBUG] Processing scene ${index + 1}:`, scene);
             return {
               id: `scene-${Date.now()}-${index}`,
               title: scene.title || `Scene ${index + 1}`,
               description: scene.description || '',
               personas_involved: scene.personas_involved || [],
               user_goal: scene.user_goal || '',
               sequence_order: scene.sequence_order || index + 1,
               image_url: scene.image_url || '',
               successMetric: scene.successMetric || '',
               timeout_turns: scene.timeout_turns !== undefined && scene.timeout_turns !== null ? scene.timeout_turns : 15
             };
           });
         
         console.log("=== FINAL SCENES ===");
         console.log(`Total scenes created: ${processedScenes.length}`);
         processedScenes.forEach((scene: any, index: number) => {
           console.log(`Scene ${index + 1}: ${scene.title}`);
           console.log(`  Goal: ${scene.user_goal}`);
           console.log(`  Personas: ${scene.personas_involved.join(', ')}`);
           console.log(`  Image: ${scene.image_url ? 'Generated' : 'None'}`);
         });
         setScenes(processedScenes);
         console.log("Processed scenes:", processedScenes.map((s: any) => ({ title: s.title, personas_involved: s.personas_involved })));
       } else {
         console.log("[DEBUG] No scenes found in aiData, creating empty scenes array");
         setScenes([]);
       }
      
     } else {
       console.log("No AI result found in response:", resultData);
       console.log("Full result data:", resultData);
       throw new Error("No AI result received from backend");
     }
    
   } catch (err: any) {
     console.error("Autofill error details:", err);
     console.error("Error stack:", err.stack);
     setAutofillError(err.message || "Unknown error occurred during autofill");
   } finally {
     setAutofillLoading(false);
     setAutofillStep("");
     setAutofillProgress(0);
   }
 };


 // Utility to normalize scenes
 function normalizeScenes(scenes: any[]) {
   return scenes.map(scene => ({
     ...scene,
     timeout_turns:
       scene.timeout_turns !== undefined && scene.timeout_turns !== null
         ? scene.timeout_turns
         : 15,
   }));
 }


 // Helper to extract likely player name from the title
 function extractPlayerName(title: string) {
   if (!title) return "";
   // e.g., "Greg James at Sun Microsystems" => "Greg James"
   const match = title.match(/^([^,\-@]+?)(?:\s+at|\s+in|,|\-|$)/i);
   return match ? match[1].trim() : title.trim();
 }


 // Helper to normalize names for comparison
 function normalizeName(name: string) {
   return name ? name.replace(/[^a-zA-Z ]/g, "").toLowerCase().trim() : "";
 }


 function isLikelySamePerson(playerName: string, personaName: string) {
   const nPlayer = normalizeName(playerName);
   const nPersona = normalizeName(personaName);
   if (!nPlayer || !nPersona) return false;
   if (nPlayer === nPersona) return true;
   // Split into words and check for overlap
   const playerWords = nPlayer.split(" ").filter(Boolean);
   const personaWords = nPersona.split(" ").filter(Boolean);
   const overlap = playerWords.filter(word => personaWords.includes(word));
   return overlap.length >= 2; // At least first and last name match
 }


 // Helper to format description with proper paragraphs
 function formatDescription(text: string): string {
   if (!text) return '';
   
   // Split by common paragraph separators
   let paragraphs = text.split(/\n\s*\n/);
   
   // If no double line breaks, try splitting by single line breaks
   if (paragraphs.length <= 1) {
     paragraphs = text.split(/\n/);
   }
   
   // If still only one paragraph, try to break it up by sentences
   if (paragraphs.length <= 1) {
     const sentences = text.match(/[^.!?]+[.!?]+/g) || [];
     if (sentences.length > 2) {
       // Group sentences into paragraphs (2-3 sentences per paragraph)
       const groupedParagraphs = [];
       for (let i = 0; i < sentences.length; i += 2) {
         const paragraph = sentences.slice(i, i + 2).join(' ').trim();
         if (paragraph) groupedParagraphs.push(paragraph);
       }
       paragraphs = groupedParagraphs;
     }
   }
   
   // Clean up each paragraph
   paragraphs = paragraphs
     .map(p => p.trim())
     .filter(p => p.length > 0)
     .map(p => {
       // Remove excessive whitespace
       p = p.replace(/\s+/g, ' ');
       // Ensure proper sentence endings
       if (!p.endsWith('.') && !p.endsWith('!') && !p.endsWith('?')) {
         p += '.';
       }
       return p;
     });
   
   // Join with double line breaks for proper paragraph separation
   return paragraphs.join('\n\n');
 }

 // Helper to extract likely player names from the title and description
 function extractPlayerNames(title: string, description: string) {
   const names: string[] = [];
   // Extract all 'Firstname Lastname' patterns from the entire description
   if (description) {
     const nameMatches = [...description.matchAll(/([A-Z][a-z]+ [A-Z][a-z]+)/g)];
     for (const match of nameMatches) {
       const name = match[1].trim();
       if (!names.includes(name)) names.push(name);
     }
   }
   // Fallback: try to extract from the title
   if (title) {
     const match = title.match(/([A-Z][a-z]+ [A-Z][a-z]+)/);
     if (match && !names.includes(match[1].trim())) names.push(match[1].trim());
   }
   return names;
 }

 // Helper to extract single names that might be the main character
 function extractSingleNames(title: string, description: string) {
   const names: string[] = [];
   const text = `${title} ${description}`;
   
   // Look for capitalized single names (likely main characters)
   const singleNameMatches = [...text.matchAll(/\b([A-Z][a-z]{2,})\b/g)];
   for (const match of singleNameMatches) {
     const name = match[1].trim();
     // Filter out common words that aren't names
     const commonWords = ['the', 'and', 'for', 'with', 'from', 'this', 'that', 'they', 'their', 'company', 'network', 'ltd', 'inc', 'corp'];
     if (!commonWords.includes(name.toLowerCase()) && name.length > 2) {
       if (!names.includes(name)) names.push(name);
     }
   }
   
   return names;
 }


 function isLikelySamePersonFuzzy(playerNames: string[], personaName: string) {
   const nPersona = normalizeName(personaName);
   return playerNames.some(playerName => {
     const nPlayer = normalizeName(playerName);
     const playerWords = nPlayer.split(" ").filter(Boolean);
     // Require all player words (e.g., first and last name) to be present in persona name
     return playerWords.length > 1 && playerWords.every(word => nPersona.includes(word));
   });
 }


 // When autofillResult changes, update personas state (only if it contains personas array)
 useEffect(() => {
   // Only run this if we have personas in the old format
   if (
     autofillResult &&
     autofillResult.ai_result &&
     Array.isArray(autofillResult.ai_result.personas) &&
     autofillResult.ai_result.personas.length > 0 &&
     !autofillResult.ai_result.key_figures // Only run if we don't have key_figures (old format)
   ) {
     console.log("[DEBUG] Found personas in autofillResult, applying legacy persona processing");
     const playerNames = extractPlayerNames(name, description);
     console.log("[DEBUG] Extracted player names:", playerNames);
     const mainCharacter = playerNames[0]?.toLowerCase().trim();
     autofillResult.ai_result.personas.forEach((persona: any) => {
       console.log(`[DEBUG] Persona: '${persona.name}', Excluded: ${persona.name?.toLowerCase().trim() === mainCharacter}`);
     });
     const filtered = autofillResult.ai_result.personas.filter((persona: any) => {
       return persona.name?.toLowerCase().trim() !== mainCharacter;
     }).map((persona: any) => ({
       ...persona,
       traits: { ...persona.traits }, // editable traits
       defaultTraits: { ...persona.traits } // original LLM traits
     }));
     setPersonas(filtered);
   } else {
     console.log("[DEBUG] No personas array in autofillResult or key_figures present, skipping legacy persona processing");
   }
 }, [autofillResult, name, description]);


 // Update persona traits handler
 const handleTraitsChange = (idx: number, newTraits: any) => {
   // Check if we're editing a temporary persona
   if (editingIdx !== null && tempPersonas[editingIdx]?.isTemp) {
     setTempPersonas(tempPersonas => tempPersonas.map((p, i) => i === idx ? { ...p, traits: { ...newTraits } } : p));
   } else {
     setPersonas(personas => personas.map((p, i) => i === idx ? { ...p, traits: { ...newTraits } } : p));
   }
 };


 // Save persona edits handler
 const handleSavePersona = (idx: number, updatedPersona: any) => {
   if (updatedPersona.isTemp) {
     // This is a temporary persona being saved for the first time
     const { isTemp, ...personaToSave } = updatedPersona; // Remove isTemp flag
     personaToSave.id = `persona-${Date.now()}-${idx}`; // Generate permanent ID
     
     // Remove from temp personas and add to permanent personas at the top
     setTempPersonas(tempPersonas => tempPersonas.filter((_, i) => i !== idx));
     setPersonas(personas => [personaToSave, ...personas]);
   } else {
     // This is an existing persona being updated
     setPersonas(personas => personas.map((p, i) => i === idx ? { ...updatedPersona } : p));
   }
   setEditingIdx(null);
 };


 // Delete persona handler
 const handleDeletePersona = (idx: number) => {
   // Check if we're editing a temporary persona
   if (editingIdx !== null && tempPersonas[editingIdx]?.isTemp) {
     // Delete from temporary personas
     setTempPersonas(tempPersonas => tempPersonas.filter((_, i) => i !== idx));
   } else {
     // Delete from permanent personas
     setPersonas(personas => personas.filter((_, i) => i !== idx));
   }
   setEditingIdx(null);
 };

 // Scene management handlers
 const handleSaveScene = (idx: number, updatedScene: any) => {
   setScenes(scenes => scenes.map((s, i) => {
     if (i === idx) {
       // Merge the updated scene, preserving all new fields (like timeout_turns)
       return { ...s, ...updatedScene };
     }
     return s;
   }));
   setEditingSceneIdx(null);
 };

 const handleDeleteScene = (idx: number) => {
   setScenes(scenes => scenes.filter((_, i) => i !== idx));
   setEditingSceneIdx(null);
 };




 return (
   <div className="min-h-screen bg-background text-foreground flex flex-col items-center py-10 px-2">
     {/* Left overlay sidebar */}
     <div className="fixed top-0 left-0 h-full w-72 z-50 bg-black shadow-2xl flex flex-col items-start pl-8 pt-8">
       <h1 className="mb-10 text-white text-xl font-bold mb-6">
         Simulation Builder
       </h1>
       <Link href="/dashboard" className="mb-6">
         <button className="bg-white text-black rounded px-4 py-2 font-medium shadow hover:bg-gray-200 transition">Back to Dashboard</button>
             </Link>
       {/* Add sidebar navigation or content here */}
     </div>
     {/* Add left padding to prevent content from being hidden under the sidebar */}
     <div className="w-72 h-0" />
     {/* Top overlay bar */}
     <div className="fixed top-0 left-0 w-full z-40 bg-background shadow-lg flex items-center justify-between h-14 px-8">
       <span className="text-lg font-semibold">Simulation Builder</span>
       <div className="flex gap-4">
         <button 
           onClick={handleSave}
           disabled={isSaving}
           className={`rounded px-4 py-2 font-medium shadow transition flex items-center gap-2 ${
             isSaved 
               ? "bg-green-100 text-green-800 border border-green-300" 
               : "bg-white text-black hover:bg-gray-200"
           } ${isSaving ? "opacity-50 cursor-not-allowed" : ""}`}
         >
           {isSaving ? (
             "Saving..."
           ) : isSaved ? (
             <>
               <Check className="h-4 w-4" />
               Saved
             </>
           ) : (
             "Save"
           )}
         </button>
         <button 
           onClick={handlePublish}
           disabled={isPublishing}
           className={`rounded px-4 py-2 font-medium shadow transition flex items-center gap-2 ${
             isPublished 
               ? "bg-green-600 text-white" 
               : "bg-black text-white hover:bg-gray-800"
           } ${isPublishing ? "opacity-50 cursor-not-allowed" : ""}`}
         >
           {isPublishing ? (
             "Publishing..."
           ) : isPublished ? (
             <>
               <Check className="h-4 w-4" />
               Published
             </>
           ) : (
             "Publish"
           )}
         </button>
         {autofillResult && (
           <button 
             onClick={handlePlayScenario}
             className="bg-blue-600 text-white rounded px-4 py-2 font-medium shadow hover:bg-blue-700 transition flex items-center gap-2"
           >
             <Activity className="h-4 w-4" />
             Play Scenario
           </button>
         )}
       </div>
     </div>
     {/* Add top padding to prevent content from being hidden under the bar */}
     <div className="h-14" />
     {/* Main content shifted further right to avoid sidebar overlap */}
     <div className="pl-[26rem] w-full">
       {/* Header and Upload Row */}
       <div className="w-full max-w-4xl grid grid-cols-1 md:grid-cols-2 gap-8 mb-8 items-start">
         {/* Left: Title and Subtitle */}
         <div className="flex flex-col gap-2">
           <h1 className="text-2xl font-bold">Upload your Business Case Study</h1>
           <p className="text-muted-foreground text-sm">We will analyze the contents and autofill the configuration for you.</p>
         </div>
         {/* Right: Drag and Drop File Upload Box */}
         <div
           className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 flex flex-col items-center justify-center min-h-[120px] cursor-pointer ${
             isDragOver
               ? 'border-blue-500 bg-blue-50 scale-105'
               : uploadedFile && uploadedFile.type === "application/pdf"
               ? 'border-green-500 bg-green-50'
               : 'border-gray-300 bg-card hover:border-gray-400'
           }`}
           onDragOver={handleDragOver}
           onDragLeave={handleDragLeave}
           onDrop={handleDrop}
           onClick={() => fileInputRef.current?.click()}
         >
           {uploadedFile && uploadedFile.type === "application/pdf" ? (
             <span className="flex flex-col items-center">
               {/* Simple PDF icon using SVG */}
               <svg className="h-10 w-10 mx-auto mb-2 text-red-500" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                 <path d="M6 2a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6H6z" />
                 <path d="M14 2v6h6" />
               </svg>
               <span className="text-xs text-red-500 font-semibold">PDF attached</span>
             </span>
           ) : (
             <Upload className={`h-10 w-10 mx-auto mb-2 ${isDragOver ? 'text-blue-500' : 'text-muted-foreground'}`} />
           )}
          
           {!(uploadedFile && uploadedFile.type === "application/pdf") && (
             <span className={`font-medium ${isDragOver ? 'text-blue-600' : 'text-muted-foreground'}`}>
               {isDragOver ? (
                 <span>Drop your PDF here</span>
               ) : (
                 <span><span className="underline">Click here</span> to upload your PDF or drag and drop</span>
               )}
             </span>
           )}
          
           <input
             id="file-upload"
             type="file"
             accept=".pdf"
             className="hidden"
             onChange={handleFileChange}
             ref={fileInputRef}
           />
          
           {uploadedFile && (
             <div className="mt-2 text-primary text-sm font-medium">{uploadedFile.name}</div>
           )}
         </div>
         <div className="flex gap-2 justify-right">


         </div>
         {/* Buttons directly below the upload box, perfectly aligned */}
         {uploadedFile && (
           <div className="flex ml-25 gap-2 justify-right">
             {/* Choose a different file */}
             <label htmlFor="file-upload" className="cursor-pointer m-0">
               <button
                 type="button"
                 onClick={handleChooseDifferentFile}
                 className="bg-white text-black rounded px-4 py-2 font-medium shadow hover:bg-gray-200 transition border border-gray-300 w-full h-full align-middle"
               >
                 Choose a different file
               </button>
             </label>
             {/* Use and autofill */}
             <button
               className="bg-black text-white rounded px-2 py-2 font-medium shadow hover:bg-gray-800 transition border border-black w-1000 h-10 align-middle flex items-center justify-center"
               onClick={handleAutofill}
               disabled={autofillLoading}
             >
               <Sparkles className="mr-2 h-4 w-4 text-white inline" />
               Use and autofill
             </button>
           </div>
         )}
         {/* Show loading progress */}
         {autofillLoading && (
           <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
             <div className="flex items-center justify-between mb-2">
               <span className="text-sm font-medium text-blue-800">{autofillStep}</span>
               <span className="text-xs text-blue-600">{Math.round(autofillProgress)}%</span>
             </div>
             <Progress value={autofillProgress} className="w-full h-2" />
           </div>
         )}
        
         {/* Show error */}
         {autofillError && (
           <div className="mt-4 p-4 bg-red-50 rounded-lg border border-red-200">
             <div className="flex items-center">
               <span className="text-red-600 font-medium">Error:</span>
               <span className="text-red-600 ml-2">{autofillError}</span>
             </div>
           </div>
         )}
        
         {/* Show success message */}
         {autofillResult && autofillStep === "Complete!" && (
           <div className="mt-4 p-4 bg-green-50 rounded-lg border border-green-200">
             <div className="flex items-center">
               <span className="text-green-600 font-medium">✓ Success!</span>
               <span className="text-green-600 ml-2">PDF content has been mapped to your form fields.</span>
             </div>
           </div>
         )}
       </div>


       {/* Accordions */}
       <div className="w-full max-w-4xl">
         <Accordion type="multiple" className="space-y-6" defaultValue={['info', 'personas', 'timeline']}>
           {/* Information Accordion */}
           <AccordionItem value="info">
             <AccordionTrigger className="flex items-center gap-2 text-lg font-semibold justify-start text-left">
               <Info className="h-5 w-5" />
               Information
               <span className="ml-2 text-muted-foreground text-sm font-normal">The overall description of the simulation. This is the foundation and sense of direction.</span>
             </AccordionTrigger>
             <AccordionContent className="overflow-visible" style={{ overflow: 'visible' }}>
               <div className="space-y-5 pt-4 w-full mx-auto overflow-visible">
                 <div className="overflow-visible focus-within:overflow-visible">
                   <Label htmlFor="name">Name</Label>
                   <Input id="name" value={name} onChange={e => {
                  setName(e.target.value);
                  markAsUnsaved();
                }} className="mt-1 w-full box-border p-2" />
                 </div>
                 <div className="overflow-visible focus-within:overflow-visible rounded-none">
                   <Label htmlFor="description">Description/Background</Label>
                   <Textarea
                     id="description"
                     value={description}
                     onChange={e => {
                       setDescription(e.target.value);
                       markAsUnsaved();
                     }}
                     className="mt-1 w-full overflow-visible rounded-none z-10 p-2 min-h-[200px] resize-y"
                     style={{ minHeight: '200px', maxHeight: '400px' }}
                   />
                 </div>
                 <div className="overflow-visible focus-within:overflow-visible">
                   <Label htmlFor="learning-outcomes">Learning Outcomes</Label>
                   <Textarea
                     id="learning-outcomes"
                     value={learningOutcomes}
                     onChange={e => {
                       setLearningOutcomes(e.target.value);
                       markAsUnsaved();
                     }}
                     className="mt-1 w-full box-border p-2 min-h-[200px] resize-y"
                     style={{ minHeight: '200px', maxHeight: '400px' }}
                   />
                 </div>
                           <div>
                   <Label className="block mb-1">Files</Label>
                   <span className="block text-muted-foreground text-xs mb-2">Use this to give more context to the simulation</span>
                   <Button variant="outline" onClick={handleUploadFilesClick}>Upload Files</Button>
                   <input
                     type="file"
                     multiple
                     className="hidden"
                     ref={filesInputRef}
                     onChange={handleFilesChange}
                   />
                   {uploadedFiles.length > 0 && (
                     <ul className="mt-2 text-xs text-muted-foreground">
                       {uploadedFiles.map((file, idx) => (
                         <li key={idx} className="flex items-center gap-2">
                           {file.name}
                           <button
                             type="button"
                             className="ml-1 text-red-500 hover:text-red-700"
                             onClick={() => handleRemoveFile(idx)}
                             aria-label={`Remove ${file.name}`}
                           >
                             <X className="w-3 h-3" />
                           </button>
                         </li>
                       ))}
                     </ul>
                   )}
                 </div>
               </div>
             </AccordionContent>
           </AccordionItem>


           {/* Personas Accordion */}
           <AccordionItem value="personas">
             <AccordionTrigger className="flex items-center gap-2 text-lg font-semibold justify-start text-left">
               <Users className="h-5 w-5" />
               Personas
               <span className="ml-2 text-muted-foreground text-sm font-normal">The characters the user will interact during the simulation with their own personality and goals.</span>
             </AccordionTrigger>
             <AccordionContent>
               <div className="flex flex-col items-center py-6">
                 <Button onClick={handleAddPersona} variant="outline" className="w-60">Add new persona</Button>
                 {/* Render persona cards here, excluding the player character */}
                 {(tempPersonas.length > 0 || personas.length > 0) && (
                   // Debug log to show which personas are being rendered
                   console.log("[DEBUG] Temp personas to render:", tempPersonas.map(p => p.name)),
                   console.log("[DEBUG] Permanent personas to render:", personas.map(p => p.name)),
                   <div className="w-full flex flex-col items-center mt-6">
                     {/* Render temporary personas first (at the top) */}
                     {tempPersonas.map((persona: any, idx: number) => (
                       <div key={`temp-${idx}`} className="relative w-full">
                         <div onClick={() => setEditingIdx(idx)} style={{ cursor: 'pointer' }}>
                           <PersonaCard
                             persona={{ ...persona, traits: persona.traits }}
                             defaultTraits={persona.defaultTraits}
                             onTraitsChange={newTraits => handleTraitsChange(idx, newTraits)}
                             onSave={updatedPersona => handleSavePersona(idx, updatedPersona)}
                             onDelete={() => handleDeletePersona(idx)}
                             editMode={false}
                           />
                         </div>
                       </div>
                     ))}
                     {/* Render permanent personas */}
                     {personas.map((persona: any, idx: number) => (
                       <div key={`perm-${idx}`} className="relative w-full">
                         <div onClick={() => setEditingIdx(idx)} style={{ cursor: 'pointer' }}>
                           <PersonaCard
                             persona={{ ...persona, traits: persona.traits }}
                             defaultTraits={persona.defaultTraits}
                             onTraitsChange={newTraits => handleTraitsChange(idx, newTraits)}
                             onSave={updatedPersona => handleSavePersona(idx, updatedPersona)}
                             onDelete={() => handleDeletePersona(idx)}
                             editMode={false}
                           />
                         </div>
                       </div>
                     ))}
                   </div>
                 )}
               </div>
             </AccordionContent>
           </AccordionItem>


           {/* Timeline Accordion */}
           <AccordionItem value="timeline">
             <AccordionTrigger className="flex items-center gap-2 text-lg font-semibold justify-start text-left">
               <Activity className="h-5 w-5" />
               Timeline
               <span className="ml-2 text-muted-foreground text-sm font-normal">These are the sequence of events the user needs to solve for during the simulation.</span>
             </AccordionTrigger>
             <AccordionContent>
               <div className="py-4">
                 <p className="text-muted-foreground text-sm mb-6">Think of each segment as a self-contained mini-level in your simulation. Arrange them from top to bottom, this will be the sequence each scene will take place in.</p>
                 <div className="flex flex-col items-center">
                   <Button onClick={handleAddScene} variant="outline" className="w-60">Add new Scene</Button>
                   
                   {/* Render scene cards */}
                   {scenes.length > 0 && (
                     <div className="w-full flex flex-col items-center mt-6">
                       {scenes
                         .sort((a, b) => a.sequence_order - b.sequence_order)
                         .map((scene: any, idx: number) => (
                         <div key={scene.id} className="relative w-full">
                           <div onClick={() => setEditingSceneIdx(idx)} style={{ cursor: 'pointer' }}>
                             <SceneCard
                               scene={scene}
                               onSave={updatedScene => handleSaveScene(idx, updatedScene)}
                               onDelete={() => handleDeleteScene(idx)}
                               editMode={false}
                               allPersonas={[...personas, ...tempPersonas]}
                               studentRole={autofillResult?.student_role || ""}
                             />
                           </div>
                         </div>
                       ))}
                     </div>
                   )}
                 </div>
               </div>
             </AccordionContent>
           </AccordionItem>
         </Accordion>
       </div>
     </div>
     {/* Modal for editing persona */}
     {editingIdx !== null && (
       <PersonaModal isOpen={true} onClose={() => setEditingIdx(null)}>
         <PersonaCard
           persona={{ 
             ...(editingIdx < tempPersonas.length ? tempPersonas[editingIdx] : personas[editingIdx - tempPersonas.length]), 
             traits: (editingIdx < tempPersonas.length ? tempPersonas[editingIdx] : personas[editingIdx - tempPersonas.length]).traits 
           }}
           defaultTraits={(editingIdx < tempPersonas.length ? tempPersonas[editingIdx] : personas[editingIdx - tempPersonas.length]).defaultTraits}
           onTraitsChange={newTraits => handleTraitsChange(editingIdx, newTraits)}
           onSave={updatedPersona => handleSavePersona(editingIdx, updatedPersona)}
           onDelete={() => handleDeletePersona(editingIdx)}
           editMode={true}
         />
       </PersonaModal>
     )}
     
     {/* Modal for editing scene */}
     {editingSceneIdx !== null && (
       <SceneModal isOpen={true} onClose={() => setEditingSceneIdx(null)}>
         <SceneCard
           scene={scenes[editingSceneIdx]}
           onSave={updatedScene => handleSaveScene(editingSceneIdx, updatedScene)}
           onDelete={() => handleDeleteScene(editingSceneIdx)}
           editMode={true}
           allPersonas={[...personas, ...tempPersonas]}
           studentRole={autofillResult?.student_role || ""}
         />
       </SceneModal>
     )}
   </div>
 )
}
