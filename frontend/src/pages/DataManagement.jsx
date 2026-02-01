import { useState, useEffect } from "react";
import { Upload, FileText, Calendar, Download, Trash2, Eye, Users, BarChart3, AlertCircle, CheckCircle, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { DataPreviewDialog } from "@/components/data/DataPreviewDialog";
import { FileUploadZone } from "@/components/data/FileUploadZone";
import { JiraConnectionModal } from "@/components/data/JiraConnectionModal";
import { filesService } from "@/services/files";
import { jiraService } from "@/services/jira";

const supportedFormats = [
  { name: "Excel Files", extension: ".xlsx", description: "Microsoft Excel Workbook" },
  { name: "CSV Files", extension: ".csv", description: "Comma Separated Values" },
];

export default function DataManagement() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleteDialog, setDeleteDialog] = useState(null);
  const [previewDialog, setPreviewDialog] = useState(null);
  const [totalFiles, setTotalFiles] = useState(0);
  const [totalRecords, setTotalRecords] = useState(0);
  const [processingCount, setProcessingCount] = useState(0);
  const [showJiraModal, setShowJiraModal] = useState(false);
  const [pendingFile, setPendingFile] = useState(null);
  const { toast } = useToast();

  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await filesService.getFiles({}, 1, 50);
      
      if (response.success) {
        setFiles(response.data.files);
        setTotalFiles(response.data.total);
        
        // Calculate total records and processing count
        const records = response.data.files.reduce((sum, file) => sum + (file.records || 0), 0);
        setTotalRecords(records);
        
        const processing = response.data.files.filter(file => file.status === 'processing').length;
        setProcessingCount(processing);
      } else {
        setError(response.error);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file) => {
    // Check JIRA connection first
    const jiraCheck = await jiraService.checkJiraConnection();
    
    if (!jiraCheck.success || !jiraCheck.data?.connected) {
      // Show modal and store the file for later upload
      setPendingFile(file);
      setShowJiraModal(true);
      return;
    }
    
    // Proceed with upload if JIRA is connected
    await uploadFileDirectly(file);
  };

  const uploadFileDirectly = async (file) => {
    try {
      const response = await filesService.uploadFile(file);

      if (!response || response.error) {
        throw new Error(response?.error || "Upload failed");
      }

      toast({
        title: "File Uploaded",
        description: "Your file has been uploaded successfully. Risk analysis will begin shortly.",
      });

      fetchFiles(); // refresh list after success
    } catch (error) {
      toast({
        title: "Upload Failed",
        description: error.message,
        variant: "destructive",
      });
    }
  };

  const handleJiraConnectSuccess = () => {
    if (pendingFile) {
      uploadFileDirectly(pendingFile);
      setPendingFile(null);
    }
  };



  const getStatusBadge = (status) => {
    switch (status) {
      case 'success':
      case 'processed':
      case 'completed':
        return <Badge className="bg-dashboard-success text-white"><CheckCircle className="w-3 h-3 mr-1" />Completed</Badge>;
      case 'processing':
        return <Badge className="bg-dashboard-warning text-white"><BarChart3 className="w-3 h-3 mr-1" />Processing</Badge>;
      case 'error':
        return <Badge className="bg-dashboard-danger text-white"><AlertCircle className="w-3 h-3 mr-1" />Error</Badge>;
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  const handlePreview = async (file) => {
    try {
      const response = await filesService.getFileById(file.id);
      if (response.success) {
        setPreviewDialog(response.data);
      } else {
        toast({
          title: "Preview Failed",
          description: "Failed to load file preview.",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Preview Failed",
        description: "An unexpected error occurred.",
        variant: "destructive",
      });
    }
  };

  const handleDelete = (file) => {
    setDeleteDialog(file);
  };

  const confirmDelete = async () => {
    try {
      const response = await filesService.deleteFile(deleteDialog.id);
      
      if (response.success) {
        toast({
          title: "File Deleted",
          description: `${deleteDialog.name} has been deleted successfully.`,
        });
        
        // Refresh file list
        fetchFiles();
      } else {
        toast({
          title: "Delete Failed",
          description: response.error || "Failed to delete file.",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Delete Failed",
        description: "An unexpected error occurred.",
        variant: "destructive",
      });
    }
    
    setDeleteDialog(null);
  };

  const handleDownload = async (file) => {
    try {
      // In a real implementation, you would download the file
      // For now, we'll just show a toast
      toast({
        title: "Download Started",
        description: `Downloading ${file.name}...`,
      });
    } catch (error) {
      toast({
        title: "Download Failed",
        description: "Failed to download file.",
        variant: "destructive",
      });
    }
  };

  if (loading && files.length === 0) {
    return (
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Data Management</h1>
          <p className="text-muted-foreground">Upload, manage, and process employee data and project files</p>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Data Management</h1>
          <p className="text-muted-foreground">Upload, manage, and process employee data and project files</p>
        </div>
        <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-6 text-center">
          <h2 className="text-xl font-semibold text-destructive">Error Loading Files</h2>
          <p className="mt-2 text-destructive/80">{error}</p>
          <button 
            onClick={fetchFiles}
            className="mt-4 px-4 py-2 bg-destructive text-destructive-foreground rounded-md hover:opacity-90"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">Data Management</h1>
        <p className="text-muted-foreground">Upload, manage, and process employee data and project files</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload Section */}
        <div className="lg:col-span-2 space-y-6">
          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <FileText className="w-5 h-5 text-dashboard-primary" />
                  <div>
                    <p className="text-sm font-medium">Total Files</p>
                    <p className="text-2xl font-bold">{totalFiles}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <Users className="w-5 h-5 text-dashboard-success" />
                  <div>
                    <p className="text-sm font-medium">Total Records</p>
                    <p className="text-2xl font-bold">{totalRecords}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <BarChart3 className="w-5 h-5 text-dashboard-info" />
                  <div>
                    <p className="text-sm font-medium">Processing</p>
                    <p className="text-2xl font-bold">{processingCount}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Upload Area */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Upload className="w-5 h-5" />
                <span>Upload Data Files</span>
              </CardTitle>
              <CardDescription>
                Securely upload Excel files containing employee records, task data, and project information.
                JIRA connection is required for risk analysis.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <FileUploadZone 
                onFileUpload={handleFileUpload}
                accept=".xlsx,.xls,.csv"
                maxSize={10 * 1024 * 1024}
              />
              <p className="text-sm text-muted-foreground mt-2">
                Note: JIRA connection is required for risk analysis of uploaded files.
              </p>
            </CardContent>
          </Card>

          {/* Recent Files */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Uploads</CardTitle>
              <CardDescription>Manage your uploaded data files</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {files.map((file) => (
                  <div
                    key={file.id}
                    className="flex items-center space-x-4 p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                  >
                    <FileText className="w-8 h-8 text-dashboard-primary flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <p className="text-sm font-medium text-foreground truncate">
                          {file.filename}
                        </p>
                        {getStatusBadge(file.status)}
                      </div>
                      <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                        <span>{file.records || 0} records</span>
                        <span>{(file.size / 1024 / 1024).toFixed(1)} MB</span>
                        <span>by {file.uploader}</span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                      <Calendar className="w-3 h-3" />
                      <span>{new Date(file.uploaded_at).toLocaleDateString()}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      {/* <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => handlePreview(file)}
                      >
                        <Eye className="w-4 h-4" />
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => handleDownload(file)}
                      >
                        <Download className="w-4 h-4" />
                      </Button> */}
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => handleDelete(file)}
                        className="text-dashboard-danger hover:text-dashboard-danger"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
              
              {files.length === 0 && !loading && (
                <div className="text-center py-8 text-muted-foreground">
                  No files uploaded yet. Upload your first file to get started.
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Sidebar Information */}
        <div className="space-y-6">
          {/* File Format Guide */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Supported Formats</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {supportedFormats.map((format, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <FileText className="w-5 h-5 text-dashboard-info mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">{format.name}</p>
                    <p className="text-xs text-muted-foreground">{format.extension}</p>
                    <p className="text-xs text-muted-foreground">{format.description}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Upload Guidelines */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Upload Guidelines</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="space-y-2">
                <h4 className="text-sm font-medium">File Requirements:</h4>
                <ul className="text-xs text-muted-foreground space-y-1">
                  <li>• Maximum file size: 10MB</li>
                  <li>• Supported formats: .xlsx, .xls, .csv</li>
                  <li>• Headers should be in the first row</li>
                  <li>• No empty rows between data</li>
                </ul>
              </div>
              <Separator />
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Data Types:</h4>
                <ul className="text-xs text-muted-foreground space-y-1">
                  <li>• Employee records</li>
                  <li>• Task and project data</li>
                  <li>• Leave and attendance records</li>
                  <li>• Performance metrics</li>
                </ul>
              </div>
            </CardContent>
          </Card>

          {/* Processing Status */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Processing Queue</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span>Files in queue</span>
                  <Badge variant="outline">{processingCount}</Badge>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span>Estimated time</span>
                  <span className="text-muted-foreground">~{processingCount * 2} minutes</span>
                </div>
                <Progress value={processingCount > 0 ? 65 : 0} className="w-full" />
                {processingCount > 0 && (
                  <p className="text-xs text-muted-foreground">
                    Processing files...
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Preview Dialog */}
      <DataPreviewDialog 
        open={!!previewDialog} 
        onClose={() => setPreviewDialog(null)} 
        file={previewDialog} 
      />

      {/* JIRA Connection Modal */}
      <JiraConnectionModal 
        open={showJiraModal} 
        onOpenChange={setShowJiraModal}
        onConnectSuccess={handleJiraConnectSuccess}
      />

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={!!deleteDialog} onOpenChange={() => setDeleteDialog(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete File</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{deleteDialog?.filename}"? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction 
              onClick={confirmDelete}
              className="bg-dashboard-danger hover:bg-dashboard-danger/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}