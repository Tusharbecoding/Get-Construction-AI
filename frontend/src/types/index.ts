export interface Document {
  id: string;
  filename: string;
  status: "processing" | "ready" | "error";
}

export interface ChatMessage {
  id: string;
  message: string;
  response?: string;
  sources?: Source[];
  timestamp: Date;
  isUser: boolean;
}

export interface Source {
  page: number;
  section: number;
  content_preview: string;
  content_type: string;
}
