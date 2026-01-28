import { useState, useRef } from "react";
import { Upload, FileText, AlertCircle, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";

export function FileUploadZone({ onFileUpload, accept = ".xlsx,.xls,.csv", maxSize = 10 * 1024 * 1024 }) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const fileInputRef = useRef(null);
  const { toast } = useToast();

  const supportedFormats = accept.split(',').map(format => format.trim());

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    handleFiles(files);
  };

  const validateFile = (file) => {
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!supportedFormats.includes(fileExtension)) {
      return { valid: false, error: `Invalid file format. Supported formats: ${supportedFormats.join(', ')}` };
    }
    
    if (file.size > maxSize) {
      return { valid: false, error: `File too large. Maximum size: ${(maxSize / (1024 * 1024)).toFixed(1)}MB` };
    }
    
    return { valid: true };
  };

  const handleFiles = async (files) => {
    if (files.length === 0) return;

    const validFiles = [];
    const errors = [];

    // Validate all files first
    files.forEach(file => {
      const validation = validateFile(file);
      if (validation.valid) {
        validFiles.push(file);
      } else {
        errors.push({ file: file.name, error: validation.error });
      }
    });

    // Show errors if any
    if (errors.length > 0) {
      errors.forEach(({ file, error }) => {
        toast({
          title: `Error with ${file}`,
          description: error,
          variant: "destructive",
        });
      });
    }

    // Process valid files
    if (validFiles.length > 0) {
          setIsUploading(true);
          setUploadProgress(0);

          for (let i = 0; i < validFiles.length; i++) {
            const file = validFiles[i];

            try {
              setUploadProgress(Math.round((i / validFiles.length) * 100));

              // 🔥 REAL upload — WAIT for backend
              await onFileUpload(file);

              setUploadedFiles(prev => [
                ...prev,
                {
                  id: Date.now() + i,
                  name: file.name,
                  size: (file.size / (1024 * 1024)).toFixed(2) + " MB",
                  status: "success",
                  uploadedAt: new Date().toLocaleTimeString(),
                },
              ]);
            } catch (err) {
              toast({
                title: `Upload failed: ${file.name}`,
                description: err.message || "Upload failed",
                variant: "destructive",
              });
            }
          }

          setUploadProgress(100);
          setIsUploading(false);

      
      toast({
        title: "Upload Successful",
        description: `${validFiles.length} file(s) uploaded successfully.`,
      });

      // Reset progress after a delay
      setTimeout(() => {
        setUploadProgress(0);
      }, 2000);
    }

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const removeFile = (fileId) => {
    setUploadedFiles(prev => prev.filter(file => file.id !== fileId));
  };

  return (
    <div className="space-y-4">
      {/* Upload Zone */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 cursor-pointer ${
          isDragOver
            ? 'border-dashboard-primary bg-dashboard-primary/5 scale-105'
            : 'border-muted-foreground/30 hover:border-dashboard-primary/50 bg-muted/30'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <Upload className={`w-12 h-12 mx-auto mb-4 transition-colors ${
          isDragOver ? 'text-dashboard-primary' : 'text-muted-foreground'
        }`} />
        <p className="text-lg font-medium text-foreground mb-2">
          {isDragOver ? 'Drop files here' : 'Drop your files here, or click to browse'}
        </p>
        <p className="text-sm text-muted-foreground mb-4">
          Supported formats: {supportedFormats.join(', ')} (Max {(maxSize / (1024 * 1024)).toFixed(1)}MB)
        </p>
        <Button variant="outline" type="button">
          Browse Files
        </Button>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={accept}
          className="hidden"
          onChange={handleFileSelect}
        />
      </div>

      {/* Upload Progress */}
      {isUploading && (
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Uploading files...</span>
            <span>{Math.round(uploadProgress)}%</span>
          </div>
          <Progress value={uploadProgress} className="w-full" />
        </div>
      )}

      {/* Recently Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-sm font-medium">Recently Uploaded</h4>
          <div className="space-y-2">
            {uploadedFiles.map((file) => (
              <div
                key={file.id}
                className="flex items-center space-x-3 p-3 bg-muted/50 rounded-lg"
              >
                <FileText className="w-5 h-5 text-dashboard-primary" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-foreground truncate">
                    {file.name}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {file.size} • Uploaded at {file.uploadedAt}
                  </p>
                </div>
                <Badge className="bg-dashboard-success text-white">
                  <CheckCircle className="w-3 h-3 mr-1" />
                  Success
                </Badge>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => removeFile(file.id)}
                  className="text-muted-foreground hover:text-destructive"
                >
                  ×
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default FileUploadZone;