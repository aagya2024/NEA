/**
 * ChatWidget — Floating AI chatbot panel.
 * Features: formatted responses, chat history, smooth UX.
 */

import { useState, useRef, useEffect, useCallback } from 'react';
import { FiMessageSquare, FiX, FiSend, FiTrash2 } from 'react-icons/fi';
import api from '../../api/axios';
import { useAuth } from '../../context/AuthContext';

// Simple markdown-ish renderer for chat responses
function FormattedMessage({ text }) {
    if (!text) return null;

    const lines = text.split('\n');
    return (
        <div className="space-y-1">
            {lines.map((line, i) => {
                // Bold text: **text**
                const parts = line.split(/(\*\*.*?\*\*)/g);
                const rendered = parts.map((part, j) => {
                    if (part.startsWith('**') && part.endsWith('**')) {
                        return <strong key={j}>{part.slice(2, -2)}</strong>;
                    }
                    return <span key={j}>{part}</span>;
                });

                // Bullet points
                if (line.trim().startsWith('•') || line.trim().startsWith('-')) {
                    return <div key={i} className="pl-2">{rendered}</div>;
                }

                // Numbered items
                if (/^\s*\d+\./.test(line)) {
                    return <div key={i} className="pl-2">{rendered}</div>;
                }

                // Empty lines as spacing
                if (line.trim() === '') {
                    return <div key={i} className="h-1" />;
                }

                return <div key={i}>{rendered}</div>;
            })}
        </div>
    );
}

