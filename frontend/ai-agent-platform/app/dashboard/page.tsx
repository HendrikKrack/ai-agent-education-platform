"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Bot, Plus, Play, Users, FileText, Star, TrendingUp, Clock, Zap, LogOut } from "lucide-react"
import { useAuth } from "@/lib/auth-context"
import { apiClient, Agent, Scenario } from "@/lib/api"

export default function Dashboard() {
  const router = useRouter()
  const { user, logout, isLoading: authLoading } = useAuth()
  
  const [agents, setAgents] = useState<Agent[]>([])
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login")
      return
    }

    if (user) {
      loadDashboardData()
    }
  }, [user, authLoading, router])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      
      // Load user's agents and recent scenarios in parallel
      const [userAgents, allScenarios] = await Promise.all([
        apiClient.getUserAgents(user!.id),
        apiClient.getScenarios()
      ])
      
      setAgents(userAgents.slice(0, 3)) // Show only recent 3 agents
      setScenarios(allScenarios.slice(0, 3)) // Show only recent 3 scenarios
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load dashboard data")
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    logout()
    router.push("/")
  }

  // Debug logging
  console.log('Dashboard state:', { authLoading, loading, user, error })

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <Bot className="h-12 w-12 text-yellow-500 mx-auto mb-4 animate-spin" />
          <p>Loading your dashboard...</p>
          <p className="text-sm text-gray-400 mt-2">
            Auth: {authLoading ? 'Loading' : 'Ready'} | Data: {loading ? 'Loading' : 'Ready'}
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-400 mb-4">{error}</p>
          <Button onClick={loadDashboardData} className="bg-yellow-500 text-black hover:bg-yellow-400">
            Try Again
          </Button>
        </div>
      </div>
    )
  }

  if (!user) return null

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="border-b border-yellow-500/20 bg-black/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Bot className="h-8 w-8 text-yellow-500" />
            <span className="text-2xl font-bold">AgentCraft</span>
          </div>
          <nav className="hidden md:flex items-center space-x-6">
            <Link href="/dashboard" className="text-yellow-500">
              Dashboard
            </Link>
            <Link href="/marketplace" className="hover:text-yellow-500 transition-colors">
              Marketplace
            </Link>
            <Link href="/agent-builder" className="hover:text-yellow-500 transition-colors">
              Build Agent
            </Link>
            <Link href="/scenario-builder" className="hover:text-yellow-500 transition-colors">
              Create Scenario
            </Link>
          </nav>
          <div className="flex items-center space-x-4">
            <span className="hidden md:block text-sm text-gray-400">
              Welcome, {user.full_name || user.username}
            </span>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">
            Welcome back, <span className="text-yellow-500">{user.full_name || user.username}</span>
          </h1>
          <p className="text-gray-400 text-lg">Ready to build something amazing today?</p>
        </div>

        {/* Quick Actions */}
        <div className="grid md:grid-cols-4 gap-4 mb-8">
          <Card className="bg-gradient-to-br from-yellow-500/20 to-yellow-600/10 border-yellow-500/30 hover:border-yellow-500/50 transition-colors cursor-pointer">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <Bot className="h-8 w-8 text-yellow-500" />
                <Plus className="h-5 w-5 text-yellow-500" />
              </div>
            </CardHeader>
            <CardContent>
              <Link href="/agent-builder">
                <h3 className="font-semibold text-lg mb-1">Build Agent</h3>
                <p className="text-sm text-gray-400">Create a new AI agent</p>
              </Link>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-blue-500/20 to-blue-600/10 border-blue-500/30 hover:border-blue-500/50 transition-colors cursor-pointer">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <Users className="h-8 w-8 text-blue-400" />
                <Plus className="h-5 w-5 text-blue-400" />
              </div>
            </CardHeader>
            <CardContent>
              <Link href="/marketplace">
                <h3 className="font-semibold text-lg mb-1">Browse Marketplace</h3>
                <p className="text-sm text-gray-400">Discover community agents</p>
              </Link>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-500/20 to-green-600/10 border-green-500/30 hover:border-green-500/50 transition-colors cursor-pointer">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <FileText className="h-8 w-8 text-green-400" />
                <Plus className="h-5 w-5 text-green-400" />
              </div>
            </CardHeader>
            <CardContent>
              <Link href="/scenario-builder">
                <h3 className="font-semibold text-lg mb-1">Create Scenario</h3>
                <p className="text-sm text-gray-400">Build test scenarios</p>
              </Link>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-500/20 to-purple-600/10 border-purple-500/30 hover:border-purple-500/50 transition-colors cursor-pointer">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <Play className="h-8 w-8 text-purple-400" />
                <Zap className="h-5 w-5 text-purple-400" />
              </div>
            </CardHeader>
            <CardContent>
              <Link href="/simulation">
                <h3 className="font-semibold text-lg mb-1">Run Simulation</h3>
                <p className="text-sm text-gray-400">Test your agents</p>
              </Link>
            </CardContent>
          </Card>
        </div>

        {/* Stats Cards */}
        <div className="grid md:grid-cols-4 gap-4 mb-8">
          <Card className="bg-black border-yellow-500/20">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-400">Total Agents</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-500">{user.public_agents_count}</div>
              <p className="text-xs text-gray-400 flex items-center mt-1">
                <TrendingUp className="h-3 w-3 mr-1" />
                Public agents
              </p>
            </CardContent>
          </Card>

          <Card className="bg-black border-yellow-500/20">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-400">Downloads</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-400">{user.total_downloads}</div>
              <p className="text-xs text-gray-400 flex items-center mt-1">
                <TrendingUp className="h-3 w-3 mr-1" />
                Community downloads
              </p>
            </CardContent>
          </Card>

          <Card className="bg-black border-yellow-500/20">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-400">Reputation</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-400">{user.reputation_score.toFixed(1)}</div>
              <p className="text-xs text-gray-400 flex items-center mt-1">
                <Star className="h-3 w-3 mr-1 fill-current" />
                Community rating
              </p>
            </CardContent>
          </Card>

          <Card className="bg-black border-yellow-500/20">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-400">Member Since</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-400">
                {new Date(user.created_at).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
              </div>
              <p className="text-xs text-gray-400 flex items-center mt-1">
                <Clock className="h-3 w-3 mr-1" />
                {user.is_verified ? 'Verified' : 'Unverified'}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity */}
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Recent Agents */}
          <Card className="bg-black border-yellow-500/20">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Your Recent Agents</span>
                <Button variant="ghost" size="sm" asChild>
                  <Link href="/agent-builder">Create New</Link>
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {agents.length === 0 ? (
                  <div className="text-center py-8 text-gray-400">
                    <Bot className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No agents created yet</p>
                    <Link href="/agent-builder">
                      <Button className="mt-2 bg-yellow-500 text-black hover:bg-yellow-400">
                        Create Your First Agent
                      </Button>
                    </Link>
                  </div>
                ) : (
                  agents.map((agent) => (
                    <div
                      key={agent.id}
                      className="flex items-center justify-between p-3 rounded-lg bg-gray-900/50 hover:bg-gray-900/70 transition-colors"
                    >
                      <div className="flex items-center space-x-3">
                        <Bot className="h-8 w-8 text-yellow-500" />
                        <div>
                          <h4 className="font-medium">{agent.name}</h4>
                          <p className="text-sm text-gray-400">{agent.category}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge
                          variant={agent.is_public ? "default" : "secondary"}
                          className="bg-yellow-500/20 text-yellow-500"
                        >
                          {agent.is_public ? "Public" : "Private"}
                        </Badge>
                        <div className="flex items-center text-sm text-gray-400">
                          <Star className="h-3 w-3 mr-1 fill-current text-yellow-500" />
                          {agent.average_rating?.toFixed(1) || 'N/A'}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>

          {/* Recent Scenarios */}
          <Card className="bg-black border-yellow-500/20">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Available Scenarios</span>
                <Button variant="ghost" size="sm" asChild>
                  <Link href="/scenario-builder">Create New</Link>
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {scenarios.length === 0 ? (
                  <div className="text-center py-8 text-gray-400">
                    <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No scenarios available</p>
                    <Link href="/scenario-builder">
                      <Button className="mt-2 bg-green-500 text-black hover:bg-green-400">
                        Create Your First Scenario
                      </Button>
                    </Link>
                  </div>
                ) : (
                  scenarios.map((scenario) => (
                    <div
                      key={scenario.id}
                      className="flex items-center justify-between p-3 rounded-lg bg-gray-900/50 hover:bg-gray-900/70 transition-colors"
                    >
                      <div className="flex items-center space-x-3">
                        <FileText className="h-8 w-8 text-blue-400" />
                        <div>
                          <h4 className="font-medium">{scenario.title}</h4>
                          <p className="text-sm text-gray-400">{scenario.industry}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline" className="border-blue-400/30 text-blue-400">
                          {scenario.source_type}
                        </Badge>
                        <Link href="/simulation">
                          <Button size="sm" variant="ghost" className="text-yellow-500 hover:text-yellow-400">
                            <Play className="h-4 w-4" />
                          </Button>
                        </Link>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
