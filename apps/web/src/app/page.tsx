import { ChatWidget } from "@/components/chat-widget/ChatWidget";

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-100 p-10">
      <h1 className="text-3xl font-bold text-gray-900">
        Berlin AI Chatbot Platform
      </h1>

      <p className="mt-4 max-w-xl text-gray-700">
        Local preview page for the customer support and lead generation chatbot.
      </p>

      <ChatWidget />
    </main>
  );
}