export default function ChatWidget() {
    const { isAuthenticated } = useAuth();
    const [open, setOpen] = useState(false);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [hasLoaded, setHasLoaded] = useState(false);
    const endRef = useRef(null);
    const inputRef = useRef(null);

    // Auto-scroll to bottom
    useEffect(() => {
        endRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, loading]);

    // Focus input when panel opens
    useEffect(() => {
        if (open && inputRef.current) {
            setTimeout(() => inputRef.current?.focus(), 100);
        }
    }, [open]);

    // Load chat history when first opened
    const loadHistory = useCallback(async () => {
        if (hasLoaded) return;
        try {
            const { data } = await api.get('/chat/history', { params: { limit: 20 } });
            if (data && data.length > 0) {
                const history = data.reverse().flatMap((item) => [
                    { role: 'user', content: item.message },
                    { role: 'assistant', content: item.response },
                ]);
                setMessages(history);
            }
        } catch {
            // silently ignore history load errors
        }
        setHasLoaded(true);
    }, [hasLoaded]);

    useEffect(() => {
        if (open) loadHistory();
    }, [open, loadHistory]);

    if (!isAuthenticated) return null;

    const sendMessage = async () => {
        const text = input.trim();
        if (!text || loading) return;

        const userMsg = { role: 'user', content: text };
        setMessages((prev) => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            const { data } = await api.post('/chat', { message: text });
            setMessages((prev) => [
                ...prev,
                { role: 'assistant', content: data.response || data.message || 'No response.' },
            ]);
        } catch (err) {
            const detail = err.response?.data?.detail;
            setMessages((prev) => [
                ...prev,
                {
                    role: 'assistant',
                    content: detail || 'Sorry, something went wrong. Please try again.',
                },
            ]);
        } finally {
            setLoading(false);
        }
    };

    const clearChat = () => {
        setMessages([]);
        setHasLoaded(false);
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <>
            {/* Floating Button */}
            {!open && (
                <button
                    onClick={() => setOpen(true)}
                    className="fixed bottom-6 right-6 w-14 h-14 bg-nea-blue text-white rounded-full shadow-lg
                     flex items-center justify-center hover:bg-nea-blue-dark transition-all
                     hover:scale-110 z-50 group"
                    title="AI Assistant"
                >
                    <FiMessageSquare className="w-6 h-6 group-hover:scale-110 transition-transform" />
                </button>
            )}

            {/* Chat Panel */}
            {open && (
                <div className="fixed bottom-6 right-6 w-96 h-[520px] bg-white border border-gray-200
                        rounded-2xl shadow-2xl flex flex-col z-50 overflow-hidden
                        animate-[slideUp_0.25s_ease-out]"
                    style={{ animation: 'slideUp 0.25s ease-out' }}
                >
                    {/* Header */}
                    <div className="bg-nea-blue text-white px-4 py-3 flex items-center justify-between shrink-0">
                        <div className="flex items-center gap-2">
                            <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                                <img src="/nea-logo.png" alt="NEA" className="w-5 h-5 object-contain" />
                            </div>
                            <div>
                                <div className="text-sm font-semibold">NEA AI Assistant</div>
                                <div className="text-[10px] text-white/60">Ask about NEA policies & documents</div>
                            </div>
                        </div>
                        <div className="flex items-center gap-1">
                            <button
                                onClick={clearChat}
                                className="p-1.5 hover:bg-white/20 rounded-lg transition-colors"
                                title="Clear chat"
                            >
                                <FiTrash2 className="w-4 h-4" />
                            </button>
                            <button
                                onClick={() => setOpen(false)}
                                className="p-1.5 hover:bg-white/20 rounded-lg transition-colors"
                            >
                                <FiX className="w-5 h-5" />
                            </button>
                        </div>
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-3">
                        {messages.length === 0 && (
                            <div className="text-center text-gray-400 text-sm mt-6">
                                <div className="w-12 h-12 rounded-full bg-blue-50 flex items-center justify-center mx-auto mb-3">
                                    <img src="/nea-logo.png" alt="NEA" className="w-7 h-7 object-contain" />
                                </div>
                                <p className="font-medium text-gray-600 mb-1">NEA AI Assistant</p>
                                <p className="text-xs text-gray-400">
                                    Ask me about news, notices, documents,<br />
                                    forms, acts, or job openings.
                                </p>

                                {/* Quick suggestions */}
                                <div className="mt-4 space-y-1.5">
                                    {[
                                        'What can you help me with?',
                                        'Show me the latest notices',
                                        'Are there any job openings?',
                                    ].map((suggestion) => (
                                        <button
                                            key={suggestion}
                                            onClick={() => { setInput(suggestion); }}
                                            className="block w-full text-left px-3 py-2 bg-gray-50 hover:bg-blue-50
                                               rounded-lg text-xs text-gray-600 hover:text-nea-blue transition-colors"
                                        >
                                            {suggestion}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}
                        {messages.map((msg, i) => (
                            <div
                                key={i}
                                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                <div
                                    className={`max-w-[85%] px-3 py-2 rounded-xl text-sm leading-relaxed ${msg.role === 'user'
                                        ? 'bg-nea-blue text-white rounded-br-sm'
                                        : 'bg-gray-100 text-gray-800 rounded-bl-sm'
                                        }`}
                                >
                                    {msg.role === 'assistant' ? (
                                        <FormattedMessage text={msg.content} />
                                    ) : (
                                        msg.content
                                    )}
                                </div>
                            </div>
                        ))}
                        {loading && (
                            <div className="flex justify-start">
                                <div className="bg-gray-100 px-4 py-2.5 rounded-xl rounded-bl-sm">
                                    <div className="flex gap-1.5">
                                        <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                        <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                        <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={endRef} />
                    </div>

                    {/* Input */}
                    <div className="border-t border-gray-200 p-3 shrink-0">
                        <form
                            onSubmit={(e) => { e.preventDefault(); sendMessage(); }}
                            className="flex items-center gap-2"
                        >
                            <input
                                ref={inputRef}
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder="Type your question..."
                                className="flex-1 px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm
                           focus:outline-none focus:ring-2 focus:ring-nea-blue/30 transition-all"
                                disabled={loading}
                            />
                            <button
                                type="submit"
                                disabled={loading || !input.trim()}
                                className="p-2.5 bg-nea-blue text-white rounded-lg hover:bg-nea-blue-dark
                           disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                            >
                                <FiSend className="w-4 h-4" />
                            </button>
                        </form>
                    </div>
                </div>
            )}

            {/* Animation keyframe */}
            <style>{`
                @keyframes slideUp {
                    from { opacity: 0; transform: translateY(20px) scale(0.95); }
                    to { opacity: 1; transform: translateY(0) scale(1); }
                }
            `}</style>
        </>
    );
}
