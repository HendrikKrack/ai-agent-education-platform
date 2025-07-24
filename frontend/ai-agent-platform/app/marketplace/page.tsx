"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Bot, Search, Star, Download, Heart, Users, ArrowLeft, Filter, TrendingUp, AlertCircle } from "lucide-react"
import { useAuth } from "@/lib/auth-context"
import { apiClient, Agent, Scenario } from "@/lib/api"

export default function Marketplace() {
  const router = useRouter()
  const { user, isAuthenticated } = useAuth()
  
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("all")
  const [agents, setAgents] = useState<Agent[]>([])
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [favorites, setFavorites] = useState<Set<string>>(new Set())

  const categories = [
    "All",
    "Customer Service",
    "Data Analysis",
    "Content Creation",
    "Sales & Marketing",
    "Research",
    "Automation",
    "Education",
    "Finance",
  ]

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!user && !loading) {
      router.push('/login')
    }
  }, [user, router, loading])

  // Fetch agents and scenarios
  useEffect(() => {
    const fetchData = async () => {
      if (!isAuthenticated) return
      
      try {
        const [agentsData, scenariosData] = await Promise.all([
          apiClient.getAgents(),
          apiClient.getScenarios()
        ])
        
        setAgents(agentsData)
        setScenarios(scenariosData)
      } catch (err) {
        console.error('Error fetching marketplace data:', err)
        setError('Failed to load marketplace data')
      } finally {
        setLoading(false)
      }
    }

    if (isAuthenticated) {
      fetchData()
    }
  }, [isAuthenticated])

  const filteredAgents = agents.filter(agent => {
    const matchesSearch = agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         agent.role.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         agent.backstory.toLowerCase().includes(searchQuery.toLowerCase())
    
    const matchesCategory = selectedCategory === 'all' || 
                           (agent.category && agent.category.toLowerCase() === selectedCategory.toLowerCase())
    
    return matchesSearch && matchesCategory
  })

  const filteredScenarios = scenarios.filter(scenario => {
    const matchesSearch = scenario.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         scenario.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         (scenario.industry && scenario.industry.toLowerCase().includes(searchQuery.toLowerCase()))
    
    const matchesCategory = selectedCategory === 'all' || 
                           (scenario.industry && scenario.industry.toLowerCase() === selectedCategory.toLowerCase())
    
    return matchesSearch && matchesCategory
  })

  const toggleFavorite = (id: string) => {
    const newFavorites = new Set(favorites)
    if (newFavorites.has(id)) {
      newFavorites.delete(id)
    } else {
      newFavorites.add(id)
    }
    setFavorites(newFavorites)
  }

  const cloneAgent = async (agent: Agent) => {
    try {
      // Create a copy of the agent
      const clonedAgent = await apiClient.createAgent({
        name: `${agent.name} (Clone)`,
        description: agent.description,
        role: agent.role,
        personality: agent.personality,
        expertise: agent.expertise,
        goal: agent.goal,
        backstory: agent.backstory,
        tools: agent.tools,
        verbose: agent.verbose,
        allow_delegation: agent.allow_delegation,
        reasoning: agent.reasoning,
        category: agent.category,
        tags: [...agent.tags, 'cloned'],
        is_public: false,
        is_template: false,
        allow_remixes: agent.allow_remixes,
        version: '1.0.0',
        version_notes: `Cloned from ${agent.name}`,
        clone_count: 0,
      })
      
      // Navigate to agent builder to edit the cloned agent
      router.push(`/agent-builder?edit=${clonedAgent.id}`)
    } catch (err) {
      console.error('Error cloning agent:', err)
      setError('Failed to clone agent')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-yellow-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p>Loading marketplace...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return null // Will redirect to login
  }

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="border-b border-yellow-500/20 bg-black/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button variant="ghost" size="sm" asChild>
              <Link href="/dashboard">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Link>
            </Button>
            <div className="flex items-center space-x-2">
              <Users className="h-6 w-6 text-yellow-500" />
              <span className="text-xl font-bold">Marketplace</span>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm" className="border-yellow-500/30 text-yellow-500 bg-transparent">
              <Heart className="h-4 w-4 mr-2" />
              My Favorites ({favorites.size})
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-4">
            Discover Amazing <span className="text-yellow-500">AI Agents</span>
          </h1>
          <p className="text-xl text-gray-400 mb-6">Browse, clone, and customize agents and scenarios created by the community</p>

          {/* Search and Filters */}
          <div className="max-w-2xl mx-auto flex space-x-4 mb-6">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search agents and scenarios..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 bg-gray-900 border-gray-700 focus:border-yellow-500"
              />
            </div>
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="w-48 bg-gray-900 border-gray-700 focus:border-yellow-500">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-gray-900 border-gray-700">
                {categories.map((category) => (
                  <SelectItem key={category} value={category.toLowerCase().replace(" ", "-")}>
                    {category}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button variant="outline" className="border-yellow-500/30 text-yellow-500 bg-transparent">
              <Filter className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {error && (
          <Card className="mb-6 bg-red-500/10 border-red-500/30">
            <CardContent className="pt-6">
              <div className="flex items-center space-x-2 text-red-400">
                <AlertCircle className="h-5 w-5" />
                <p>{error}</p>
              </div>
            </CardContent>
          </Card>
        )}

        <Tabs defaultValue="agents" className="space-y-6">
          <TabsList className="grid w-full grid-cols-2 bg-gray-900 max-w-md mx-auto">
            <TabsTrigger value="agents" className="data-[state=active]:bg-yellow-500 data-[state=active]:text-black">
              AI Agents ({filteredAgents.length})
            </TabsTrigger>
            <TabsTrigger value="scenarios" className="data-[state=active]:bg-yellow-500 data-[state=active]:text-black">
              Scenarios ({filteredScenarios.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="agents" className="space-y-8">
            {/* Featured Agents */}
            <section>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold flex items-center">
                  <Star className="h-6 w-6 mr-2 text-yellow-500" />
                  Featured Agents
                </h2>
              </div>
              
              {filteredAgents.length === 0 ? (
                <div className="text-center py-12 text-gray-400">
                  <Bot className="h-16 w-16 mx-auto mb-4 opacity-50" />
                  <p className="text-xl mb-2">No agents found</p>
                  <p>Try adjusting your search or filter criteria</p>
                </div>
              ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {filteredAgents.slice(0, 6).map((agent) => (
                    <Card
                      key={agent.id}
                      className="bg-gradient-to-br from-yellow-500/10 to-yellow-600/5 border-yellow-500/30 hover:border-yellow-500/50 transition-colors"
                    >
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <Bot className="h-8 w-8 text-yellow-500" />
                          <div className="flex items-center space-x-2">
                            {agent.is_template && (
                              <Badge className="bg-yellow-500 text-black">Template</Badge>
                            )}
                            {agent.is_public && (
                              <Badge className="bg-green-500 text-black">Public</Badge>
                            )}
                          </div>
                        </div>
                        <CardTitle className="text-lg">{agent.name}</CardTitle>
                        <CardDescription className="text-gray-400 line-clamp-2">
                          {agent.backstory}
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-400">Role: {agent.role}</span>
                            <div className="flex items-center space-x-1">
                              <Star className="h-3 w-3 fill-current text-yellow-500" />
                              <span>{(agent.average_rating || 0).toFixed(1)}</span>
                            </div>
                          </div>
                          <div className="flex flex-wrap gap-1">
                            {agent.tags.slice(0, 3).map((tag) => (
                              <Badge key={tag} variant="outline" className="border-gray-600 text-gray-400 text-xs">
                                {tag}
                              </Badge>
                            ))}
                          </div>
                          <div className="flex items-center justify-between pt-2">
                            <div className="flex items-center text-sm text-gray-400">
                              <Download className="h-3 w-3 mr-1" />
                              {agent.clone_count.toLocaleString()} clones
                            </div>
                            <div className="flex space-x-2">
                              <Button 
                                size="sm" 
                                variant="ghost" 
                                onClick={() => toggleFavorite(agent.id)}
                                className={favorites.has(agent.id) ? "text-red-400 hover:text-red-300" : "text-gray-400 hover:text-white"}
                              >
                                <Heart className={`h-4 w-4 ${favorites.has(agent.id) ? 'fill-current' : ''}`} />
                              </Button>
                              <Button 
                                size="sm" 
                                onClick={() => cloneAgent(agent)}
                                className="bg-yellow-500 text-black hover:bg-yellow-400"
                              >
                                Clone
                              </Button>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </section>

            {/* More Agents */}
            {filteredAgents.length > 6 && (
              <section>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold flex items-center">
                    <TrendingUp className="h-6 w-6 mr-2 text-blue-400" />
                    More Agents
                  </h2>
                </div>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {filteredAgents.slice(6).map((agent) => (
                    <Card key={agent.id} className="bg-black border-gray-700 hover:border-gray-600 transition-colors">
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <Bot className="h-8 w-8 text-blue-400" />
                          <Badge variant="outline" className="border-blue-400/30 text-blue-400">
                            {agent.category}
                          </Badge>
                        </div>
                        <CardTitle className="text-lg">{agent.name}</CardTitle>
                        <CardDescription className="text-gray-400 line-clamp-2">
                          {agent.backstory}
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-400">Role: {agent.role}</span>
                            <div className="flex items-center space-x-1">
                              <Star className="h-3 w-3 fill-current text-yellow-500" />
                              <span>{(agent.average_rating || 0).toFixed(1)}</span>
                            </div>
                          </div>
                          <div className="flex flex-wrap gap-1">
                            {agent.tags.slice(0, 3).map((tag) => (
                              <Badge key={tag} variant="outline" className="border-gray-600 text-gray-400 text-xs">
                                {tag}
                              </Badge>
                            ))}
                          </div>
                          <div className="flex items-center justify-between pt-2">
                            <div className="flex items-center text-sm text-gray-400">
                              <Download className="h-3 w-3 mr-1" />
                              {agent.clone_count.toLocaleString()} clones
                            </div>
                            <div className="flex space-x-2">
                              <Button 
                                size="sm" 
                                variant="ghost" 
                                onClick={() => toggleFavorite(agent.id)}
                                className={favorites.has(agent.id) ? "text-red-400 hover:text-red-300" : "text-gray-400 hover:text-white"}
                              >
                                <Heart className={`h-4 w-4 ${favorites.has(agent.id) ? 'fill-current' : ''}`} />
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => cloneAgent(agent)}
                                className="border-blue-400/30 text-blue-400 hover:bg-blue-400 hover:text-black bg-transparent"
                              >
                                Clone
                              </Button>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </section>
            )}
          </TabsContent>

          <TabsContent value="scenarios" className="space-y-8">
            <section>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold flex items-center">
                  <TrendingUp className="h-6 w-6 mr-2 text-green-400" />
                  Popular Scenarios
                </h2>
              </div>
              
              {filteredScenarios.length === 0 ? (
                <div className="text-center py-12 text-gray-400">
                  <Bot className="h-16 w-16 mx-auto mb-4 opacity-50" />
                  <p className="text-xl mb-2">No scenarios found</p>
                  <p>Try adjusting your search or filter criteria</p>
                </div>
              ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {filteredScenarios.map((scenario) => (
                    <Card key={scenario.id} className="bg-black border-gray-700 hover:border-gray-600 transition-colors">
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <div className="w-8 h-8 bg-green-400/20 rounded-lg flex items-center justify-center">
                            <Bot className="h-5 w-5 text-green-400" />
                          </div>
                          <div className="flex items-center space-x-2">
                            <Badge variant="outline" className="border-green-400/30 text-green-400">
                              {scenario.industry}
                            </Badge>
                            {scenario.is_template && (
                              <Badge className="bg-green-500 text-black">Template</Badge>
                            )}
                          </div>
                        </div>
                        <CardTitle className="text-lg">{scenario.title}</CardTitle>
                        <CardDescription className="text-gray-400 line-clamp-2">
                          {scenario.description}
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-400">Challenge: {scenario.challenge}</span>
                          </div>
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-400">Objectives: {scenario.learning_objectives.length}</span>
                            <span className="text-gray-400">
                              Created: {new Date(scenario.created_at).toLocaleDateString()}
                            </span>
                          </div>
                          <div className="flex items-center justify-between pt-2">
                            <div className="flex items-center text-sm text-gray-400">
                              <Download className="h-3 w-3 mr-1" />
                              {scenario.clone_count.toLocaleString()} uses
                            </div>
                            <div className="flex space-x-2">
                              <Button 
                                size="sm" 
                                variant="ghost" 
                                onClick={() => toggleFavorite(scenario.id)}
                                className={favorites.has(scenario.id) ? "text-red-400 hover:text-red-300" : "text-gray-400 hover:text-white"}
                              >
                                <Heart className={`h-4 w-4 ${favorites.has(scenario.id) ? 'fill-current' : ''}`} />
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => router.push(`/simulation?scenario=${scenario.id}`)}
                                className="border-green-400/30 text-green-400 hover:bg-green-400 hover:text-black bg-transparent"
                              >
                                Use
                              </Button>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </section>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
