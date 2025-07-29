"use client";
import MessageFooter from "@/components/MessageFooter";
import UploadDocument from "@/components/UploadDocument";

export default function Home() {
  return (
    <div className="font-sans bg-white flex w-full justify-center items-center flex-col min-h-screen p-8 pb-20 gap-16 sm:p-20">
      <UploadDocument onDocumentUploaded={() => {}} />
      <MessageFooter />
    </div>
  );
}
