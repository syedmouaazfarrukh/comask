import { AnswerDemo } from "./AnswerDemo";
import { DEMO_URL } from "@/lib/links";

export function Hero() {
  return (
    <section id="top" className="hero">
      <div className="hero-grid" aria-hidden />
      <div className="hero-glow" aria-hidden />
      <div className="container hero-inner">
        <div className="hero-copy">
          <p className="kicker-accent">// Citation engine · energy compliance</p>
          <h1 className="display-xl">
            Compliance answers,
            <br />
            <span className="accent">sourced to the statute.</span>
          </h1>
          <p className="body-lg muted">
            Comask is built for energy attorneys and compliance teams. Every
            answer pins each fact to the exact rule — CRS, 4&nbsp;CCR, FERC
            orders, eCFR, NERC standards. Not a chatbot. Not a guess.
          </p>
          <div className="hero-cta">
            <a href={DEMO_URL} className="btn btn-solid btn-lg">
              Request a demo →
            </a>
            <a href="#difference" className="btn btn-line btn-lg">
              Why not just RAG?
            </a>
          </div>
          <div className="hero-meta">
            <span className="label-mono"><span className="dot" /> Inline citations</span>
            <span className="label-mono"><span className="dot" /> Knowledge graph</span>
            <span className="label-mono"><span className="dot" /> Validated against source</span>
          </div>
        </div>
        <div className="hero-visual">
          <AnswerDemo />
        </div>
      </div>
    </section>
  );
}
