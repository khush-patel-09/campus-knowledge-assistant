
"use client";

import { useState } from "react";
import type { FormEvent } from "react";
import {
  BookOpen,
  GraduationCap,
  MessageSquare,
  Plus,
  Search,
  Settings,
  ChevronDown,
  ArrowUp,
  FileText,
  ShieldCheck,
  Sparkles,
  PanelLeftClose,
  LoaderCircle,
  ExternalLink,
  AlertCircle,
} from "lucide-react";

import { askQuestion } from "@/services/api";
import type { Source } from "@/types/api";

const suggestions = [
  {
    title: "Academic curriculum",
    description: "Find courses, credits and prerequisites",
    question: "Which courses are included in the CSE curriculum?",
    icon: BookOpen,
  },
  {
    title: "University policies",
    description: "Understand rules and regulations",
    question: "What are the university's academic regulations?",
    icon: ShieldCheck,
  },
  {
    title: "Examination guidelines",
    description: "Explore examination procedures",
    question: "What happens if a student is caught violating examination rules?",
    icon: FileText,
  },
];

interface ChatMessage {
  id: number;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  error?: boolean;
}

export default function Home() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedSource, setSelectedSource] = useState<number | null>(null);

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();

    const trimmed = question.trim();

    if (!trimmed || loading) return;

    const userMessage: ChatMessage = {
      id: Date.now(),
      role: "user",
      content: trimmed,
    };

    setMessages((previous) => [...previous, userMessage]);
    setQuestion("");
    setLoading(true);
    setSelectedSource(null);

    try {
      const response = await askQuestion({
        question: trimmed,
      });

      const assistantMessage: ChatMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: response.answer,
        sources: response.sources,
      };

      setMessages((previous) => [...previous, assistantMessage]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content:
          error instanceof Error
            ? error.message
            : "Something went wrong. Please try again.",
        error: true,
      };

      setMessages((previous) => [...previous, errorMessage]);
    } finally {
      setLoading(false);
    }
  }

  function startNewConversation() {
    if (loading) return;

    setMessages([]);
    setQuestion("");
    setSelectedSource(null);
  }

  function renderAnswer(content: string, sources: Source[]) {
    const parts = content.split(/(\[\d+\])/g);

    return parts.map((part, index) => {
      const match = part.match(/^\[(\d+)\]$/);

      if (!match) {
        return <span key={index}>{part}</span>;
      }

      const reference = Number(match[1]);
      const exists = sources.some(
        (source) => source.reference === reference
      );

      if (!exists) {
        return <span key={index}>{part}</span>;
      }

      return (
        <button
          key={index}
          onClick={() => setSelectedSource(reference)}
          className="mx-0.5 inline-flex items-center rounded-md bg-[#edf0ff] px-1.5 py-0.5 text-xs font-semibold text-[#5267d8] transition hover:bg-[#dfe5ff]"
          title={`View source ${reference}`}
        >
          [{reference}]
        </button>
      );
    });
  }

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="hidden w-[260px] shrink-0 flex-col bg-[#151e31] text-white md:flex">
        <div className="flex h-[76px] items-center gap-3 border-b border-white/10 px-6">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#596fe0]">
            <GraduationCap size={21} />
          </div>
          <div>
            <h1 className="text-[15px] font-semibold tracking-tight">
              Campus AI
            </h1>
            <p className="text-[11px] text-slate-400">
              Knowledge Assistant
            </p>
          </div>
          <button className="ml-auto text-slate-400 hover:text-white">
            <PanelLeftClose size={17} />
          </button>
        </div>

        <div className="px-4 pt-6">
          <button
            onClick={startNewConversation}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-[#5267d8] px-4 py-3 text-sm font-medium transition hover:bg-[#6579e6] disabled:opacity-50"
            disabled={loading}
          >
            <Plus size={17} />
            New conversation
          </button>
        </div>

        <div className="px-5 pt-9">
          <p className="mb-3 text-[10px] font-semibold uppercase tracking-[1.5px] text-slate-500">
            Workspace
          </p>

          <nav className="space-y-1">
            <button className="flex w-full items-center gap-3 rounded-lg bg-white/10 px-3 py-2.5 text-left text-sm text-white">
              <MessageSquare size={17} />
              Ask a question
            </button>
            <button className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm text-slate-400 transition hover:bg-white/5 hover:text-white">
              <BookOpen size={17} />
              Knowledge base
            </button>
            <button className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm text-slate-400 transition hover:bg-white/5 hover:text-white">
              <Search size={17} />
              Search documents
            </button>
          </nav>
        </div>

        <div className="mt-auto border-t border-white/10 p-4">
          <button className="flex w-full items-center gap-3 rounded-lg px-3 py-3 text-sm text-slate-400 hover:bg-white/5 hover:text-white">
            <Settings size={17} />
            Settings
          </button>

          <div className="mt-3 flex items-center gap-3 rounded-lg bg-white/5 p-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#34435e] text-xs font-semibold">
              ST
            </div>
            <div>
              <p className="text-xs font-medium">Student Workspace</p>
              <p className="mt-0.5 text-[10px] text-slate-400">
                University account
              </p>
            </div>
            <ChevronDown size={15} className="ml-auto text-slate-500" />
          </div>
        </div>
      </aside>

      {/* Main workspace */}
      <main className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-[76px] shrink-0 items-center justify-between border-b border-[#e8ebf1] bg-white px-5 md:px-9">
          <div>
            <p className="text-sm font-semibold text-[#253047]">
              Ask a question
            </p>
            <p className="mt-1 text-[11px] text-[#8993a4]">
              Your university knowledge, in one place
            </p>
          </div>

          <div className="flex items-center gap-2 rounded-full border border-[#e8ebf1] bg-[#fbfcfe] px-3 py-2">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            <span className="text-[11px] font-medium text-[#687589]">
              API configured
            </span>
          </div>
        </header>

        {/* Chat area */}
        <section className="flex flex-1 flex-col overflow-y-auto">
          <div className="mx-auto flex w-full max-w-[850px] flex-1 flex-col px-5 py-10 md:px-10">
            {messages.length === 0 ? (
              <div className="my-auto">
                <div className="mb-7 flex h-12 w-12 items-center justify-center rounded-2xl bg-[#e9edff] text-[#5267d8]">
                  <Sparkles size={23} />
                </div>

                <p className="mb-3 text-xs font-semibold uppercase tracking-[2px] text-[#687bd7]">
                  CAMPUS KNOWLEDGE ASSISTANT
                </p>

                <h2 className="max-w-[650px] text-3xl font-semibold leading-tight tracking-tight text-[#1b263b] md:text-[42px]">
                  Your university knowledge,
                  <span className="text-[#6579dc]"> simplified.</span>
                </h2>

                <p className="mt-4 max-w-[540px] text-sm leading-7 text-[#778397]">
                  Ask questions about academic regulations, course
                  structures, examination policies and university
                  documentation. Get answers grounded in official sources.
                </p>

                <div className="mt-12">
                  <p className="mb-4 text-[11px] font-semibold uppercase tracking-[1.5px] text-[#8993a4]">
                    EXPLORE WHAT YOU CAN ASK
                  </p>

                  <div className="grid gap-3 md:grid-cols-3">
                    {suggestions.map((item) => {
                      const Icon = item.icon;

                      return (
                        <button
                          key={item.title}
                          onClick={() => setQuestion(item.question)}
                          className="group rounded-xl border border-[#e8ebf1] bg-white p-4 text-left transition hover:-translate-y-0.5 hover:border-[#cbd3fa] hover:shadow-md"
                        >
                          <div className="mb-5 flex h-9 w-9 items-center justify-center rounded-lg bg-[#f0f2ff] text-[#596ed7] transition group-hover:bg-[#e4e9ff]">
                            <Icon size={18} />
                          </div>
                          <p className="text-sm font-semibold text-[#28344b]">
                            {item.title}
                          </p>
                          <p className="mt-2 text-xs leading-5 text-[#8993a4]">
                            {item.description}
                          </p>
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-8">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={
                      message.role === "user"
                        ? "flex justify-end"
                        : "flex justify-start"
                    }
                  >
                    {message.role === "user" ? (
                      <div className="max-w-[80%] rounded-2xl rounded-br-sm bg-[#5267d8] px-5 py-3.5 text-sm leading-6 text-white">
                        {message.content}
                      </div>
                    ) : (
                      <div className="w-full">
                        <div className="mb-2 flex items-center gap-2">
                          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[#e9edff] text-[#5267d8]">
                            {message.error ? (
                              <AlertCircle size={15} />
                            ) : (
                              <Sparkles size={15} />
                            )}
                          </div>
                          <span className="text-xs font-semibold text-[#34415a]">
                            {message.error ? "Request failed" : "Campus AI"}
                          </span>
                        </div>

                        <div
                          className={`rounded-xl border p-5 text-sm leading-7 ${
                            message.error
                              ? "border-red-200 bg-red-50 text-red-700"
                              : "border-[#e8ebf1] bg-white text-[#39465c]"
                          }`}
                        >
                          {message.error
                            ? message.content
                            : renderAnswer(
                                message.content,
                                message.sources ?? []
                              )}
                        </div>

                        {!message.error &&
                          message.sources &&
                          message.sources.length > 0 && (
                            <div className="mt-4">
                              <p className="mb-3 text-[10px] font-semibold uppercase tracking-[1.5px] text-[#8993a4]">
                                SOURCES ({message.sources.length})
                              </p>

                              <div className="space-y-2">
                                {message.sources.map((source) => (
                                  <div
                                    key={source.reference}
                                    className={`rounded-xl border bg-white p-4 transition ${
                                      selectedSource === source.reference
                                        ? "border-[#8091ed] shadow-sm"
                                        : "border-[#e8ebf1]"
                                    }`}
                                  >
                                    <div className="flex items-start gap-3">
                                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[#f0f2ff] text-[#596ed7]">
                                        <FileText size={16} />
                                      </div>

                                      <div className="min-w-0 flex-1">
                                        <p className="text-xs font-semibold text-[#34415a]">
                                          [{source.reference}] {source.title}
                                        </p>

                                        <div className="mt-1 flex flex-wrap gap-x-3 gap-y-1 text-[11px] text-[#8993a4]">
                                          {source.page_number !== null && (
                                            <span>
                                              Page {source.page_number}
                                            </span>
                                          )}

                                          {source.section_title && (
                                            <span>
                                              {source.section_title}
                                            </span>
                                          )}
                                        </div>

                                        {source.source_url && (
                                          <a
                                            href={source.source_url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="mt-2 inline-flex items-center gap-1 text-xs font-medium text-[#5267d8] hover:underline"
                                          >
                                            Open source
                                            <ExternalLink size={12} />
                                          </a>
                                        )}
                                      </div>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                      </div>
                    )}
                  </div>
                ))}

                {loading && (
                  <div className="flex items-center gap-3 text-sm text-[#8993a4]">
                    <LoaderCircle
                      size={18}
                      className="animate-spin text-[#5267d8]"
                    />
                    Searching university documents and generating an answer...
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Input area */}
          <div className="sticky bottom-0 bg-gradient-to-t from-[#f8f9fc] via-[#f8f9fc] to-transparent px-5 pb-6 pt-4 md:px-10">
            <div className="mx-auto max-w-[850px]">
              <form
                onSubmit={handleSubmit}
                className="rounded-2xl border border-[#e1e5ed] bg-white p-3 shadow-[0_4px_24px_rgba(30,45,75,0.05)] transition focus-within:border-[#aebaf3]"
              >
                <textarea
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      e.currentTarget.form?.requestSubmit();
                    }
                  }}
                  placeholder="Ask anything about your university..."
                  rows={2}
                  disabled={loading}
                  className="w-full resize-none border-none bg-transparent px-2 py-2 text-sm text-[#28344b] outline-none placeholder:text-[#a0a9b8] disabled:opacity-60"
                />

                <div className="flex items-center justify-between px-1 pt-2">
                  <p className="text-[10px] text-[#a0a9b8]">
                    Answers are generated using university documents.
                  </p>

                  <button
                    type="submit"
                    disabled={!question.trim() || loading}
                    className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#5267d8] text-white transition hover:bg-[#4055c4] disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    {loading ? (
                      <LoaderCircle size={17} className="animate-spin" />
                    ) : (
                      <ArrowUp size={18} />
                    )}
                  </button>
                </div>
              </form>

              <p className="mt-3 text-center text-[10px] text-[#a0a9b8]">
                AI-generated responses may require verification. Always refer
                to official university documents.
              </p>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
