import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Comask — Energy compliance, sourced to the statute",
  description:
    "Comask is a citation engine for energy compliance teams. Every answer is pinned to the exact rule — CRS, 4 CCR, FERC orders, eCFR, NERC standards. Not a chatbot. Not a guess.",
  metadataBase: new URL("https://comask.app"),
  openGraph: {
    title: "Comask — Energy compliance, sourced to the statute",
    description:
      "Stop reading AI hallucinations. Comask answers regulatory questions with inline citations to the exact rule — every fact pinned to the law.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
