// app/api/auth/[...nextauth]/route.js
"use server";

import NextAuth from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";

const authOptions = {
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "text" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        try {
          // Create AbortController for timeout
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
          
          // Call the new JSON login endpoint - must use absolute URL for server-side requests
          const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/users/json-token`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              email: credentials.email,
              password: credentials.password
            }),
            signal: controller.signal
          });
          
          // Clear the timeout
          clearTimeout(timeoutId);
          
          // Handle response
          if (!res.ok) {
            const errorText = await res.text();
            console.error("Auth error:", res.status, errorText);
            return null;
          }
          
          const user = await res.json();
          if (user.access_token) {
            return {
              id: user.user_id, // Ensure your backend returns user_id, or adapt as needed.
              email: credentials.email,
              access_token: user.access_token
            };
          }
          return null;
        } catch (error) {
          console.error("Auth exception:", error);
          // Don't throw, return null to show a friendly error via NextAuth
          return null;
        }
      }
    })
  ],
  secret: process.env.NEXTAUTH_SECRET,
  session: { 
    strategy: "jwt",
    maxAge: 6 * 60 * 60, // 6 hours in seconds
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.accessToken = user.access_token;
        token.id = user.id;
      }
      return token;
    },
    async session({ session, token }) {
      session.user.accessToken = token.accessToken;
      session.user.id = token.id;
      return session;
    }
  }
};

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };
