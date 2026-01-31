import { useState, useEffect } from "react";
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle 
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { AlertCircle, ExternalLink, Settings } from "lucide-react";
import { jiraService } from "@/services/jira";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";

export function JiraConnectionModal({ open, onOpenChange, onConnectSuccess }) {
  const [checking, setChecking] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    if (open) {
      checkConnection();
    }
  }, [open]);

  const checkConnection = async () => {
    setChecking(true);
    try {
      const response = await jiraService.checkJiraConnection();
      setIsConnected(response.success && response.data?.connected);
    } catch (error) {
      setIsConnected(false);
    } finally {
      setChecking(false);
    }
  };

  const handleConnect = () => {
    navigate("/jira-connection");
    onOpenChange(false);
  };

  const handleRefresh = () => {
    checkConnection();
    if (isConnected) {
      toast({
        title: "JIRA Connected",
        description: "You can now upload files for risk analysis.",
      });
      onConnectSuccess?.();
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-dashboard-warning" />
            JIRA Connection Required
          </DialogTitle>
          <DialogDescription className="space-y-4">
            <p>
              To analyze risks and conflicts between employee leave data and JIRA tasks, 
              you need to connect your JIRA account first.
            </p>
            
            {checking ? (
              <div className="flex items-center justify-center py-4">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                <span className="ml-2">Checking connection...</span>
              </div>
            ) : isConnected ? (
              <div className="bg-dashboard-success/10 border border-dashboard-success/20 rounded-lg p-4">
                <p className="text-dashboard-success font-medium">✓ JIRA is connected!</p>
                <p className="text-sm text-muted-foreground mt-1">
                  You can now upload files for risk analysis.
                </p>
              </div>
            ) : (
              <div className="bg-dashboard-warning/10 border border-dashboard-warning/20 rounded-lg p-4">
                <p className="text-dashboard-warning font-medium">⚠ JIRA not connected</p>
                <p className="text-sm text-muted-foreground mt-1">
                  Please connect your JIRA account to enable risk analysis features.
                </p>
              </div>
            )}
            
            <div className="text-sm text-muted-foreground">
              <p className="font-medium mb-2">Why JIRA connection is needed:</p>
              <ul className="space-y-1 ml-4 list-disc">
                <li>Compare employee leave dates with assigned JIRA tasks</li>
                <li>Identify potential project delays and resource conflicts</li>
                <li>Generate risk alerts for overlapping assignments</li>
              </ul>
            </div>
          </DialogDescription>
        </DialogHeader>
        
        <div className="flex flex-col sm:flex-row gap-3 mt-4">
          {!isConnected ? (
            <>
              <Button 
                onClick={handleConnect}
                className="flex-1 bg-dashboard-primary hover:bg-dashboard-primary/90"
              >
                <Settings className="w-4 h-4 mr-2" />
                Connect JIRA
              </Button>
              <Button 
                variant="outline" 
                onClick={() => onOpenChange(false)}
              >
                Cancel
              </Button>
            </>
          ) : (
            <>
              <Button 
                onClick={handleRefresh}
                variant="outline"
              >
                Refresh Status
              </Button>
              <Button 
                onClick={() => onOpenChange(false)}
                className="bg-dashboard-success hover:bg-dashboard-success/90"
              >
                Continue to Upload
              </Button>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}