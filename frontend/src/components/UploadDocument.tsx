import React from "react";

const UploadDocument = () => {
  return (
    <div>
      <form action="">
        <input type="file" accept=".pdf, .doc, .docx" />
        <button>Upload</button>
      </form>
    </div>
  );
};

export default UploadDocument;
