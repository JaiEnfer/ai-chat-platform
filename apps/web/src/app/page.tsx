import { SignInButton, SignUpButton, UserButton } from "@clerk/nextjs";
import { auth } from "@clerk/nextjs/server";
import Link from "next/link";

export default async function Home() {
  const { userId } = await auth();

  return (
    <main className="min-h-screen bg-gray-100 text-gray-900">
      <nav className="mx-auto flex max-w-6xl items-center justify-between p-6">
        <h1 className="text-xl font-bold">AI Chat Platform</h1>

        <div className="flex items-center gap-3">
          {userId ? (
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

          <div className="mt-8 flex gap-3">
            {userId ? (
              <Link
                href="/dashboard"
                className="rounded-xl bg-gray-900 px-5 py-3 text-sm font-medium text-white"
              >
                Go to Dashboard
              </Link>
            ) : (
              <SignUpButton mode="modal">
                <button className="rounded-xl bg-gray-900 px-5 py-3 text-sm font-medium text-white">
                  Start Free Pilot
                </button>
              </SignUpButton>
            )}
          </div>
        </div>

        <div className="mt-16 grid gap-4 md:grid-cols-3">
          <FeatureCard
            title="AI Chat Widget"
            description="Answer customer questions directly on your website."
          />
          <FeatureCard
            title="Lead Capture"
            description="Collect names, emails, phone numbers, and customer intent."
          />
          <FeatureCard
            title="Business Dashboard"
            description="Manage knowledge, leads, conversations, and analytics."
          />
        </div>
      </section>
    </main>
  );
}

function FeatureCard(props: { title: string; description: string }) {
  return (
    <div className="rounded-2xl bg-white p-6 shadow-sm">
      <h3 className="font-semibold">{props.title}</h3>
      <p className="mt-2 text-sm text-gray-600">{props.description}</p>
    </div>
  );
}
