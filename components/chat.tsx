"use client";

import { PreviewMessage, ThinkingMessage } from "@/components/message";
import { MultimodalInput } from "@/components/multimodal-input";
import { Overview } from "@/components/overview";
import { useScrollToBottom } from "@/hooks/use-scroll-to-bottom";
import { Message } from "ai";
import { useChat } from "ai/react";
import { toast } from "sonner";
import { InitMessageList } from "./test_init_message";
import { PlusCircle, Command, X } from "lucide-react";
import { Button } from "./ui/button";
import { useEffect } from "react";

const STORAGE_KEY = "chat_messages";

interface ChatProps {
  onClose?: () => void;
}

export function Chat({ onClose }: ChatProps) {
  const chatId = "001";

  // Load initial messages from localStorage or use InitMessageList
  const loadInitialMessages = (): Message[] => {
    if (typeof window === "undefined") return InitMessageList;
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : InitMessageList;
  };

  const {
    messages,
    setMessages,
    handleSubmit,
    input,
    setInput,
    append,
    isLoading,
    stop,
    reload,
  } = useChat({
    api: "/api/chat_streaming",
    maxSteps: 4,
    initialMessages: loadInitialMessages(),
    onError: (error: Error) => {
      if (error.message.includes("Too many requests")) {
        toast.error(
          "You are sending too many messages. Please try again later.",
        );
      }
    },
  });

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    }
  }, [messages]);

  const handleNewChat = () => {
    setMessages([]);
    setInput("");
    localStorage.removeItem(STORAGE_KEY);
  };

  const [messagesContainerRef, messagesEndRef] =
    useScrollToBottom<HTMLDivElement>();

  return (
    <div className="flex flex-col h-full bg-background">
      <div className="border-b px-4 py-3 flex justify-between items-center">
        <span className="text-sm font-medium text-foreground">Chat</span>
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            className="h-8 px-3 text-xs font-medium bg-muted/50 hover:bg-muted text-muted-foreground hover:text-foreground transition-colors flex items-center gap-2 rounded-lg"
            onClick={handleNewChat}
          >
            <PlusCircle className="h-3.5 w-3.5" />
            New conversation
          </Button>
          <div className="text-xs text-muted-foreground flex items-center gap-1 px-2 py-1 rounded-md bg-muted/50">
            <Command className="h-3 w-3" />
            <span>K</span>
          </div>
          {onClose && (
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="h-8 w-8 rounded-full hover:bg-muted"
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>
      <div
        ref={messagesContainerRef}
        className="flex flex-col gap-6 flex-1 overflow-y-auto pt-8 px-4"
      >
        {messages.length === 0 && <Overview />}

        {messages.map((message: Message, index: number) => (
          <PreviewMessage
            key={message.id}
            chatId={chatId}
            message={message}
            isLoading={isLoading && messages.length - 1 === index}
          />
        ))}

        {isLoading &&
          messages.length > 0 &&
          messages[messages.length - 1].role === "user" && <ThinkingMessage />}

        <div
          ref={messagesEndRef}
          className="shrink-0 min-w-[24px] min-h-[24px]"
        />
      </div>

      <div className="border-t p-4">
        <MultimodalInput
          chatId={chatId}
          input={input}
          setInput={setInput}
          handleSubmit={handleSubmit}
          isLoading={isLoading}
          stop={stop}
          messages={messages}
          setMessages={setMessages}
          append={append}
        />
      </div>
    </div>
  );
}
