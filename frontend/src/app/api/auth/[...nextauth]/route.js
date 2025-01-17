import NextAuth from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";

const handler = NextAuth({
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "text", placeholder: "name@example.com" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials, req) {
        try {
          // 1) Call your FastAPI endpoint
          const res = await fetch("http://localhost:8000/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              email: credentials.email,
              password: credentials.password,
            }),
          });

          if (!res.ok) {
            // If the response is not OK, credentials are invalid
            return null;
          }

          // 2) Parse JSON from FastAPI
          const userData = await res.json();
          // For example: { id: 123, email: '...', name: '...', token: '...' }

          // 3) Return an object that represents the "user"
          // NextAuth will store this in the session
          return {
            id: userData.id,
            name: userData.name,
            email: userData.email,
            token: userData.token,
          };
        } catch (err) {
          console.error("Authorize error:", err);
          return null;
        }
      },
    }),
  ],

  // (Optional) Add custom callbacks for controlling session, JWT, etc.
  callbacks: {
    /**
     * Called whenever a JWT is created or updated.
     * Insert the user token into the JWT (so we can access it in session).
     */
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
        token.email = user.email;
        token.name = user.name;
        token.apiToken = user.token; // store the "token" from FastAPI
      }
      return token;
    },

    /**
     * Called whenever a session is checked (e.g., in a client component).
     * Transfers fields from the JWT into the session object.
     */
    async session({ session, token }) {
      if (token) {
        session.user.id = token.id;
        session.user.name = token.name;
        session.user.email = token.email;
        session.user.apiToken = token.apiToken;
      }
      return session;
    },
  },

  // You might want a custom sign-in page or error page
  pages: {
    signIn: "/signin", // e.g., a custom sign-in route
  },

  // SECRET is required for production JWT encryption, e.g. NEXTAUTH_SECRET env var
  secret: process.env.NEXTAUTH_SECRET || "mysecret",
});

// For Next.js App Router, export as GET and POST
export { handler as GET, handler as POST };
