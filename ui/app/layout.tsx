export const metadata = {
  title: "MacPorts Ports — Modern UI",
  description: "A modern, client-side UI for ports.macports.org",
};

import "./globals.css";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { ThemeProvider } from "@/lib/theme-context";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased flex flex-col">
        <ThemeProvider>
          <Header />
          <main className="container py-8 flex-1">{children}</main>
          <Footer />
        </ThemeProvider>
      </body>
    </html>
  );
}
