import NextAuth from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";

const handler = NextAuth({
  session: {
    strategy: "jwt",
    // We'll override maxAge in the signIn callback if rememberMe is set
    maxAge: 60 * 60 * 24 // default 1 day, can be overridden
  },
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "text" },
        password: { label: "Password", type: "password" },
        rememberMe: { label: "Remember Me", type: "checkbox" }
      },
      async authorize(credentials) {
        try {
          // Call your FastAPI login
          const res = await fetch("http://localhost:8000/users/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              email: credentials.email,
              password: credentials.password
            })
          });
          if (!res.ok) return null;

          const data = await res.json(); 
          // data = { access_token, token_type, user_id }

          return {
            id: data.user_id,
            email: credentials.email,
            accessToken: data.access_token,
            rememberMe: credentials.rememberMe // store the user's choice
          };
        } catch (err) {
          console.error("Authorize error:", err);
          return null;
        }
      }
    })
  ],
  callbacks: {
    async jwt({ token, user, account }) {
      if (user) {
        token.userId = user.id;
        token.email = user.email;
        token.accessToken = user.accessToken;
        token.rememberMe = user.rememberMe;
      }
      return token;
    },
    async session({ session, token }) {
      session.user.id = token.userId;
      session.user.email = token.email;
      session.user.accessToken = token.accessToken;
      return session;
    },
    async signIn({ user }) {
      // If rememberMe is true, set a longer maxAge
      if (user?.rememberMe === "on" || user?.rememberMe === true) {
        // e.g. 30 days:
        this.session.maxAge = 60 * 60 * 24 * 30;
      } else {
        // e.g. 1 day or 0
        this.session.maxAge = 60 * 60 * 24;
      }
      return true; // allow sign in
    }
  },
  pages: {
    signIn: "/login"
  },
  secret: "MY_NEXTAUTH_SECRET"
});

export { handler as GET, handler as POST };
