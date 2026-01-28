import { Upload, FileText, Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";

const lastUploadedFiles = [
  // {
  //   name: "jira_tasks_Q4_2024.xlsx",
  //   records: 102,
  //   uploadedAt: "2 hours ago",
  // },
  {
    name: "team_roster_updated_Sep.xlsx",
    records: 45,
    uploadedAt: "1 day ago",
  },
  {
    name: "project_timelines_Q4.xlsx",
    records: 23,
    uploadedAt: "3 days ago",
  },
];

export function EmployeeDataManagement() {
  return (
    <div className="bg-card rounded-lg p-6 shadow-lg hover:shadow-xl transition-all duration-200 border border-border">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-foreground">
          Employee Data Management
        </h2>
        <p className="text-sm text-muted-foreground">
          Upload and manage employees records and leave data.
        </p>
      </div>

      {/* Upload Section */}
      <div className="mb-8">
        <h3 className="text-sm font-semibold text-foreground mb-4">
          Upload Employee Data
        </h3>
        <p className="text-xs text-muted-foreground mb-4">
          Securely upload Excel files (.xlsx) containing employee records and
          Jira related data.
        </p>

        <div className="border-2 border-dashed border-muted-foreground/30 rounded-lg p-8 text-center hover:border-dashboard-primary/50 transition-colors cursor-pointer bg-muted/30">
          <Upload className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-sm text-muted-foreground mb-2">
            Drag and drop your Excel file here, or click to select
          </p>
          <Button variant="outline" className="mt-2">
            Browse Files
          </Button>
          <p className="text-xs text-gray-500 mt-2">Supported format: .xlsx</p>
        </div>
      </div>

      {/* Last Uploaded Files */}
      <div>
        <h3 className="text-sm font-semibold text-foreground mb-4">
          Last Uploaded Files:
        </h3>
        <div className="space-y-3">
          {lastUploadedFiles.map((file, index) => (
            <div
              key={index}
              className="flex items-center space-x-3 p-3 bg-muted/50 rounded-lg hover:bg-muted transition-colors"
            >
              <FileText className="w-5 h-5 text-dashboard-primary" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-foreground truncate">
                  {file.name}
                </p>
                <p className="text-xs text-muted-foreground">
                  ({file.records} records)
                </p>
              </div>
              <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                <Calendar className="w-3 h-3" />
                <span>{file.uploadedAt}</span>
              </div>
            </div>
          ))}
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          Supported format: .xlsx
        </p>
      </div>
    </div>
  );
}

export default EmployeeDataManagement;
