import { useState, useEffect } from "react";
import { 
  FileText, 
  BarChart3, 
  TrendingUp, 
  Plus, 
  Search, 
  Filter, 
  Download, 
  Trash2, 
  Eye,
  Calendar,
  Users,
  Folder,
  Clock
} from "lucide-react";
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "@/components/ui/select";
import { 
  Button 
} from "@/components/ui/button";
import { 
  Input 
} from "@/components/ui/input";
import { 
  Badge 
} from "@/components/ui/badge";
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger 
} from "@/components/ui/dialog";
import { 
  Label 
} from "@/components/ui/label";
import { 
  useToast 
} from "@/hooks/use-toast";
import { 
  Bar, 
  BarChart, 
  Line, 
  LineChart, 
  Pie, 
  PieChart, 
  Cell, 
  ResponsiveContainer, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend 
} from "recharts";
import { reportsService } from "@/services/reports";

const reportTypes = [
  { 
    id: "task_summary", 
    name: "Task Summary", 
    description: "Overview of tasks by status, priority, and assignee",
    icon: FileText,
    color: "bg-blue-500"
  },
  { 
    id: "user_performance", 
    name: "User Performance", 
    description: "Team member performance and workload distribution",
    icon: Users,
    color: "bg-green-500"
  },
  { 
    id: "project_progress", 
    name: "Project Progress", 
    description: "Project completion rates and milestone tracking",
    icon: Folder,
    color: "bg-purple-500"
  },
  { 
    id: "time_tracking", 
    name: "Time Tracking", 
    description: "Time estimation vs actual work hours",
    icon: Clock,
    color: "bg-yellow-500"
  },
  { 
    id: "resource_utilization", 
    name: "Resource Utilization", 
    description: "Team capacity and resource allocation",
    icon: TrendingUp,
    color: "bg-red-500"
  }
];

const exportFormats = [
  { id: "pdf", name: "PDF" },
  { id: "csv", name: "CSV" },
  { id: "excel", name: "Excel" }
];

