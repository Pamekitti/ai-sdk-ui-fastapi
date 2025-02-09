import "./globals.css";
import { GeistSans } from "geist/font/sans";
import { Toaster } from "sonner";
import { cn } from "@/lib/utils";
import { Navbar } from "@/components/navbar";
import { FloatingChat } from "@/components/floating-chat";
import { ThemeProvider } from "@/components/theme-provider";

export const metadata = {
  title: "Alto CERO AI Assistant",
  description:
    "Alto CERO AI Assistant is an intelligent building management system that uses AI to optimize your facility operations.",
  openGraph: {
    images: [
      {
        url: "/og?title=Alto CERO AI Assistant",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    images: [
      {
        url: "/og?title=Alto CERO AI Assistant",
      },
    ],
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head />
      <body className={cn(GeistSans.className, "antialiased min-h-screen")}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <Toaster position="top-center" richColors />
          <Navbar />
          {children}
          <FloatingChat />
        </ThemeProvider>
      </body>
    </html>
  );
}
