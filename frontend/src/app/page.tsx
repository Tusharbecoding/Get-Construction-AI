"use client";
import Chat from "@/components/Chat";
import UploadDocument from "@/components/UploadDocument";
import { Document } from "@/types";

export default function Home() {
  const document: Document = {
    id: "1",
    filename: "test.pdf",
    status: "processing",
  };

  return (
    <div className="font-sans bg-white flex w-full justify-center items-center flex-col min-h-screen p-8 pb-20 gap-16 sm:p-20">
      <UploadDocument onDocumentUploaded={() => {}} />
      <Chat document={document} />
    </div>
  );
}