export default function Reports() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterType, setFilterType] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [isGenerateDialogOpen, setIsGenerateDialogOpen] = useState(false);
  const [isReportDialogOpen, setIsReportDialogOpen] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  const [generateForm, setGenerateForm] = useState({
    report_type: "task_summary",
    name: "",
    description: "",
    start_date: "",
    end_date: "",
    project_key: "",
    user_id: "",
    is_public: false
  });
  const [availableProjects, setAvailableProjects] = useState([]);
  const [availableUsers, setAvailableUsers] = useState([]);
  const [projectsLoading, setProjectsLoading] = useState(false);
  const [usersLoading, setUsersLoading] = useState(false);
  
  const { toast } = useToast();

  useEffect(() => {
    fetchReports();
  }, [filterType, searchTerm]);

  useEffect(() => {
    if (isGenerateDialogOpen) {
      fetchProjectKeys();
      fetchUsers();
    }
  }, [isGenerateDialogOpen]);

  const fetchReports = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const filters = {
        report_type: filterType !== "all" ? filterType : undefined
      };
      
      const response = await reportsService.getReports(filters, 1, 100);
      
      if (response.success) {
        setReports(response.data.reports);
      } else {
        setError(response.error);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchProjectKeys = async () => {
    try {
      setProjectsLoading(true);
      const response = await reportsService.getReportableProjects();
      
      if (response.success) {
        setAvailableProjects(response.data.projects);
      } else {
        toast({
          title: "Failed to Load Projects",
          description: response.error || "Could not fetch available projects.",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Failed to Load Projects",
        description: "An unexpected error occurred while fetching projects.",
        variant: "destructive",
      });
    } finally {
      setProjectsLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      setUsersLoading(true);
      const response = await reportsService.getReportableUsers();
      
      if (response.success) {
        setAvailableUsers(response.data.users);
      } else {
        toast({
          title: "Failed to Load Users",
          description: response.error || "Could not fetch available users.",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Failed to Load Users",
        description: "An unexpected error occurred while fetching users.",
        variant: "destructive",
      });
    } finally {
      setUsersLoading(false);
    }
  };

  const handleGenerateReport = async (e) => {
    e.preventDefault();
    
    try {
      // Set a default name if none provided
      const reportData = {
        ...generateForm,
        name: generateForm.name || `${reportTypes.find(r => r.id === generateForm.report_type)?.name} Report`
      };
      
      const response = await reportsService.generateReport(reportData);
      
      if (response.success) {
        toast({
          title: "Report Generated",
          description: "Your report has been generated successfully.",
        });
        
        setIsGenerateDialogOpen(false);
        fetchReports();
        
        // Reset form
        setGenerateForm({
          report_type: "task_summary",
          name: "",
          description: "",
          start_date: "",
          end_date: "",
          project_key: "",
          user_id: "",
          is_public: false
        });
      } else {
        toast({
          title: "Generation Failed",
          description: response.error || "Failed to generate report.",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Generation Failed",
        description: "An unexpected error occurred.",
        variant: "destructive",
      });
    }
  };

  const handleViewReport = async (report) => {
    try {
      const response = await reportsService.getReportById(report.id);
      
      if (response.success) {
        setSelectedReport(response.data);
        setIsReportDialogOpen(true);
      } else {
        toast({
          title: "View Failed",
          description: response.error || "Failed to load report.",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "View Failed",
        description: "An unexpected error occurred.",
        variant: "destructive",
      });
    }
  };

  const handleDeleteReport = async (reportId, reportName) => {
    try {
      const response = await reportsService.deleteReport(reportId);
      
      if (response.success) {
        toast({
          title: "Report Deleted",
          description: `${reportName} has been deleted successfully.`,
        });
        
        fetchReports();
      } else {
        toast({
          title: "Deletion Failed",
          description: response.error || "Failed to delete report.",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Deletion Failed",
        description: "An unexpected error occurred.",
        variant: "destructive",
      });
    }
  };

  const handleExportReport = async (reportId, format) => {
    try {
      const response = await reportsService.exportReport(reportId, { format });
      
      if (response.success) {
        toast({
          title: "Export Started",
          description: `Your report is being exported as ${format.toUpperCase()}.`,
        });
      } else {
        toast({
          title: "Export Failed",
          description: response.error || "Failed to export report.",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Export Failed",
        description: "An unexpected error occurred.",
        variant: "destructive",
      });
    }
  };

  const handleInputChange = (field, value) => {
    setGenerateForm(prev => ({ ...prev, [field]: value }));
  };

  const getReportTypeDetails = (typeId) => {
    return reportTypes.find(type => type.id === typeId) || reportTypes[0];
  };

  const renderReportChart = (report) => {
    if (!report || !report.data || report.data.length === 0) {
      return (
        <div className="flex items-center justify-center h-64 text-muted-foreground">
          No data available for this report
        </div>
      );
    }

    // Group data by category for better visualization
    const categorizedData = {};
    report.data.forEach(point => {
      const category = point.metadata?.category || "uncategorized";
      if (!categorizedData[category]) {
        categorizedData[category] = [];
      }
      categorizedData[category].push(point);
    });

    // For simplicity, we'll render the first category as a bar chart
    const firstCategory = Object.keys(categorizedData)[0];
    const chartData = categorizedData[firstCategory] || [];

    if (chartData.length === 0) {
      return (
        <div className="flex items-center justify-center h-64 text-muted-foreground">
          No chart data available
        </div>
      );
    }

    return (
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="label" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="value" fill="#3b82f6" />
        </BarChart>
      </ResponsiveContainer>
    );
  };

  const renderReportSummary = (report) => {
    if (!report || !report.summary) {
      return null;
    }

    const summaryItems = Object.entries(report.summary).map(([key, value]) => {
      // Format key to be more readable
      const formattedKey = key
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase());
      
      return (
        <div key={key} className="flex justify-between py-2 border-b">
          <span className="text-muted-foreground">{formattedKey}</span>
          <span className="font-medium">
            {typeof value === 'number' ? value.toLocaleString() : value}
          </span>
        </div>
      );
    });

    return (
      <div className="space-y-2">
        <h4 className="font-semibold text-lg">Summary</h4>
        {summaryItems}
      </div>
    );
  };

  if (loading && reports.length === 0) {
    return (
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-foreground">Reports</h1>
            <p className="text-muted-foreground">Comprehensive insights and analytics</p>
          </div>
          <Dialog open={isGenerateDialogOpen} onOpenChange={setIsGenerateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Generate Report
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Generate New Report</DialogTitle>
                <DialogDescription>
                  Create a custom report based on your selected parameters
                </DialogDescription>
              </DialogHeader>
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              </div>
            </DialogContent>
          </Dialog>
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
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-foreground">Reports</h1>
            <p className="text-muted-foreground">Comprehensive insights and analytics</p>
          </div>
          <Dialog open={isGenerateDialogOpen} onOpenChange={setIsGenerateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Generate Report
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Generate New Report</DialogTitle>
                <DialogDescription>
                  Create a custom report based on your selected parameters
                </DialogDescription>
              </DialogHeader>
              <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-6 text-center">
                <h2 className="text-xl font-semibold text-destructive">Error Loading Reports</h2>
                <p className="mt-2 text-destructive/80">{error}</p>
                <button 
                  onClick={fetchReports}
                  className="mt-4 px-4 py-2 bg-destructive text-destructive-foreground rounded-md hover:opacity-90"
                >
                  Retry
                </button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Reports</h1>
          <p className="text-muted-foreground">Comprehensive insights and analytics</p>
        </div>
        <Dialog open={isGenerateDialogOpen} onOpenChange={setIsGenerateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Generate Report
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Generate New Report</DialogTitle>
              <DialogDescription>
                Create a custom report based on your selected parameters
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleGenerateReport} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="report_type">Report Type</Label>
                <Select 
                  value={generateForm.report_type} 
                  onValueChange={(value) => handleInputChange("report_type", value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select report type" />
                  </SelectTrigger>
                  <SelectContent>
                    {reportTypes.map((type) => (
                      <SelectItem key={type.id} value={type.id}>
                        <div className="flex items-center">
                          <type.icon className="w-4 h-4 mr-2" />
                          {type.name}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="name">Report Name</Label>
                <Input
                  id="name"
                  value={generateForm.name}
                  onChange={(e) => handleInputChange("name", e.target.value)}
                  placeholder="Enter report name"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Input
                  id="description"
                  value={generateForm.description}
                  onChange={(e) => handleInputChange("description", e.target.value)}
                  placeholder="Enter report description"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="start_date">Start Date</Label>
                  <Input
                    id="start_date"
                    type="date"
                    value={generateForm.start_date}
                    onChange={(e) => handleInputChange("start_date", e.target.value)}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="end_date">End Date</Label>
                  <Input
                    id="end_date"
                    type="date"
                    value={generateForm.end_date}
                    onChange={(e) => handleInputChange("end_date", e.target.value)}
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="project_key">Project</Label>
                  <Select 
                    value={generateForm.project_key} 
                    onValueChange={(value) => handleInputChange("project_key", value)}
                    disabled={projectsLoading}
                  >
                    <SelectTrigger>
                      {projectsLoading ? (
                        <div className="flex items-center">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary mr-2"></div>
                          Loading projects...
                        </div>
                      ) : (
                        <SelectValue placeholder="Select project" />
                      )}
                    </SelectTrigger>
                    <SelectContent>
                      {availableProjects.map((project) => (
                        <SelectItem key={project.key} value={project.key}>
                          {project.name} ({project.key})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="user_id">User</Label>
                  <Select 
                    value={generateForm.user_id} 
                    onValueChange={(value) => handleInputChange("user_id", value)}
                    disabled={usersLoading}
                  >
                    <SelectTrigger>
                      {usersLoading ? (
                        <div className="flex items-center">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary mr-2"></div>
                          Loading users...
                        </div>
                      ) : (
                        <SelectValue placeholder="Select user" />
                      )}
                    </SelectTrigger>
                    <SelectContent>
                      {availableUsers.map((user) => (
                        <SelectItem key={user.id} value={user.id}>
                          {user.name} ({user.email})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <input
                  id="is_public"
                  type="checkbox"
                  checked={generateForm.is_public}
                  onChange={(e) => handleInputChange("is_public", e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <Label htmlFor="is_public">Make this report public</Label>
              </div>
              
              <div className="flex justify-end space-x-2 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setIsGenerateDialogOpen(false)}
                >
                  Cancel
                </Button>
                <Button type="submit">Generate Report</Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input
            placeholder="Search reports..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        
        <div className="flex gap-2">
          <Select value={filterType} onValueChange={setFilterType}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Filter by type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              {reportTypes.map((type) => (
                <SelectItem key={type.id} value={type.id}>
                  {type.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Reports List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {reports
          .filter(report => 
            report.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            report.description.toLowerCase().includes(searchTerm.toLowerCase())
          )
          .map((report) => {
            const typeDetails = getReportTypeDetails(report.type);
            const Icon = typeDetails.icon;
            
            return (
              <Card key={report.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={`${typeDetails.color} w-10 h-10 rounded-lg flex items-center justify-center`}>
                        <Icon className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <CardTitle className="text-base line-clamp-1">{report.name}</CardTitle>
                        <div className="flex items-center space-x-2 mt-1">
                          <Badge variant="outline">{typeDetails.name}</Badge>
                          {report.is_public && (
                            <Badge className="bg-dashboard-success/10 text-dashboard-success hover:bg-dashboard-success/20">
                              Public
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <CardDescription className="line-clamp-2">
                    {report.description || "No description provided"}
                  </CardDescription>
                  
                  <div className="flex items-center text-xs text-muted-foreground">
                    <Calendar className="w-3 h-3 mr-1" />
                    <span>Created {new Date(report.created_at).toLocaleDateString()}</span>
                  </div>
                  
                  <div className="flex space-x-2">
                    <Button 
                      size="sm" 
                      variant="outline" 
                      onClick={() => handleViewReport(report)}
                    >
                      <Eye className="w-4 h-4 mr-1" />
                      View
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => handleDeleteReport(report.id, report.name)}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                    <Select onValueChange={(value) => handleExportReport(report.id, value)}>
                      <SelectTrigger className="w-10 p-2">
                        <Download className="w-4 h-4" />
                      </SelectTrigger>
                      <SelectContent>
                        {exportFormats.map((format) => (
                          <SelectItem key={format.id} value={format.id}>
                            Export as {format.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </CardContent>
              </Card>
            );
          })}
      </div>

      {reports.length === 0 && !loading && (
        <div className="flex items-center justify-center min-h-[400px]">
          <Card className="w-full max-w-md text-center">
            <CardHeader className="pb-4">
              <div className="flex justify-center mb-4">
                <div className="w-16 h-16 bg-dashboard-primary/10 rounded-full flex items-center justify-center">
                  <BarChart3 className="w-8 h-8 text-dashboard-primary" />
                </div>
              </div>
              <CardTitle>No Reports Found</CardTitle>
              <CardDescription>
                Generate your first report to get started with analytics and insights.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={() => setIsGenerateDialogOpen(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Generate Report
              </Button>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Report Detail Dialog */}
      <Dialog open={isReportDialogOpen} onOpenChange={setIsReportDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {selectedReport?.metadata?.name || "Report Details"}
            </DialogTitle>
            <DialogDescription>
              {selectedReport?.metadata?.description || "Detailed report information"}
            </DialogDescription>
          </DialogHeader>
          
          {selectedReport && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-muted/50 p-4 rounded-lg">
                  <div className="text-sm text-muted-foreground">Report Type</div>
                  <div className="font-medium">
                    {getReportTypeDetails(selectedReport.metadata.type)?.name}
                  </div>
                </div>
                <div className="bg-muted/50 p-4 rounded-lg">
                  <div className="text-sm text-muted-foreground">Created</div>
                  <div className="font-medium">
                    {new Date(selectedReport.metadata.created_at).toLocaleDateString()}
                  </div>
                </div>
                <div className="bg-muted/50 p-4 rounded-lg">
                  <div className="text-sm text-muted-foreground">Status</div>
                  <div className="font-medium">
                    <Badge className="bg-dashboard-success text-white">Generated</Badge>
                  </div>
                </div>
              </div>
              
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Report Data</h3>
                {renderReportChart(selectedReport)}
              </div>
              
              {selectedReport.summary && (
                <div className="space-y-4">
                  {renderReportSummary(selectedReport)}
                </div>
              )}
              
              <div className="flex justify-end space-x-2">
                <Select onValueChange={(value) => handleExportReport(selectedReport.metadata.id, value)}>
                  <SelectTrigger className="w-40">
                    <Download className="w-4 h-4 mr-2" />
                    Export Report
                  </SelectTrigger>
                  <SelectContent>
                    {exportFormats.map((format) => (
                      <SelectItem key={format.id} value={format.id}>
                        Export as {format.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}