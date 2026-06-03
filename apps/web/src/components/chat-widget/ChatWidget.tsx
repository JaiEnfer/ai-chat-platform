"use client";
import { FormEvent, useEffect, useState } from "react";

type ChatMessage = {
  role: "visitor" | "bot";
  text: string;
};

type ChatResponse = {
  answer: string;
  should_collect_lead: boolean;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;
const WIDGET_KEY = process.env.NEXT_PUBLIC_WIDGET_KEY;

type ChatWidgetProps = {
  widgetKey?: string;
  embedded?: boolean;
};

export function ChatWidget({ widgetKey, embedded = false }: ChatWidgetProps) {
  const resolvedWidgetKey = widgetKey ?? WIDGET_KEY;
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "bot",
      text: "Hi! How can I help you today?",
    },
  ]);

  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [shouldShowLeadForm, setShouldShowLeadForm] = useState(false);

  const [leadName, setLeadName] = useState("");
  const [leadEmail, setLeadEmail] = useState("");
  const [leadPhone, setLeadPhone] = useState("");
  const [isSubmittingLead, setIsSubmittingLead] = useState(false);
  const [visitorId, setVisitorId] = useState<string | null>(null);

  useEffect(() => {
    const storageKey = "berlin-chatbot-visitor-id";
    const existingVisitorId = window.localStorage.getItem(storageKey);

    if (existingVisitorId) {
      setVisitorId(existingVisitorId);
      return;
    }

    const newVisitorId = crypto.randomUUID();

    window.localStorage.setItem(storageKey, newVisitorId);
    setVisitorId(newVisitorId);
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedInput = input.trim();

    if (!API_BASE_URL || !resolvedWidgetKey || !visitorId) {
      return null;
    }

    if (!trimmedInput || isSending) {
      return;
    }

    setMessages((currentMessages) => [
      ...currentMessages,
      {
        role: "visitor",
        text: trimmedInput,
      },
    ]);

    setInput("");
    setIsSending(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          widget_key: resolvedWidgetKey,
          visitor_id: visitorId,
          message: trimmedInput,
        }),
      });

      if (!response.ok) {
        throw new Error("Chat request failed");
      }

      const data = (await response.json()) as ChatResponse;

      setMessages((currentMessages) => [
        ...currentMessages,
        {
          role: "bot",
          text: data.answer,
        },
      ]);

      setShouldShowLeadForm(data.should_collect_lead);
    } catch {
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          role: "bot",
          text: "Sorry, something went wrong. Please try again.",
        },
      ]);
    } finally {
      setIsSending(false);
    }
  }

  async function handleLeadSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedName = leadName.trim();
    const trimmedEmail = leadEmail.trim();
    const trimmedPhone = leadPhone.trim();

    if (!trimmedName || !trimmedEmail || isSubmittingLead) {
      return;
    }

    setIsSubmittingLead(true);

    try {
      const response = await fetch(`${API_BASE_URL}/leads`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          widget_key: resolvedWidgetKey,
          name: trimmedName,
          email: trimmedEmail,
          phone: trimmedPhone || null,
          message: "Lead submitted from chatbot widget.",
        }),
      });

      if (!response.ok) {
        throw new Error("Lead submission failed");
      }

      setMessages((currentMessages) => [
        ...currentMessages,
        {
          role: "bot",
          text: "Thank you. The team will contact you soon.",
        },
      ]);

      setLeadName("");
      setLeadEmail("");
      setLeadPhone("");
      setShouldShowLeadForm(false);
    } catch {
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          role: "bot",
          text: "Sorry, I could not submit your details. Please try again.",
        },
      ]);
    } finally {
      setIsSubmittingLead(false);
    }
  }

  return (
    <div
      className={
        embedded
          ? "flex h-full w-full flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm"
          : "fixed bottom-6 right-6 flex h-[560px] w-[360px] flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-xl"
      }
    >
      <div className="bg-gray-900 px-4 py-3 text-white">
        <h2 className="text-sm font-semibold">AI Assistant</h2>
        <p className="text-xs text-gray-300">Usually replies instantly</p>
      </div>

      <div className="flex-1 space-y-3 overflow-y-auto bg-gray-50 p-4">
        {messages.map((message, index) => (
          <div
            key={`${message.role}-${index}`}
            className={
              message.role === "visitor"
                ? "ml-auto max-w-[80%] rounded-2xl bg-gray-900 px-3 py-2 text-sm text-white"
                : "mr-auto max-w-[80%] rounded-2xl bg-white px-3 py-2 text-sm text-gray-900 shadow-sm"
            }
          >
            {message.text}
          </div>
        ))}

        {shouldShowLeadForm && (
          <form
            onSubmit={handleLeadSubmit}
            className="space-y-2 rounded-2xl bg-white p-3 shadow-sm"
          >
            <p className="text-sm font-medium text-gray-900">
              Leave your details
            </p>

            <input
              value={leadName}
              onChange={(event) => setLeadName(event.target.value)}
              placeholder="Your name"
              className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm text-gray-900 outline-none focus:border-gray-900"
            />

            <input
              value={leadEmail}
              onChange={(event) => setLeadEmail(event.target.value)}
              placeholder="Your email"
              type="email"
              className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm text-gray-900 outline-none focus:border-gray-900"
            />

            <input
              value={leadPhone}
              onChange={(event) => setLeadPhone(event.target.value)}
              placeholder="Phone optional"
              className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm text-gray-900 outline-none focus:border-gray-900"
            />

            <button
              type="submit"
              disabled={isSubmittingLead}
              className="w-full rounded-xl bg-gray-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
            >
              Submit
            </button>
          </form>
        )}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2 border-t p-3">
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Type your question..."
          className="flex-1 rounded-xl border border-gray-300 px-3 py-2 text-sm text-gray-900 outline-none focus:border-gray-900"
        />

        <button
          type="submit"
          disabled={isSending}
          className="rounded-xl bg-gray-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  );
}
