"use client";

import { useState } from "react";
import UploadDocument from "@/components/UploadDocument";
import Chat from "@/components/Chat";
import { Document } from "@/types";

export default function Home() {
  const [currentDocument, setCurrentDocument] = useState<Document | null>(null);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              {currentDocument && (
                <button
                  onClick={() => setCurrentDocument(null)}
                  className="text-blue-500 hover:text-blue-700"
                >
                  Upload New Document
                </button>
              )}
            </div>

            {!currentDocument && (
              <div className="text-center">
                <UploadDocument onDocumentUploaded={setCurrentDocument} />
              </div>
            )}

            <Chat document={currentDocument} />
          </div>
        </div>
      </div>
    </div>
  );
}
