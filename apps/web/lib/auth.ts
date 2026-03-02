/**
 * Auth helper — placeholder for WorkOS / Supabase Auth integration.
 * Returns the current session with organizationId for tenant-scoped queries.
 */

export interface Session {
  userId: string;
  organizationId: string;
  email: string;
  role: "OWNER" | "ADMIN" | "MEMBER" | "VIEWER";
}

export async function auth(): Promise<Session | null> {
  // TODO: Wire to WorkOS getSession() or Supabase auth.getUser()
  // For development, return a stub session
  return {
    userId: "00000000-0000-0000-0000-000000000001",
    organizationId: "00000000-0000-0000-0000-000000000010",
    email: "dev@productos.app",
    role: "OWNER",
  };
}

export async function requireAuth(): Promise<Session> {
  const session = await auth();
  if (!session) throw new Error("Unauthorized");
  return session;
}
