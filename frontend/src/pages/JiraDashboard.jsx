import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { jiraService } from "@/services/jira";
import { useToast } from "@/hooks/use-toast";

export default function JiraDashboard() {
  const [projectKey, setProjectKey] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [issues, setIssues] = useState({
    all: [],
    epics: [],
    stories: [],
    tasks: [],
    bugs: []
  });
  const [connectionStatus, setConnectionStatus] = useState(null);
  
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    // Check connection status on component mount
    checkConnection();
  }, []);

  const checkConnection = async () => {
    try {
      const response = await jiraService.getConnectionStatus();
      if (response.success) {
        setConnectionStatus(response.data);
      } else {
        setConnectionStatus({ connected: false });
        toast({
          title: "Connection Error",
          description: "Jira connection is not valid. Please check your credentials.",
          variant: "destructive",
        });
      }
    } catch (error) {
      setConnectionStatus({ connected: false });
      toast({
        title: "Connection Error",
        description: "Failed to check Jira connection.",
        variant: "destructive",
      });
    }
  };

  const fetchAllIssues = async () => {
    if (!projectKey) {
      toast({
        title: "Project Key Required",
        description: "Please enter a project key.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      const response = await jiraService.getAllIssues(projectKey);
      if (response.success) {
        setIssues(prev => ({ ...prev, all: response.data }));
        toast({
          title: "Success",
          description: `Fetched ${response.data.length} issues.`,
        });
      } else {
        toast({
          title: "Error",
          description: response.error,
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch issues.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const fetchEpics = async () => {
    if (!projectKey) {
      toast({
        title: "Project Key Required",
        description: "Please enter a project key.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      const response = await jiraService.getEpics(projectKey);
      if (response.success) {
        setIssues(prev => ({ ...prev, epics: response.data }));
        toast({
          title: "Success",
          description: `Fetched ${response.data.length} epics.`,
        });
      } else {
        toast({
          title: "Error",
          description: response.error,
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch epics.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const fetchStories = async () => {
    if (!projectKey) {
      toast({
        title: "Project Key Required",
        description: "Please enter a project key.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      const response = await jiraService.getStories(projectKey);
      if (response.success) {
        setIssues(prev => ({ ...prev, stories: response.data }));
        toast({
          title: "Success",
          description: `Fetched ${response.data.length} stories.`,
        });
      } else {
        toast({
          title: "Error",
          description: response.error,
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch stories.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const fetchTasks = async () => {
    if (!projectKey) {
      toast({
        title: "Project Key Required",
        description: "Please enter a project key.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      const response = await jiraService.getTasks(projectKey);
      if (response.success) {
        setIssues(prev => ({ ...prev, tasks: response.data }));
        toast({
          title: "Success",
          description: `Fetched ${response.data.length} tasks.`,
        });
      } else {
        toast({
          title: "Error",
          description: response.error,
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch tasks.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const fetchBugs = async () => {
    if (!projectKey) {
      toast({
        title: "Project Key Required",
        description: "Please enter a project key.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      const response = await jiraService.getBugs(projectKey);
      if (response.success) {
        setIssues(prev => ({ ...prev, bugs: response.data }));
        toast({
          title: "Success",
          description: `Fetched ${response.data.length} bugs.`,
        });
      } else {
        toast({
          title: "Error",
          description: response.error,
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch bugs.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const statusLower = status.toLowerCase();
    if (statusLower.includes("done") || statusLower.includes("closed")) return "bg-green-100 text-green-800";
    if (statusLower.includes("progress") || statusLower.includes("review")) return "bg-blue-100 text-blue-800";
    if (statusLower.includes("todo") || statusLower.includes("backlog")) return "bg-yellow-100 text-yellow-800";
    return "bg-gray-100 text-gray-800";
  };

  const getPriorityColor = (priority) => {
    const priorityLower = priority.toLowerCase();
    if (priorityLower.includes("highest") || priorityLower.includes("urgent")) return "bg-red-100 text-red-800";
    if (priorityLower.includes("high")) return "bg-orange-100 text-orange-800";
    if (priorityLower.includes("medium")) return "bg-yellow-100 text-yellow-800";
    if (priorityLower.includes("low")) return "bg-green-100 text-green-800";
    return "bg-gray-100 text-gray-800";
  };

  return (
    <div className="p-6 space-y-6 bg-background min-h-screen">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Jira Dashboard</h1>
          <p className="text-muted-foreground">Browse and manage your Jira issues</p>
        </div>
        {!connectionStatus?.connected && (
          <Button onClick={() => navigate("/jira-connection")}>Connect Jira</Button>
        )}
      </div>

      {connectionStatus?.connected ? (
        <Card>
          <CardHeader>
            <CardTitle>Project Issues</CardTitle>
            <CardDescription>Fetch issues from your Jira project</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-4">
              <div className="flex-1">
                <Label htmlFor="projectKey">Project Key</Label>
                <Input
                  id="projectKey"
                  placeholder="Enter project key (e.g., PROJ)"
                  value={projectKey}
                  onChange={(e) => setProjectKey(e.target.value)}
                  disabled={isLoading}
                />
              </div>
              <div className="flex items-end">
                <Button onClick={fetchAllIssues} disabled={isLoading || !projectKey}>
                  {isLoading ? "Fetching..." : "Fetch Issues"}
                </Button>
              </div>
            </div>
            
            <Separator />
            
            <Tabs defaultValue="all">
              <TabsList>
                <TabsTrigger value="all">All Issues ({issues.all.length})</TabsTrigger>
                <TabsTrigger value="epics">Epics ({issues.epics.length})</TabsTrigger>
                <TabsTrigger value="stories">Stories ({issues.stories.length})</TabsTrigger>
                <TabsTrigger value="tasks">Tasks ({issues.tasks.length})</TabsTrigger>
                <TabsTrigger value="bugs">Bugs ({issues.bugs.length})</TabsTrigger>
              </TabsList>
              
              <TabsContent value="all" className="space-y-4">
                <div className="grid gap-4">
                  {issues.all.map((issue, index) => (
                    <Card key={index} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-mono text-sm font-medium">{issue.key}</span>
                              <Badge variant="secondary">{issue.fields?.issuetype?.name || "Issue"}</Badge>
                            </div>
                            <h3 className="font-medium mt-1">{issue.fields?.summary || "No summary"}</h3>
                          </div>
                          <div className="flex flex-col items-end gap-2">
                            <Badge className={getStatusColor(issue.fields?.status?.name || "")}>
                              {issue.fields?.status?.name || "Unknown"}
                            </Badge>
                            <Badge className={getPriorityColor(issue.fields?.priority?.name || "")}>
                              {issue.fields?.priority?.name || "No priority"}
                            </Badge>
                          </div>
                        </div>
                        <div className="flex items-center gap-4 mt-3 text-sm text-muted-foreground">
                          <span>Assignee: {issue.fields?.assignee?.displayName || "Unassigned"}</span>
                          <span>Created: {issue.fields?.created ? new Date(issue.fields.created).toLocaleDateString() : "N/A"}</span>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                  {issues.all.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      <p>No issues found. Enter a project key and click "Fetch Issues".</p>
                    </div>
                  )}
                </div>
              </TabsContent>
              
              <TabsContent value="epics" className="space-y-4">
                <div className="flex gap-2">
                  <Button onClick={fetchEpics} disabled={isLoading} variant="outline" size="sm">
                    Refresh Epics
                  </Button>
                </div>
                <div className="grid gap-4">
                  {issues.epics.map((issue, index) => (
                    <Card key={index} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-mono text-sm font-medium">{issue.key}</span>
                              <Badge variant="secondary">{issue.fields?.issuetype?.name || "Epic"}</Badge>
                            </div>
                            <h3 className="font-medium mt-1">{issue.fields?.summary || "No summary"}</h3>
                          </div>
                          <div className="flex flex-col items-end gap-2">
                            <Badge className={getStatusColor(issue.fields?.status?.name || "")}>
                              {issue.fields?.status?.name || "Unknown"}
                            </Badge>
                          </div>
                        </div>
                        <div className="flex items-center gap-4 mt-3 text-sm text-muted-foreground">
                          <span>Assignee: {issue.fields?.assignee?.displayName || "Unassigned"}</span>
                          <span>Created: {issue.fields?.created ? new Date(issue.fields.created).toLocaleDateString() : "N/A"}</span>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                  {issues.epics.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      <p>No epics found. Click "Refresh Epics" to fetch data.</p>
                    </div>
                  )}
                </div>
              </TabsContent>
              
              <TabsContent value="stories" className="space-y-4">
                <div className="flex gap-2">
                  <Button onClick={fetchStories} disabled={isLoading} variant="outline" size="sm">
                    Refresh Stories
                  </Button>
                </div>
                <div className="grid gap-4">
                  {issues.stories.map((issue, index) => (
                    <Card key={index} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-mono text-sm font-medium">{issue.key}</span>
                              <Badge variant="secondary">{issue.fields?.issuetype?.name || "Story"}</Badge>
                            </div>
                            <h3 className="font-medium mt-1">{issue.fields?.summary || "No summary"}</h3>
                          </div>
                          <div className="flex flex-col items-end gap-2">
                            <Badge className={getStatusColor(issue.fields?.status?.name || "")}>
                              {issue.fields?.status?.name || "Unknown"}
                            </Badge>
                            <Badge className={getPriorityColor(issue.fields?.priority?.name || "")}>
                              {issue.fields?.priority?.name || "No priority"}
                            </Badge>
                          </div>
                        </div>
                        <div className="flex items-center gap-4 mt-3 text-sm text-muted-foreground">
                          <span>Assignee: {issue.fields?.assignee?.displayName || "Unassigned"}</span>
                          <span>Created: {issue.fields?.created ? new Date(issue.fields.created).toLocaleDateString() : "N/A"}</span>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                  {issues.stories.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      <p>No stories found. Click "Refresh Stories" to fetch data.</p>
                    </div>
                  )}
                </div>
              </TabsContent>
              
              <TabsContent value="tasks" className="space-y-4">
                <div className="flex gap-2">
                  <Button onClick={fetchTasks} disabled={isLoading} variant="outline" size="sm">
                    Refresh Tasks
                  </Button>
                </div>
                <div className="grid gap-4">
                  {issues.tasks.map((issue, index) => (
                    <Card key={index} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-mono text-sm font-medium">{issue.key}</span>
                              <Badge variant="secondary">{issue.fields?.issuetype?.name || "Task"}</Badge>
                            </div>
                            <h3 className="font-medium mt-1">{issue.fields?.summary || "No summary"}</h3>
                          </div>
                          <div className="flex flex-col items-end gap-2">
                            <Badge className={getStatusColor(issue.fields?.status?.name || "")}>
                              {issue.fields?.status?.name || "Unknown"}
                            </Badge>
                            <Badge className={getPriorityColor(issue.fields?.priority?.name || "")}>
                              {issue.fields?.priority?.name || "No priority"}
                            </Badge>
                          </div>
                        </div>
                        <div className="flex items-center gap-4 mt-3 text-sm text-muted-foreground">
                          <span>Assignee: {issue.fields?.assignee?.displayName || "Unassigned"}</span>
                          <span>Created: {issue.fields?.created ? new Date(issue.fields.created).toLocaleDateString() : "N/A"}</span>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                  {issues.tasks.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      <p>No tasks found. Click "Refresh Tasks" to fetch data.</p>
                    </div>
                  )}
                </div>
              </TabsContent>
              
              <TabsContent value="bugs" className="space-y-4">
                <div className="flex gap-2">
                  <Button onClick={fetchBugs} disabled={isLoading} variant="outline" size="sm">
                    Refresh Bugs
                  </Button>
                </div>
                <div className="grid gap-4">
                  {issues.bugs.map((issue, index) => (
                    <Card key={index} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-mono text-sm font-medium">{issue.key}</span>
                              <Badge variant="secondary">{issue.fields?.issuetype?.name || "Bug"}</Badge>
                            </div>
                            <h3 className="font-medium mt-1">{issue.fields?.summary || "No summary"}</h3>
                          </div>
                          <div className="flex flex-col items-end gap-2">
                            <Badge className={getStatusColor(issue.fields?.status?.name || "")}>
                              {issue.fields?.status?.name || "Unknown"}
                            </Badge>
                            <Badge className={getPriorityColor(issue.fields?.priority?.name || "")}>
                              {issue.fields?.priority?.name || "No priority"}
                            </Badge>
                          </div>
                        </div>
                        <div className="flex items-center gap-4 mt-3 text-sm text-muted-foreground">
                          <span>Assignee: {issue.fields?.assignee?.displayName || "Unassigned"}</span>
                          <span>Created: {issue.fields?.created ? new Date(issue.fields.created).toLocaleDateString() : "N/A"}</span>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                  {issues.bugs.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      <p>No bugs found. Click "Refresh Bugs" to fetch data.</p>
                    </div>
                  )}
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      ) : (
        <Card className="border-destructive">
          <CardHeader>
            <CardTitle className="text-destructive">Jira Connection Required</CardTitle>
            <CardDescription>
              Connect your Jira account to view and manage issues
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => navigate("/jira-connection")}>Connect to Jira</Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}