import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { jiraService } from "@/services/jira";
import { useToast } from "@/hooks/use-toast";
import { ExternalLink, LinkIcon, CheckCircle, XCircle, RefreshCw } from "lucide-react";

export default function Integrations() {
  const [jiraStatus, setJiraStatus] = useState({
    connected: false,
    domain: "",
    email: "",
    created_at: null,
    updated_at: null
  });
  const [isLoading, setIsLoading] = useState(false);
  
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    fetchJiraStatus();
  }, []);

  const fetchJiraStatus = async () => {
    setIsLoading(true);
    try {
      const response = await jiraService.getConnectionStatus();
      if (response.success) {
        setJiraStatus(response.data);
      } else {
        toast({
          title: "Error",
          description: "Failed to fetch Jira connection status.",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch Jira connection status.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleConnectJira = () => {
    navigate("/jira-connection");
  };

  const handleValidateConnection = async () => {
    setIsLoading(true);
    try {
      const response = await jiraService.validateConnection();
      if (response.success) {
        toast({
          title: "Connection Valid",
          description: response.data.message,
        });
        // Refresh status
        fetchJiraStatus();
      } else {
        toast({
          title: "Connection Invalid",
          description: response.error,
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to validate Jira connection.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSyncData = async () => {
    setIsLoading(true);
    try {
      const response = await jiraService.syncJiraData();
      if (response.success) {
        toast({
          title: "Sync Successful",
          description: response.data.message,
        });
      } else {
        toast({
          title: "Sync Failed",
          description: response.error,
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to sync Jira data.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6 bg-background min-h-screen">
      <div>
        <h1 className="text-2xl font-bold">Integrations</h1>
        <p className="text-muted-foreground">Connect and manage your third-party integrations</p>
      </div>

      {/* Jira Integration Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">J</span>
              </div>
              <div>
                <CardTitle>Jira</CardTitle>
                <CardDescription>Connect your Jira instance to sync tasks and projects</CardDescription>
              </div>
            </div>
            {jiraStatus.connected ? (
              <Badge className="bg-green-100 text-green-800 hover:bg-green-100">
                <CheckCircle className="w-3 h-3 mr-1" />
                Connected
              </Badge>
            ) : (
              <Badge variant="destructive">
                <XCircle className="w-3 h-3 mr-1" />
                Not Connected
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {jiraStatus.connected ? (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Domain</p>
                  <p className="font-medium">{jiraStatus.domain}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Email</p>
                  <p className="font-medium">{jiraStatus.email}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Connected On</p>
                  <p className="font-medium">
                    {jiraStatus.created_at ? new Date(jiraStatus.created_at).toLocaleString() : "N/A"}
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground">Last Updated</p>
                  <p className="font-medium">
                    {jiraStatus.updated_at ? new Date(jiraStatus.updated_at).toLocaleString() : "N/A"}
                  </p>
                </div>
              </div>
              
              <Separator />
              
              <div className="flex flex-wrap gap-2">
                <Button onClick={handleValidateConnection} variant="outline" disabled={isLoading}>
                  {isLoading ? (
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <RefreshCw className="w-4 h-4 mr-2" />
                  )}
                  Validate Connection
                </Button>
                <Button onClick={handleSyncData} variant="outline" disabled={isLoading}>
                  {isLoading ? (
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <RefreshCw className="w-4 h-4 mr-2" />
                  )}
                  Sync Data
                </Button>
                <Button 
                  onClick={handleConnectJira} 
                  variant="outline" 
                  disabled={isLoading}
                >
                  <LinkIcon className="w-4 h-4 mr-2" />
                  Reconnect
                </Button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-muted-foreground">
                Connect your Jira instance to sync tasks, projects, and other data with Multi Desk.
              </p>
              <Button onClick={handleConnectJira} disabled={isLoading}>
                <LinkIcon className="w-4 h-4 mr-2" />
                Connect to Jira
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Add more integration cards here as needed */}
    </div>
  );
}