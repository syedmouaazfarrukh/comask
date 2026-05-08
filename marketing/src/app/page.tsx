import { AppBar } from "@/components/AppBar";
import { Hero } from "@/components/Hero";
import { CitationDifference } from "@/components/CitationDifference";
import { KnowledgeGraph } from "@/components/KnowledgeGraph";
import { Coverage } from "@/components/Coverage";
import { UseCases } from "@/components/UseCases";
import { CTA } from "@/components/CTA";
import { Footer } from "@/components/Footer";

export default function Home() {
  return (
    <>
      <AppBar />
      <main>
        <section id="demo">
          <Hero />
        </section>
        <CitationDifference />
        <KnowledgeGraph />
        <Coverage />
        <UseCases />
        <CTA />
      </main>
      <Footer />
    </>
  );
}
