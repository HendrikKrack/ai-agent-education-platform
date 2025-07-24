"use client"

import React, { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { 
  Send, 
  Users, 
  Target, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  HelpCircle,
  Play,
  RefreshCw,
  ArrowRight,
  BookOpen,
  User
} from "lucide-react"
import { buildApiUrl } from "@/lib/api"

// Types aligned with backend database schema
interface Scenario {
  id: number
  title: string
  description: string
  challenge: string
  industry?: string
  learning_objectives: string[]
  student_role?: string
  created_at: string
  is_public: boolean
}

interface Persona {
  id: number
  name: string
  role: string
  background: string
  correlation: string
  primary_goals: string[]
  personality_traits: Record<string, number>
}

interface Scene {
  id: number
  title: string
  description: string
  user_goal?: string
  scene_order: number
  estimated_duration?: number
  image_url?: string
  personas: Persona[]
  timeout_turns?: number // Add this line
}

interface SimulationData {
  user_progress_id: number
  scenario: Scenario
  current_scene: Scene
  simulation_status: string
}

interface Message {
  id: number
  sender: string
  text: string
  timestamp: Date
  type: 'user' | 'ai_persona' | 'system' | 'orchestrator'
  persona_id?: number
  persona_name?: string  // Add persona name for display
  scene_completed?: boolean  // Add scene completion flag
  next_scene_id?: number  // Add next scene ID for progression
}

// Scenario Selection Component
const ScenarioSelector = ({ 
  onScenarioSelect 
}: { 
  onScenarioSelect: (scenarioId: number) => void 
}) => {
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedScenario, setSelectedScenario] = useState<number | null>(null)

  useEffect(() => {
    fetchScenarios()
  }, [])

  const fetchScenarios = async () => {
    try {
      const response = await fetch(buildApiUrl("/api/scenarios/"))
      if (response.ok) {
        const data = await response.json()
        // Filter scenarios that have both personas and scenes
        const validScenarios = data.filter((s: any) => 
          s.personas && s.personas.length > 0 && 
          s.scenes && s.scenes.length > 0
        )
        setScenarios(validScenarios)
        
        // Auto-select the most recent scenario
        if (validScenarios.length > 0) {
          const mostRecent = validScenarios.reduce((latest: any, current: any) => 
            new Date(current.created_at) > new Date(latest.created_at) ? current : latest
          )
          setSelectedScenario(mostRecent.id)
        }
      }
    } catch (error) {
      console.error("Failed to fetch scenarios:", error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Card className="max-w-2xl mx-auto">
        <CardContent className="p-6 text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4" />
          <p>Loading available scenarios...</p>
        </CardContent>
      </Card>
    )
  }

  if (scenarios.length === 0) {
    return (
      <Card className="max-w-2xl mx-auto">
        <CardContent className="p-6 text-center">
          <BookOpen className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          <h3 className="text-lg font-semibold mb-2">No Scenarios Available</h3>
          <p className="text-gray-600 mb-4">
            You need to create a scenario first using the Scenario Builder.
          </p>
          <Button onClick={() => window.open("/scenario-builder", "_blank")}>
            Create Scenario
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Play className="w-5 h-5" />
            Select a Scenario to Simulate
          </CardTitle>
          <p className="text-sm text-gray-600">
            Choose from your available scenarios with AI personas and scenes
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          {scenarios.map((scenario) => (
            <div
              key={scenario.id}
              className={`border rounded-lg p-4 cursor-pointer transition-all hover:shadow-md ${
                selectedScenario === scenario.id 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-gray-200'
              }`}
              onClick={() => setSelectedScenario(scenario.id)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="font-semibold">{scenario.title}</h3>
                    {scenario.is_public && (
                      <Badge variant="secondary" className="text-xs">Public</Badge>
                    )}
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                    {scenario.description}
                  </p>
                  
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span className="flex items-center gap-1">
                      <User className="w-3 h-3" />
                      {scenario.student_role || "Student"}
                    </span>
                    <span className="flex items-center gap-1">
                      <Users className="w-3 h-3" />
                      Multiple Personas
                    </span>
                    <span className="flex items-center gap-1">
                      <Target className="w-3 h-3" />
                      Multi-Scene
                    </span>
                  </div>
                </div>
                
                <div className="ml-4 flex flex-col items-end gap-2">
                  <Badge variant="outline" className="text-xs">
                    ID: {scenario.id}
                  </Badge>
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={async (e) => {
                      e.stopPropagation();
                      if (!window.confirm(`Delete scenario '${scenario.title}'? This cannot be undone.`)) return;
                      try {
                        const res = await fetch(buildApiUrl(`/api/scenarios/${scenario.id}`), { method: 'DELETE' });
                        if (!res.ok) throw new Error('Failed to delete');
                        setScenarios(scenarios => scenarios.filter(s => s.id !== scenario.id));
                        if (selectedScenario === scenario.id) setSelectedScenario(null);
                      } catch (err) {
                        alert('Failed to delete scenario.');
                      }
                    }}
                  >
                    Delete
                  </Button>
                </div>
              </div>
            </div>
          ))}
          
          <div className="pt-4 border-t">
            <Button 
              onClick={() => selectedScenario && onScenarioSelect(selectedScenario)}
              disabled={!selectedScenario}
              className="w-full"
              size="lg"
            >
              <Play className="w-4 h-4 mr-2" />
              Start Simulation
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Scene Progress Component
const SceneProgress = ({ 
  currentScene, 
  totalScenes, 
  completedScenes 
}: { 
  currentScene: number
  totalScenes: number
  completedScenes: number[]
}) => {
  const progress = (completedScenes.length / totalScenes) * 100

  return (
    <Card className="mb-4">
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-semibold text-sm">Scene Progress</h3>
          <span className="text-xs text-gray-500">
            Scene {currentScene} of {totalScenes}
          </span>
        </div>
        <Progress value={progress} className="mb-2" />
        <div className="flex justify-between text-xs text-gray-500">
          <span>{completedScenes.length} completed</span>
          <span>{Math.round(progress)}%</span>
        </div>
      </CardContent>
    </Card>
  )
}

// Current Scene Info
const CurrentSceneInfo = ({ scene }: { scene: Scene }) => {
  return (
    <Card className="mb-4">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm flex items-center gap-2">
          <Target className="w-4 h-4 text-blue-500" />
          Current Scene
        </CardTitle>
      </CardHeader>
      <CardContent>
        <h3 className="font-semibold mb-2">{scene.title}</h3>
        
        {/* Scene Image */}
        {scene.image_url && (
          <div className="mb-3">
            <img 
              src={scene.image_url} 
              alt={scene.title}
              className="w-full h-32 object-cover rounded-lg border"
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.style.display = 'none';
              }}
            />
          </div>
        )}
        
        <p className="text-sm text-gray-600 mb-3">{scene.description}</p>
        
        {scene.user_goal && (
          <div className="bg-blue-50 border border-blue-200 rounded p-3 mb-3">
            <p className="text-sm font-medium text-blue-800">Your Goal:</p>
            <p className="text-sm text-blue-700">{scene.user_goal}</p>
          </div>
        )}
        
        {/* Always display timeout_turns */}
        <div className="bg-yellow-50 border border-yellow-200 rounded p-3 mb-3">
          <p className="text-sm font-medium text-yellow-800">Timeout Turns:</p>
          <p className="text-sm text-yellow-700">{typeof scene.timeout_turns === 'number' ? scene.timeout_turns : 'Not set'}</p>
        </div>
        
        {scene.personas && scene.personas.length > 0 && (
          <div>
            <p className="text-xs font-medium text-gray-700 mb-2">Available Personas:</p>
            <div className="flex flex-wrap gap-1">
              {scene.personas.map((persona) => (
                <Badge key={persona.id} variant="secondary" className="text-xs">
                  {persona.name}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// Typing Indicator
const TypingIndicator = ({ personaName }: { personaName: string }) => (
  <div className="flex justify-start mb-4">
    <div className="bg-gray-100 rounded-lg px-4 py-2 border">
      <div className="flex items-center gap-2">
        <div className="flex space-x-1">
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        </div>
        <span className="text-xs text-gray-600">{personaName} is typing...</span>
      </div>
    </div>
  </div>
)

export default function LinearSimulationChat() {
  // Core simulation state
  const [simulationData, setSimulationData] = useState<SimulationData | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isTyping, setIsTyping] = useState(false)
  const [typingPersona, setTypingPersona] = useState("")
  
  // UI state
  const [selectedScenarioId, setSelectedScenarioId] = useState<number | null>(null)
  const [completedScenes, setCompletedScenes] = useState<number[]>([])
  
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // Start simulation with selected scenario
  const startSimulation = async (scenarioId: number) => {
    setSelectedScenarioId(scenarioId)
    setIsLoading(true)
    
    try {
      const response = await fetch(buildApiUrl("/api/simulation/start"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          scenario_id: scenarioId,
          user_id: 1 // Hardcoded for now - should come from auth
        })
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`)
      }

      const data: SimulationData = await response.json()
      setSimulationData(data)
      
      // Add welcome message
      setMessages([{
        id: Date.now(),
        sender: "System",
        text: `🎯 **${data.scenario.title}**\n\n${data.scenario.description}\n\n**Your Role:** ${data.scenario.student_role}\n\n**Current Scene:** ${data.current_scene.title}\n\n**Instructions:**\n• Type **"begin"** to start the simulation\n• Type **"help"** for available commands\n• Use natural conversation to interact with personas`,
        timestamp: new Date(),
        type: 'system'
      }])

    } catch (error) {
      console.error("Failed to start simulation:", error)
      alert(`Failed to start simulation: ${error}`)
    } finally {
      setIsLoading(false)
    }
  }



  // Send message to orchestrator
  const sendMessage = async () => {
    if (!simulationData || !input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now(),
      sender: "You",
      text: input.trim(),
      timestamp: new Date(),
      type: 'user'
    }

    setMessages(prev => [...prev, userMessage])
    setInput("")
    setIsLoading(true)
    setIsTyping(true)
    setTypingPersona("ChatOrchestrator")

    try {
      const response = await fetch(buildApiUrl("/api/simulation/linear-chat"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          scenario_id: simulationData.scenario.id,
          user_id: 1,
          scene_id: simulationData.current_scene.id,
          message: userMessage.text
        })
      })

      if (!response.ok) {
        throw new Error(`Chat failed: ${response.status}`)
      }

      const chatData = await response.json()
      
      // Simulate typing delay for better UX
      setTimeout(() => {
        setIsTyping(false)
        
        // Add orchestrator response with persona information
        const aiMessage: Message = {
          id: Date.now() + 1,
          sender: chatData.persona_name || "ChatOrchestrator",
          text: chatData.message,
          timestamp: new Date(),
          type: chatData.persona_name && chatData.persona_name !== "ChatOrchestrator" ? 'ai_persona' : 'orchestrator',
          persona_name: chatData.persona_name,
          persona_id: chatData.persona_id,
          scene_completed: chatData.scene_completed,
          next_scene_id: chatData.next_scene_id
        }
        setMessages(prev => [...prev, aiMessage])

        // Handle scene progression if indicated
        if (chatData.scene_completed) {
          setCompletedScenes(prev => [...prev, simulationData.current_scene.id])
          
          if (chatData.next_scene_id) {
            // Fetch next scene data and update simulationData
            fetch(buildApiUrl(`/api/simulation/scenes/${chatData.next_scene_id}`))
              .then(response => {
                if (response.ok) {
                  return response.json()
                }
                throw new Error('Failed to fetch next scene')
              })
              .then(nextSceneData => {
                // Update simulation data with new scene
                setSimulationData(prev => prev ? {
                  ...prev,
                  current_scene: nextSceneData
                } : null)
                
                // Add scene transition message
                const transitionMessage: Message = {
                  id: Date.now() + 2,
                  sender: "System",
                  text: `🎉 **Scene Completed!** Moving to Scene ${nextSceneData.scene_order}:\n\n**${nextSceneData.title}**\n${nextSceneData.description}\n\n**Objective:** ${nextSceneData.user_goal || 'Complete the scene'}`,
                  timestamp: new Date(),
                  type: 'system'
                }
                setMessages(prev => [...prev, transitionMessage])
              })
              .catch(error => {
                console.error("Failed to fetch next scene:", error)
                
                // Fallback completion message
                const completionMessage: Message = {
                  id: Date.now() + 2,
                  sender: "System",
                  text: "🎉 Scene completed! Moving to the next scene...",
                  timestamp: new Date(),
                  type: 'system'
                }
                setMessages(prev => [...prev, completionMessage])
              })
          }
        }
        
      }, 1500) // 1.5 second typing delay

    } catch (error) {
      console.error("Failed to send message:", error)
      setIsTyping(false)
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        sender: "System",
        text: `❌ Error: ${error}. Please try again or restart the simulation.`,
        timestamp: new Date(),
        type: 'system'
      }])
    } finally {
      setIsLoading(false)
    }
  }

  // Handle Enter key
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  // If no simulation is active, show scenario selection
  if (!simulationData) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-6xl mx-auto py-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold mb-2">Linear Simulation Experience</h1>
            <p className="text-gray-600">
              Select a scenario to begin your interactive simulation with AI personas
            </p>
          </div>
          
          <ScenarioSelector onScenarioSelect={startSimulation} />
        </div>
      </div>
    )
  }

  // Main simulation interface
  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        {/* Left Sidebar - Progress & Scene Info */}
        <div className="lg:col-span-1">
          <SceneProgress
            currentScene={simulationData.current_scene.scene_order}
            totalScenes={4} // This should come from scenario data
            completedScenes={completedScenes}
          />
          
          <CurrentSceneInfo scene={simulationData.current_scene} />
          
          <Card>
            <CardContent className="p-4">
              <div className="text-center">
                <Badge variant="outline" className="text-xs mb-2">
                  Scenario #{simulationData.scenario.id}
                </Badge>
                <p className="text-xs text-gray-500">
                  Linear Flow Integration Active
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Chat Area */}
        <div className="lg:col-span-3">
          <Card className="h-[85vh] flex flex-col">
            <CardHeader className="border-b">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">
                  {simulationData.scenario.title}
                </CardTitle>
                <div className="flex items-center gap-2">
                  <Badge variant="secondary">
                    {simulationData.current_scene.title}
                  </Badge>
                </div>
              </div>
            </CardHeader>

            {/* Messages Area */}
            <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
                    message.type === 'user'
                      ? 'bg-blue-500 text-white'
                      : message.type === 'system'
                      ? 'bg-gray-100 text-gray-800 border'
                      : message.type === 'ai_persona'
                      ? 'bg-green-50 text-gray-800 border border-green-200'
                      : message.type === 'orchestrator'
                      ? 'bg-white text-gray-800 border border-purple-200'
                      : 'bg-white text-gray-800 border'
                  }`}>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-semibold opacity-75">
                        {message.sender}
                      </span>
                      {message.type === 'ai_persona' && (
                        <Badge variant="secondary" className="text-xs bg-green-100 text-green-800">
                          {message.persona_name || 'Persona'}
                        </Badge>
                      )}
                      {message.type === 'orchestrator' && (
                        <Badge variant="secondary" className="text-xs">
                          AI
                        </Badge>
                      )}
                    </div>
                    <div className="text-sm whitespace-pre-wrap">
                      {/* Simple markdown-like formatting */}
                      {message.text.split('\n').map((line, index) => {
                        // Handle bold text with **
                        const boldFormatted = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        return (
                          <div key={index} dangerouslySetInnerHTML={{ __html: boldFormatted }} />
                        )
                      })}
                    </div>
                  </div>
                </div>
              ))}

              {isTyping && (
                <TypingIndicator personaName={typingPersona} />
              )}

              <div ref={messagesEndRef} />
            </CardContent>

            {/* Input Area */}
            <div className="border-t p-4">
              <div className="space-y-3">
                <div className="flex gap-2">
                  <Input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your message or command..."
                    disabled={isLoading || isTyping}
                    className="flex-1"
                  />
                  <Button
                    onClick={sendMessage}
                    disabled={isLoading || isTyping || !input.trim()}
                  >
                    {isLoading ? (
                      <RefreshCw className="w-4 h-4 animate-spin" />
                    ) : (
                      <Send className="w-4 h-4" />
                    )}
                  </Button>
                </div>
                
                {/* Quick command buttons */}
                <div className="flex gap-2 flex-wrap">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setInput("begin")}
                    disabled={isLoading || isTyping}
                  >
                    Begin
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setInput("help")}
                    disabled={isLoading || isTyping}
                  >
                    Help
                  </Button>
                  {simulationData.current_scene.personas && simulationData.current_scene.personas.length > 0 && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        const firstPersona = simulationData.current_scene.personas![0]
                        const mentionId = firstPersona.name.toLowerCase().replace(/\s+/g, '_')
                        setInput(`@${mentionId} `)
                      }}
                      disabled={isLoading || isTyping}
                    >
                      @{simulationData.current_scene.personas[0].name.split(' ')[0]}
                    </Button>
                  )}
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
} 