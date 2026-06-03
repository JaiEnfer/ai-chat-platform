import { ChatWidget } from "@/components/chat-widget/ChatWidget";
import { SignInButton, SignUpButton, UserButton } from "@clerk/nextjs";
import { currentUser } from "@clerk/nextjs/server";
import Link from "next/link";

export const dynamic = "force-dynamic";
export const revalidate = 0;

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

async function getCompanyByUserId(userId: string) {
  if (!API_BASE_URL) {
    return null;
  }

  const response = await fetch(`${API_BASE_URL}/users/${userId}/company`, {
    cache: "no-store",
  });

  if (!response.ok) {
    return null;
  }

  return response.json() as Promise<{
    id: number;
    name: string;
    website: string;
    widget_key: string;
  }>;
}

export default async function Home() {
  const user = await currentUser();
  const company = user ? await getCompanyByUserId(user.id) : null;

  return (
    <main className="min-h-screen bg-gray-100 text-gray-900">
      <nav className="mx-auto flex max-w-6xl items-center justify-between p-6">
        <h1 className="text-xl font-bold">AI Chat Platform</h1>

        <div className="flex items-center gap-3">
          {user ? (
            <>
              <Link
                href="/dashboard"
                className="rounded-xl bg-gray-900 px-4 py-2 text-sm font-medium text-white"
              >
                Dashboard
              </Link>
              <UserButton />
            </>
          ) : (
            <>
              <SignInButton mode="modal">
                <button className="rounded-xl border border-gray-900 px-4 py-2 text-sm font-medium text-gray-900">
                  Sign In
                </button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button className="rounded-xl bg-gray-900 px-4 py-2 text-sm font-medium text-white">
                  Get Started
                </button>
              </SignUpButton>
            </>
          )}
        </div>
      </nav>

      {!user && (
        <section className="mx-auto max-w-6xl px-6 py-20">
          <div className="max-w-3xl">
            <p className="text-sm font-semibold uppercase tracking-wide text-gray-500">
              AI Lead Generation for SMB Websites
            </p>

            <h2 className="mt-4 text-5xl font-bold tracking-tight">
              Turn website visitors into qualified leads.
            </h2>

            <p className="mt-6 text-lg text-gray-600">
              Add an AI chatbot to your business website. Answer customer
              questions, collect leads, and review conversations from one simple
              dashboard.
            </p>
          </div>
        </section>
      )}

      {user && !company && (
        <section className="mx-auto max-w-3xl px-6 py-20">
          <div className="rounded-2xl bg-white p-6 shadow-sm">
            <h2 className="text-2xl font-bold">Set up your company first</h2>
            <p className="mt-2 text-gray-600">
              Create your company profile before using the AI assistant.
            </p>

            <Link
              href="/dashboard"
              className="mt-4 inline-block rounded-xl bg-gray-900 px-4 py-2 text-sm font-medium text-white"
            >
              Set Up Company
            </Link>
          </div>
        </section>
      )}

      {user && company && (
        <section className="mx-auto max-w-6xl px-6 py-10">
          <div className="mb-6">
            <h2 className="text-3xl font-bold">AI Assistant</h2>
            <p className="mt-2 text-gray-600">
              Testing chatbot for {company.name}
            </p>
          </div>

          <div className="h-[650px] max-w-xl rounded-2xl border bg-white shadow-sm">
            <ChatWidget widgetKey={company.widget_key} embedded />
          </div>
        </section>
      )}
    </main>
  );
}
