"use client"

import { useState, useRef, useEffect } from "react"
import { Send, Loader2, PawPrintIcon as Paw, Plus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { cn } from "@/lib/utils"
import { useToast } from "@/components/ui/use-toast"
import { ThemeToggle } from "@/components/theme-toggle"
import { Orbitron } from "next/font/google"

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

const orbitron = Orbitron({ subsets: ["latin"], weight: ["700"] })

export default function WoofieChatInterface() {
  const { toast } = useToast()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [typing, setTyping] = useState(false)
  const [animatedMessage, setAnimatedMessage] = useState("")
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [mounted, setMounted] = useState(false)
  const typingAudioRef = useRef<HTMLAudioElement | null>(null)

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [messages, animatedMessage])

  // Prevent hydration issues
  useEffect(() => {
    setMounted(true)
  }, [])

  // Preload typing sound
  useEffect(() => {
    try {
      const audio = new window.Audio("/sound.wav")
      audio.addEventListener('canplaythrough', () => {
        typingAudioRef.current = audio
        audio.volume = 0.25
      })
      audio.addEventListener('error', (e) => {
        console.warn('Failed to load typing sound:', e)
      })
    } catch (error) {
      console.warn('Failed to initialize audio:', error)
    }
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim()
    }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)
    setTyping(true)
    setAnimatedMessage("")

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [...messages, userMessage]
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to send message')
      }

      const data = await response.json()
      // Typing animation for assistant's message
      let i = 0
      const text = data.response
      setAnimatedMessage("")
      let lastSound = Date.now()
      function typeChar() {
        setAnimatedMessage((prev) => prev + text[i])
        // Play sound every 2 chars (throttle)
        if (typingAudioRef.current && i % 2 === 0 && text[i] !== ' ') {
          // Only play if at least 40ms since last play
          if (Date.now() - lastSound > 40) {
            typingAudioRef.current.currentTime = 0
            typingAudioRef.current.play()
            lastSound = Date.now()
          }
        }
        i++
        if (i < text.length) {
          setTimeout(typeChar, 18)
        } else {
          setTyping(false)
          // Add assistant message to messages
          setMessages(prev => [...prev, {
            id: Date.now().toString(),
            role: 'assistant',
            content: text
          }])
          setAnimatedMessage("")
        }
      }
      typeChar()
    } catch (error) {
      setTyping(false)
      setAnimatedMessage("")
      console.error('Error sending message:', error)
      toast({
        title: "Error",
        description: "Failed to send message. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  if (!mounted) return null

  return (
    <div className="relative flex flex-col h-screen overflow-hidden">
      {/* Animated Paw Prints Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(12)].map((_, i) => (
          <div
            key={i}
            className="absolute animate-float-paw"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${i * 1.5}s`,
              transform: `rotate(${Math.random() * 360}deg) scale(${0.5 + Math.random() * 0.5})`,
              opacity: '0.15',
              zIndex: 0
            }}
          >
            <svg
              width="40"
              height="40"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="text-teal-500 dark:text-teal-400"
            >
              <path d="M12 2c-1.5 0-3 1.5-3 3 0 1.5 1.5 3 3 3s3-1.5 3-3c0-1.5-1.5-3-3-3z" />
              <path d="M6 8c-1.5 0-3 1.5-3 3 0 1.5 1.5 3 3 3s3-1.5 3-3c0-1.5-1.5-3-3-3z" />
              <path d="M18 8c-1.5 0-3 1.5-3 3 0 1.5 1.5 3 3 3s3-1.5 3-3c0-1.5-1.5-3-3-3z" />
              <path d="M3 14c-1.5 0-3 1.5-3 3 0 1.5 1.5 3 3 3s3-1.5 3-3c0-1.5-1.5-3-3-3z" />
              <path d="M21 14c-1.5 0-3 1.5-3 3 0 1.5 1.5 3 3 3s3-1.5 3-3c0-1.5-1.5-3-3-3z" />
            </svg>
          </div>
        ))}
      </div>

      {/* Enhanced Animated Gradient Background */}
      <div className="fixed inset-0 -z-10 animate-gradient-move bg-gradient-to-br from-teal-400/40 via-blue-600/40 to-purple-700/40 dark:from-teal-700/30 dark:via-blue-800/30 dark:to-purple-800/30 opacity-90" />
      <div className="fixed inset-0 -z-10 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-white/50 via-transparent to-transparent dark:from-slate-800/30" />
      {/* Glassmorphism Overlay */}
      <div className="fixed inset-0 -z-10 bg-white/20 dark:bg-slate-800/20 backdrop-blur-3xl" />
      
      <header className="flex items-center justify-between p-4 border-b bg-white/50 dark:bg-slate-800/50 shadow-lg dark:border-slate-700/50 transition-all duration-300 backdrop-blur-xl sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-teal-400 to-teal-600 dark:from-teal-500/80 dark:to-teal-600/80 flex items-center justify-center transition-all duration-300 shadow-lg hover:scale-105">
            <Paw className="h-6 w-6 text-white" />
          </div>
          <h1 className={"text-2xl font-bold bg-gradient-to-r from-teal-600 to-blue-600 dark:from-teal-400/90 dark:to-blue-400/90 bg-clip-text text-transparent transition-all duration-300 " + orbitron.className}>
            Woofie Health Assistant
          </h1>
        </div>
        <div className="flex items-center gap-3">
          <ThemeToggle />
        </div>
      </header>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin scrollbar-thumb-slate-300 dark:scrollbar-thumb-slate-600 scrollbar-track-transparent">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center p-8">
            <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-teal-400/20 to-blue-500/20 dark:from-teal-500/20 dark:to-blue-600/20 shadow-2xl flex items-center justify-center mb-6 transition-all duration-300 backdrop-blur-xl border border-white/30 dark:border-slate-700/30 hover:scale-105">
              <Paw className="h-12 w-12 text-teal-500 dark:text-teal-400/90 transition-all duration-300" />
            </div>
            <h2 className="text-2xl font-bold bg-gradient-to-r from-teal-600 to-blue-600 dark:from-teal-400/90 dark:to-blue-400/90 bg-clip-text text-transparent mb-3 transition-all duration-300">How can I help with your pet's health?</h2>
            <p className="text-slate-600 dark:text-slate-300 max-w-md mb-8 transition-all duration-300 text-lg">
              Ask me about nutrition, exercise, symptoms, or preventive care for your furry friend.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-md w-full">
              {[
                "What vaccines does my puppy need?",
                "How much exercise for a dog?",
                "What should I feed my dog?",
                "How often should I feed my Pet Bird?",
              ].map((suggestion, i) => (
                <Button
                  key={i}
                  variant="outline"
                  className="justify-start text-left h-auto py-4 px-6 border-slate-200/50 dark:border-slate-700/50 hover:bg-teal-50/50 dark:hover:bg-slate-700/50 hover:text-teal-700 dark:hover:text-teal-300 whitespace-normal break-words text-sm transition-all duration-300 rounded-2xl hover:scale-105 hover:shadow-lg backdrop-blur-sm"
                  onClick={() => {
                    setInput(suggestion)
                    setTimeout(() => handleSubmit(new Event("submit") as any), 100)
                  }}
                >
                  {suggestion}
                </Button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  "flex items-start gap-3 animate-fade-in",
                  message.role === "user" ? "justify-end" : "justify-start",
                )}
              >
                {message.role !== "user" && (
                  <Avatar className="w-10 h-10 rounded-2xl bg-gradient-to-br from-teal-400 to-teal-600 dark:from-teal-500/80 dark:to-teal-600/80 transition-all duration-300 shadow-lg">
                    <AvatarFallback className="bg-transparent text-white">
                      <Paw className="h-5 w-5" />
                    </AvatarFallback>
                  </Avatar>
                )}

                <div
                  className={cn(
                    "relative px-6 py-4 rounded-3xl max-w-[80%] break-words transition-all duration-300 shadow-xl border backdrop-blur-xl",
                    message.role === "user"
                      ? "bg-gradient-to-br from-teal-400/90 to-teal-600/90 dark:from-teal-500/80 dark:to-teal-600/80 text-white border-teal-200/50 dark:border-teal-700/50"
                      : "bg-white/40 dark:bg-slate-700/40 text-slate-900 dark:text-slate-100 border-white/30 dark:border-slate-600/30",
                  )}
                >
                  <span className="drop-shadow-[0_0_6px_rgba(0,255,255,0.3)]">{message.content}</span>
                  {message.role !== "user" && (
                    <span className="absolute -top-2 -left-2 w-4 h-4 bg-gradient-to-br from-cyan-400/70 to-blue-500/70 rounded-full blur-sm opacity-70 animate-pulse" />
                  )}
                </div>

                {message.role === "user" && (
                  <Avatar className="w-10 h-10 rounded-2xl bg-gradient-to-br from-slate-200 to-slate-300 dark:from-slate-600 dark:to-slate-700 transition-all duration-300 shadow-lg">
                    <AvatarFallback className="bg-transparent">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="18"
                        height="18"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        className="text-slate-600 dark:text-slate-300"
                      >
                        <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path>
                        <circle cx="12" cy="7" r="4"></circle>
                      </svg>
                    </AvatarFallback>
                  </Avatar>
                )}
              </div>
            ))}
            {/* Typing animation */}
            {typing && (
              <div className="flex items-start gap-3 animate-fade-in justify-start">
                <Avatar className="w-10 h-10 rounded-2xl bg-gradient-to-br from-teal-400 to-teal-600 dark:from-teal-500/80 dark:to-teal-600/80 transition-all duration-300 shadow-lg">
                  <AvatarFallback className="bg-transparent text-white">
                    <Paw className="h-5 w-5" />
                  </AvatarFallback>
                </Avatar>
                <div className="relative px-6 py-4 rounded-3xl max-w-[80%] break-words bg-white/40 dark:bg-slate-700/40 text-slate-900 dark:text-slate-100 border border-white/30 dark:border-slate-600/30 shadow-xl backdrop-blur-xl transition-all duration-300">
                  <span className="drop-shadow-[0_0_6px_rgba(0,255,255,0.3)]">{animatedMessage || <span className="opacity-60 italic">Woofie is typing...</span>}</span>
                  {animatedMessage && <span className="animate-pulse">|</span>}
                  <span className="absolute -top-2 -left-2 w-4 h-4 bg-gradient-to-br from-cyan-400/70 to-blue-500/70 rounded-full blur-sm opacity-70 animate-pulse" />
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t bg-white/50 dark:bg-slate-800/50 dark:border-slate-700/50 transition-all duration-300 backdrop-blur-xl sticky bottom-0">
        <div className="flex items-center gap-4 max-w-5xl mx-auto">
          <div className="text-sm text-slate-500 dark:text-slate-400 flex items-center gap-1.5 whitespace-nowrap">
            <span>Made with</span>
            <svg className="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
            </svg>
            <span>by</span>
            <a 
              href="https://aashikbaruwal.com.np/" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-teal-600 dark:text-teal-400 hover:underline transition-colors"
            >
              Aashik
            </a>
          </div>
          <form onSubmit={handleSubmit} className="flex items-center gap-3 flex-1">
            <Button 
              type="button" 
              size="icon" 
              variant="outline" 
              className="rounded-2xl border-slate-200/50 dark:border-slate-700/50 hover:bg-slate-100/50 dark:hover:bg-slate-700/50 transition-all duration-300 hover:scale-105"
            >
              <Plus className="h-5 w-5 text-slate-600 dark:text-slate-300" />
              <span className="sr-only">Add attachment</span>
            </Button>
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about your pet's health..."
              className="flex-1 bg-slate-50/50 dark:bg-slate-700/50 border-slate-200/50 dark:border-slate-600/50 rounded-2xl focus-visible:ring-teal-500 dark:focus-visible:ring-teal-400 text-slate-900 dark:text-slate-100 placeholder:text-slate-500 dark:placeholder:text-slate-400 transition-all duration-300 h-12 text-base"
              disabled={isLoading}
            />
            <Button
              type="submit"
              size="icon"
              className="rounded-2xl bg-gradient-to-br from-teal-400 to-teal-600 dark:from-teal-500/80 dark:to-teal-600/80 hover:from-teal-500 hover:to-teal-700 dark:hover:from-teal-600/90 dark:hover:to-teal-700/90 transition-all duration-300 h-12 w-12 hover:scale-105 shadow-lg"
              disabled={isLoading || !input.trim()}
            >
              {isLoading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
              <span className="sr-only">Send message</span>
            </Button>
          </form>
        </div>
      </div>
    </div>
  )
}
