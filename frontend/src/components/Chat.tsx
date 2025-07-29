"use client";

import { useState } from "react";
import { ChatMessage, Document } from "@/types";

interface ChatProps {
  document: Document;
}

export default function Chat({ document }: ChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      message: input,
      timestamp: new Date(),
      isUser: true,
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);
    setInput("");

    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: input,
          document_id: document.id,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to get response");
      }

      const result = await response.json();

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        message: input,
        response: result.response,
        sources: result.sources,
        timestamp: new Date(),
        isUser: false,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Chat error:", error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        message: input,
        response: "Sorry, I encountered an error processing your question.",
        timestamp: new Date(),
        isUser: false,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-[600px] border rounded-lg bg-white">
      <div className="border-b p-4 bg-gray-500">
        <h3 className="font-medium">Chat about: {document.filename}</h3>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <p>Ask questions about your construction document!</p>
            <p className="text-sm mt-2">
              Try: "What's the size of the bathtub?" or "What type of cooktop is
              used?"
            </p>
          </div>
        )}

        {messages.map((message) => (
          <div key={message.id}>
            <div className="flex justify-end mb-2">
              <div className="bg-blue-500 text-white p-3 rounded-lg max-w-xs">
                {message.message}
              </div>
            </div>
            {!message.isUser && (
              <div className="flex justify-start">
                <div className="bg-gray-100 p-3 rounded-lg max-w-lg">
                  <p className="mb-2">{message.response}</p>

                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-3 pt-3 border-t">
                      <p className="text-xs font-medium text-gray-600 mb-2">
                        Sources:
                      </p>
                      {message.sources.map((source, idx) => (
                        <div key={idx} className="text-xs text-gray-500 mb-1">
                          <span className="font-medium">
                            Page {source.page}:
                          </span>
                          <span className="ml-1">{source.content_preview}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 p-3 rounded-lg">Thinking...</div>
          </div>
        )}
      </div>
      <div className="border-t p-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question about the document..."
            className="flex-1 border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
