"use client";

import { useState } from "react";
import { Document } from "../types";

interface UploadDocumentProps {
  onDocumentUploaded: (doc: Document) => void;
}

export default function UploadDocument({
  onDocumentUploaded,
}: UploadDocumentProps) {
  const [uploading, setUploading] = useState(false);

  const handleFileUpload = async (file: File) => {
    if (!file || file.type !== "application/pdf") {
      console.error("Invalid file type");
      return;
    }

    setUploading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/upload`,
        {
          method: "POST",
          body: formData,
        }
      );
      if (!response.ok) {
        throw new Error("Upload failed");
      }
      const result = await response.json();
      onDocumentUploaded({
        id: result.document_id,
        filename: result.filename,
        status: "ready",
      });
    } catch (error) {
      console.error("Upload error:", error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <div
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${uploading ? "opacity-50 cursor-not-allowed" : ""}
        `}
        onClick={() => document.getElementById("fileInput")?.click()}
      >
        {uploading ? (
          <div className="flex flex-col items-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-4"></div>
            <p className="text-gray-600">Processing document...</p>
          </div>
        ) : (
          <div>
            <p className="text-lg font-medium text-gray-900 mb-2">
              Upload Construction Document
            </p>
            <p className="text-sm text-gray-600">
              Drag and drop your PDF here, or click to select
            </p>
          </div>
        )}

        <input
          id="fileInput"
          type="file"
          accept=".pdf"
          onChange={(e) =>
            e.target.files?.[0] && handleFileUpload(e.target.files[0])
          }
          className="hidden"
          disabled={uploading}
        />
      </div>
    </div>
  );
}
