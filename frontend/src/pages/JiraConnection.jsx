import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useToast } from "@/hooks/use-toast";
import { jiraService } from "@/services/jira";

export default function JiraConnection() {
  const [isLoading, setIsLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState("idle");
  const [formData, setFormData] = useState({
    domain: "",
    email: "",
    apiToken: "",
  });
  const [error, setError] = useState("");

  const navigate = useNavigate();
  const { toast } = useToast();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setConnectionStatus("idle");
    setError("");

    try {
      const credentials = {
        domain: formData.domain,
        email: formData.email,
        api_token: formData.apiToken,
      };

      const response = await jiraService.connectJira(credentials);

      if (response.success) {
        setConnectionStatus("success");
        toast({
          title: "Connection Successful",
          description: "Successfully connected to Jira. Redirecting to dashboard...",
        });

        // Redirect to dashboard after successful connection
        setTimeout(() => {
          navigate("/dashboard", { replace: true });
        }, 2000);
      } else {
        setConnectionStatus("error");
        setError(response.error);
        toast({
          title: "Connection Failed",
          description: response.error || "Unable to connect to Jira. Please check your credentials.",
          variant: "destructive",
        });
      }
    } catch (error) {
      setConnectionStatus("error");
      setError(error.message);
      toast({
        title: "Connection Failed",
        description: "An unexpected error occurred. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div className="p-6 max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate("/integrations")}
          className="flex items-center space-x-2"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Integrations</span>
        </Button>
      </div>

      {/* Connection Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-dashboard-primary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">J</span>
            </div>
            <span>Connect to Jira</span>
          </CardTitle>
          <CardDescription>
            Enter your Jira credentials to connect your instance with Multi Desk
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {connectionStatus === "success" && (
            <Alert className="border-dashboard-success bg-dashboard-success/10">
              <CheckCircle className="h-4 w-4 text-dashboard-success" />
              <AlertDescription className="text-dashboard-success">
                Successfully connected to Jira! Redirecting to dashboard...
              </AlertDescription>
            </Alert>
          )}

          {connectionStatus === "error" && (
            <Alert className="border-dashboard-danger bg-dashboard-danger/10">
              <AlertCircle className="h-4 w-4 text-dashboard-danger" />
              <AlertDescription className="text-dashboard-danger">
                {error || "Connection failed. Please verify your credentials and try again."}
              </AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="domain">Jira Domain</Label>
              <Input
                id="domain"
                placeholder="https://company.atlassian.net"
                value={formData.domain}
                onChange={(e) => handleInputChange("domain", e.target.value)}
                disabled={isLoading}
                required
              />
              <p className="text-xs text-muted-foreground">
                Your Jira instance URL (including https://)
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Email / Username</Label>
              <Input
                id="email"
                type="email"
                placeholder="your-email@company.com"
                value={formData.email}
                onChange={(e) => handleInputChange("email", e.target.value)}
                disabled={isLoading}
                required
              />
              <p className="text-xs text-muted-foreground">
                The email address associated with your Jira account
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="apiToken">API Token</Label>
              <Input
                id="apiToken"
                type="password"
                placeholder="Enter your Jira API token"
                value={formData.apiToken}
                onChange={(e) => handleInputChange("apiToken", e.target.value)}
                disabled={isLoading}
                required
              />
              <p className="text-xs text-muted-foreground">
                Generate an API token from your Jira account settings
              </p>
            </div>

            <div className="flex space-x-3 pt-4">
              <Button
                type="submit"
                disabled={isLoading || connectionStatus === "success"}
                className="bg-dashboard-primary hover:bg-dashboard-primary/90"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Connecting...
                  </>
                ) : (
                  "Connect"
                )}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate("/integrations")}
                disabled={isLoading}
              >
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Help Section */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Need Help?</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground space-y-2">
          <p>
            <strong>How to get your Jira API Token:</strong>
          </p>
          <ol className="list-decimal list-inside space-y-1 ml-2">
            <li>Go to your Atlassian Account Settings</li>
            <li>Navigate to Security → API Tokens</li>
            <li>Click "Create API Token"</li>
            <li>Copy the generated token and paste it above</li>
          </ol>
        </CardContent>
      </Card>
    </div>
  );
}