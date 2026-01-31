import { useState, useEffect } from "react";
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle 
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { AlertCircle, ExternalLink, Settings, CheckCircle } from "lucide-react";
import { jiraService } from "@/services/jira";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";

export function PostLoginJiraSetup({ open, onOpenChange, onSetupComplete }) {
  const [checking, setChecking] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [setupStep, setSetupStep] = useState('check'); // 'check', 'connect', 'complete'
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
      const connected = response.success && response.data?.connected;
      setIsConnected(connected);
      
      if (connected) {
        setSetupStep('complete');
        setTimeout(() => {
          onSetupComplete?.();
          onOpenChange(false);
        }, 2000);
      } else {
        setSetupStep('connect');
      }
    } catch (error) {
      setIsConnected(false);
      setSetupStep('connect');
    } finally {
      setChecking(false);
    }
  };

  const handleConnect = () => {
    navigate("/jira-connection");
    onOpenChange(false);
  };

  const handleSkip = () => {
    onSetupComplete?.();
    onOpenChange(false);
  };

  const renderContent = () => {
    if (checking) {
      return (
        <div className="flex flex-col items-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"></div>
          <p className="text-lg font-medium">Checking JIRA connection...</p>
          <p className="text-sm text-muted-foreground mt-2">
            Please wait while we verify your JIRA integration status
          </p>
        </div>
      );
    }

    if (setupStep === 'complete') {
      return (
        <div className="flex flex-col items-center py-8">
          <div className="w-16 h-16 bg-dashboard-success/10 rounded-full flex items-center justify-center mb-4">
            <CheckCircle className="w-8 h-8 text-dashboard-success" />
          </div>
          <h3 className="text-xl font-bold text-dashboard-success mb-2">JIRA Already Connected!</h3>
          <p className="text-center text-muted-foreground">
            Your JIRA account is already integrated. You're all set to use all features!
          </p>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        <div className="text-center">
          <div className="w-16 h-16 bg-dashboard-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <Settings className="w-8 h-8 text-dashboard-primary" />
          </div>
          <h3 className="text-xl font-bold mb-2">Welcome to Multi Desk!</h3>
          <p className="text-muted-foreground">
            Let's set up your JIRA integration to unlock full functionality
          </p>
        </div>

        <div className="bg-muted/50 rounded-lg p-4">
          <h4 className="font-medium mb-3 flex items-center">
            <AlertCircle className="w-4 h-4 mr-2 text-dashboard-warning" />
            Why JIRA Integration is Important
          </h4>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li className="flex items-start">
              <span className="text-dashboard-success mr-2">✓</span>
              <span>Connect employee leave data with JIRA tasks</span>
            </li>
            <li className="flex items-start">
              <span className="text-dashboard-success mr-2">✓</span>
              <span>Automatically detect project conflicts and risks</span>
            </li>
            <li className="flex items-start">
              <span className="text-dashboard-success mr-2">✓</span>
              <span>Get real-time alerts for resource allocation issues</span>
            </li>
            <li className="flex items-start">
              <span className="text-dashboard-success mr-2">✓</span>
              <span>Generate comprehensive risk analysis reports</span>
            </li>
          </ul>
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start">
            <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" />
            <div>
              <h4 className="font-medium text-yellow-800 mb-1">Limited Functionality</h4>
              <p className="text-sm text-yellow-700">
                Without JIRA integration, you won't be able to upload files or perform risk analysis. 
                Some dashboard features will be restricted.
              </p>
            </div>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-3 pt-2">
          <Button 
            onClick={handleConnect}
            className="flex-1 bg-dashboard-primary hover:bg-dashboard-primary/90"
          >
            <Settings className="w-4 h-4 mr-2" />
            Connect JIRA Now
          </Button>
          <Button 
            variant="outline" 
            onClick={handleSkip}
          >
            Skip for Now
          </Button>
        </div>
      </div>
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle className="sr-only">JIRA Setup Required</DialogTitle>
        </DialogHeader>
        {renderContent()}
      </DialogContent>
    </Dialog>
  );
}