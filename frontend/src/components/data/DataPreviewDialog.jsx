import { Eye, Download, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

const sampleData = [
  { id: "EMP001", name: "John Doe", department: "Engineering", role: "Senior Developer", status: "Active", joinDate: "2023-01-15" },
  { id: "EMP002", name: "Jane Smith", department: "Product", role: "Product Manager", status: "Active", joinDate: "2023-02-20" },
  { id: "EMP003", name: "Mike Johnson", department: "Design", role: "UI/UX Designer", status: "Inactive", joinDate: "2023-03-10" },
  { id: "EMP004", name: "Sarah Wilson", department: "DevOps", role: "DevOps Engineer", status: "Active", joinDate: "2023-04-05" },
  { id: "EMP005", name: "Alex Brown", department: "QA", role: "QA Analyst", status: "Active", joinDate: "2023-05-12" },
];

export function DataPreviewDialog({ open, onClose, file }) {
  if (!file) return null;

  const getStatusBadge = (status) => {
    return status === "Active" ? (
      <Badge className="bg-dashboard-success text-white">Active</Badge>
    ) : (
      <Badge variant="outline">Inactive</Badge>
    );
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <div>
              <DialogTitle className="text-xl">Data Preview</DialogTitle>
              <DialogDescription>
                Previewing first 5 rows of {file.name}
              </DialogDescription>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          </div>
        </DialogHeader>

        {/* File Information */}
        <div className="bg-muted/50 rounded-lg p-4 space-y-2">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="font-medium">File Name:</span>
              <p className="text-muted-foreground">{file.name}</p>
            </div>
            <div>
              <span className="font-medium">Records:</span>
              <p className="text-muted-foreground">{file.records} rows</p>
            </div>
            <div>
              <span className="font-medium">Size:</span>
              <p className="text-muted-foreground">{file.size}</p>
            </div>
            <div>
              <span className="font-medium">Type:</span>
              <p className="text-muted-foreground">{file.type}</p>
            </div>
          </div>
        </div>

        <Separator />

        {/* Data Preview Table */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Data Preview</h3>
            <div className="flex space-x-2">
              <Button variant="outline" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Export Preview
              </Button>
              <Button variant="outline" size="sm">
                <Eye className="w-4 h-4 mr-2" />
                View Full Data
              </Button>
            </div>
          </div>

          <div className="border rounded-lg overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Employee ID</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Department</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Join Date</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sampleData.map((row) => (
                  <TableRow key={row.id}>
                    <TableCell className="font-medium">{row.id}</TableCell>
                    <TableCell>{row.name}</TableCell>
                    <TableCell>{row.department}</TableCell>
                    <TableCell>{row.role}</TableCell>
                    <TableCell>{getStatusBadge(row.status)}</TableCell>
                    <TableCell>{row.joinDate}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          <div className="text-sm text-muted-foreground">
            Showing 5 of {file.records} records. <button className="text-dashboard-primary hover:underline">View all records</button>
          </div>
        </div>

        {/* Data Quality Insights */}
        <Separator />
        
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Data Quality Insights</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-dashboard-success/10 border border-dashboard-success/20 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-dashboard-success rounded-full"></div>
                <span className="text-sm font-medium">Complete Records</span>
              </div>
              <p className="text-2xl font-bold text-dashboard-success mt-2">{file.records - 2}</p>
              <p className="text-sm text-muted-foreground">Records with all fields</p>
            </div>
            
            <div className="bg-dashboard-warning/10 border border-dashboard-warning/20 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-dashboard-warning rounded-full"></div>
                <span className="text-sm font-medium">Missing Data</span>
              </div>
              <p className="text-2xl font-bold text-dashboard-warning mt-2">2</p>
              <p className="text-sm text-muted-foreground">Records with missing fields</p>
            </div>
            
            <div className="bg-dashboard-danger/10 border border-dashboard-danger/20 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-dashboard-danger rounded-full"></div>
                <span className="text-sm font-medium">Duplicates</span>
              </div>
              <p className="text-2xl font-bold text-dashboard-danger mt-2">0</p>
              <p className="text-sm text-muted-foreground">Duplicate records found</p>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

export default DataPreviewDialog;