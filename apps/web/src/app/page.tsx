import { ChatWidget } from "@/components/chat-widget/ChatWidget";
import { SignInButton, SignUpButton, UserButton } from "@clerk/nextjs";
import { auth } from "@clerk/nextjs/server";

export default async function Home() {
  const { userId } = await auth();

  return (
    <main className="min-h-screen bg-gray-100 p-10">
      <h1 className="text-3xl font-bold text-gray-900">
        Berlin AI Chatbot Platform
      </h1>

      <p className="mt-4 max-w-xl text-gray-700">
        Local preview page for the customer support and lead generation chatbot.
      </p>

      <div className="mt-6 flex items-center gap-3">
        {userId ? (
          <UserButton />
        ) : (
          <>
            <SignInButton mode="modal">
              <button
                type="button"
                className="rounded-xl bg-gray-900 px-4 py-2 text-sm font-medium text-white"
              >
                Sign In
              </button>
            </SignInButton>

            <SignUpButton mode="modal">
              <button
                type="button"
                className="rounded-xl border border-gray-900 px-4 py-2 text-sm font-medium text-gray-900"
              >
                Sign Up
              </button>
            </SignUpButton>
          </>
        )}
      </div>

      <ChatWidget />
    </main>
  );
}
