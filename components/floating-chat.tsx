"use client";

import { useState, useEffect, useCallback } from "react";
import { Chat } from "./chat";
import { Button } from "./ui/button";
import { MessageCircle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export function FloatingChat() {
    const [isOpen, setIsOpen] = useState(false);

    const closeChat = useCallback(() => {
        setIsOpen(false);
    }, []);

    const toggleChat = useCallback(() => {
        setIsOpen(prev => !prev);
    }, []);

    useEffect(() => {
        const handleKeyDown = (event: KeyboardEvent) => {
            // Handle ESC key
            if (event.key === "Escape" && isOpen) {
                closeChat();
            }

            // Handle Command+K (Mac) or Control+K
            if ((event.metaKey || event.ctrlKey) && event.key === "k") {
                event.preventDefault();
                toggleChat();
            }
        };

        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, [isOpen, closeChat, toggleChat]);

    const handleBackdropClick = (event: React.MouseEvent) => {
        if (event.target === event.currentTarget) {
            closeChat();
        }
    };

    return (
        <AnimatePresence>
            {isOpen ? (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="fixed inset-0 bg-black/60 backdrop-blur-md z-50 flex items-center justify-center"
                    onClick={handleBackdropClick}
                >
                    <motion.div
                        initial={{ scale: 0.95, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0.95, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        className="relative w-[90vw] max-w-[800px] h-[80vh] max-h-[800px] bg-background border border-gray-800/50 rounded-2xl shadow-2xl overflow-hidden"
                    >
                        <Chat onClose={closeChat} />
                    </motion.div>
                </motion.div>
            ) : (
                <motion.div
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 0.9, opacity: 0 }}
                    className="fixed bottom-4 right-4 z-50"
                >
                    <Button
                        onClick={toggleChat}
                        size="icon"
                        className="h-12 w-12 rounded-full shadow-2xl bg-primary hover:bg-primary/90 transition-all duration-200 hover:scale-105 hover:shadow-primary/20"
                    >
                        <MessageCircle className="h-6 w-6" />
                    </Button>
                </motion.div>
            )}
        </AnimatePresence>
    );
} 