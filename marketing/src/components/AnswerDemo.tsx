"use client";

import { useEffect, useMemo, useRef, useState } from "react";

type Citation = {
  id: number;
  shortId: string;
  authority: "Colorado statute" | "Colorado regulation" | "Federal regulation" | "FERC order";
  jurisdiction: string;
  excerpt: string;
  effective: string;
};

type Scenario = {
  question: string;
  answer: AnswerNode[];
  citations: Citation[];
  confidence: "High" | "Medium";
  sourcesFound: number;
  elapsed: string;
};

type AnswerNode =
  | { kind: "text"; text: string }
  | { kind: "anchor"; text: string; cite: number }
  | { kind: "br" };

const SCENARIOS: Scenario[] = [
  {
    question: "What are Colorado's renewable energy requirements for IOUs?",
    answer: [
      { kind: "text", text: "Colorado's Renewable Energy Standard is established under " },
      { kind: "anchor", text: "CRS 40-2-124", cite: 1 },
      { kind: "text", text: ". Investor-owned utilities must generate " },
      { kind: "anchor", text: "30% of electricity from renewable sources by 2020", cite: 1 },
      { kind: "text", text: ", scaling to " },
      { kind: "anchor", text: "100% clean energy by 2040", cite: 2 },
      { kind: "text", text: " under the Clean Energy Plan. Compliance is filed annually with the Colorado PUC per " },
      { kind: "anchor", text: "4 CCR 723-3-3654", cite: 3 },
      { kind: "text", text: "." },
    ],
    citations: [
      {
        id: 1,
        shortId: "CRS § 40-2-124",
        authority: "Colorado statute",
        jurisdiction: "Colorado",
        excerpt:
          "Each qualifying retail utility shall generate or cause to be generated electricity from eligible energy resources in the following minimum amounts… 30% of its retail electricity sales by 2020.",
        effective: "Effective 2019-05-30",
      },
      {
        id: 2,
        shortId: "HB 19-1261 § 25-7-105",
        authority: "Colorado statute",
        jurisdiction: "Colorado",
        excerpt:
          "Greenhouse gas emissions from the electric sector shall be reduced by at least 90% from 2005 levels by 2050, with interim targets of 50% by 2030 — interpreted by the PUC as a 100% clean-energy pathway by 2040 for IOUs.",
        effective: "Effective 2019-05-30",
      },
      {
        id: 3,
        shortId: "4 CCR 723-3-3654",
        authority: "Colorado regulation",
        jurisdiction: "Colorado PUC",
        excerpt:
          "Each qualifying retail utility shall file a renewable energy standard compliance plan and annual progress report demonstrating attainment of the standards in § 40-2-124, C.R.S.",
        effective: "Last amended 2024-01-15",
      },
    ],
    confidence: "High",
    sourcesFound: 5,
    elapsed: "3.2s",
  },
  {
    question: "Who qualifies for net metering under Colorado PUC rules?",
    answer: [
      { kind: "text", text: "Net metering eligibility for IOU customers is governed by " },
      { kind: "anchor", text: "4 CCR 723-3-3664", cite: 1 },
      { kind: "text", text: ". A customer-generator qualifies if their facility uses an " },
      { kind: "anchor", text: "eligible energy resource", cite: 1 },
      { kind: "text", text: " and is sized so that " },
      { kind: "anchor", text: "expected annual production does not exceed 120% of average annual consumption", cite: 1 },
      { kind: "text", text: ". For systems above 25 kW, an interconnection agreement under " },
      { kind: "anchor", text: "FERC Small Generator Interconnection Procedures", cite: 2 },
      { kind: "text", text: " also applies." },
    ],
    citations: [
      {
        id: 1,
        shortId: "4 CCR 723-3-3664",
        authority: "Colorado regulation",
        jurisdiction: "Colorado PUC",
        excerpt:
          "A qualifying retail utility shall make net metering available to any customer-generator… provided the generating capacity is intended primarily to offset part or all of the customer-generator's own electricity requirements.",
        effective: "Last amended 2023-09-12",
      },
      {
        id: 2,
        shortId: "FERC Order 2006-A",
        authority: "FERC order",
        jurisdiction: "Federal",
        excerpt:
          "Standardizes interconnection procedures for generating facilities no larger than 20 MW… requires public utilities to incorporate the SGIP into their open access transmission tariffs.",
        effective: "Issued 2005-12-12",
      },
    ],
    confidence: "High",
    sourcesFound: 4,
    elapsed: "2.8s",
  },
  {
    question: "What's the deadline for filing an Integrated Resource Plan in Colorado?",
    answer: [
      { kind: "text", text: "Investor-owned utilities must file an Electric Resource Plan with the PUC " },
      { kind: "anchor", text: "every four years", cite: 1 },
      { kind: "text", text: ", per " },
      { kind: "anchor", text: "4 CCR 723-3-3603", cite: 1 },
      { kind: "text", text: ". The plan must cover a " },
      { kind: "anchor", text: "minimum 7-year acquisition period", cite: 1 },
      { kind: "text", text: " and include modeled scenarios consistent with the " },
      { kind: "anchor", text: "Clean Energy Plan emission reductions", cite: 2 },
      { kind: "text", text: "." },
    ],
    citations: [
      {
        id: 1,
        shortId: "4 CCR 723-3-3603",
        authority: "Colorado regulation",
        jurisdiction: "Colorado PUC",
        excerpt:
          "Each utility shall file an electric resource plan no less frequently than every four years… covering a planning period of no less than seven years.",
        effective: "Last amended 2022-11-08",
      },
      {
        id: 2,
        shortId: "CRS § 40-3.2-104",
        authority: "Colorado statute",
        jurisdiction: "Colorado",
        excerpt:
          "Clean energy plans shall reduce greenhouse gas emissions associated with electricity sold by 80% from 2005 levels by 2030.",
        effective: "Effective 2019-08-02",
      },
    ],
    confidence: "High",
    sourcesFound: 3,
    elapsed: "2.4s",
  },
];

const PIPELINE_STEPS = [
  "Intent",
  "Source search",
  "Synthesis",
  "Validation",
] as const;

export function AnswerDemo() {
  const [scenarioIdx, setScenarioIdx] = useState(0);
  const [phase, setPhase] = useState<"idle" | "typing-q" | "pipeline" | "answering" | "settled">("idle");
  const [typedQ, setTypedQ] = useState("");
  const [stepIdx, setStepIdx] = useState(0);
  const [renderedNodes, setRenderedNodes] = useState(0);
  const [openCite, setOpenCite] = useState<number | null>(null);
  const timers = useRef<ReturnType<typeof setTimeout>[]>([]);

  const scenario = SCENARIOS[scenarioIdx];

  const clearTimers = () => {
    timers.current.forEach((t) => clearTimeout(t));
    timers.current = [];
  };

  const schedule = (fn: () => void, ms: number) => {
    const t = setTimeout(fn, ms);
    timers.current.push(t);
  };

  useEffect(() => {
    clearTimers();
    setTypedQ("");
    setStepIdx(0);
    setRenderedNodes(0);
    setOpenCite(null);
    setPhase("typing-q");

    // Type the question
    const q = scenario.question;
    for (let i = 1; i <= q.length; i++) {
      schedule(() => setTypedQ(q.slice(0, i)), 22 * i);
    }
    const qDoneAt = 22 * q.length + 280;

    // Pipeline steps
    schedule(() => {
      setPhase("pipeline");
      setStepIdx(0);
    }, qDoneAt);
    PIPELINE_STEPS.forEach((_, i) => {
      schedule(() => setStepIdx(i + 1), qDoneAt + 480 * (i + 1));
    });
    const pipeDoneAt = qDoneAt + 480 * PIPELINE_STEPS.length + 200;

    // Reveal answer node-by-node
    schedule(() => setPhase("answering"), pipeDoneAt);
    const total = scenario.answer.length;
    for (let i = 1; i <= total; i++) {
      schedule(() => setRenderedNodes(i), pipeDoneAt + 90 * i);
    }
    const answerDoneAt = pipeDoneAt + 90 * total + 600;

    // Auto-open the first citation to teach the interaction
    schedule(() => setOpenCite(1), answerDoneAt);

    schedule(() => setPhase("settled"), answerDoneAt + 200);

    // Cycle to next scenario after dwell
    schedule(() => {
      setScenarioIdx((idx) => (idx + 1) % SCENARIOS.length);
    }, answerDoneAt + 7800);

    return clearTimers;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scenarioIdx]);

  const activeCitation = useMemo(
    () => scenario.citations.find((c) => c.id === openCite) ?? null,
    [scenario, openCite]
  );

  return (
    <div className="askcard">
      <div className="askcard-bar">
        <span className={`askcard-dot ${phase !== "idle" ? "is-on" : ""}`} />
        <span>comask · research session</span>
        <span className="askcard-jur">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 1 1 18 0z" />
            <circle cx="12" cy="10" r="3" />
          </svg>
          Colorado
        </span>
      </div>

      <div className="askcard-q">
        <span className="q-prompt">{">"}</span>
        <span>{typedQ}</span>
        {phase === "typing-q" && <span className="q-cursor" />}
      </div>

      <div className="askcard-pipe">
        {PIPELINE_STEPS.map((s, i) => {
          const cls =
            i < stepIdx ? "pipe-step is-done" : i === stepIdx && phase === "pipeline" ? "pipe-step is-active" : "pipe-step";
          return (
            <span key={s} className={cls}>
              {s}
            </span>
          );
        })}
      </div>

      <div className="askcard-ans">
        {phase === "answering" || phase === "settled" ? (
          <>
            {scenario.answer.slice(0, renderedNodes).map((node, i) => {
              if (node.kind === "br") return <br key={i} />;
              if (node.kind === "text") return <span key={i}>{node.text}</span>;
              const cite = scenario.citations.find((c) => c.id === node.cite);
              return (
                <span key={i}>
                  <span className="cite-anchor">{node.text}</span>
                  <button
                    type="button"
                    className="cite-badge"
                    onClick={() => setOpenCite(openCite === node.cite ? null : node.cite)}
                    aria-label={`Citation ${node.cite}: ${cite?.shortId ?? ""}`}
                  >
                    <span className="cite-num">{node.cite}</span>
                    {cite?.shortId}
                  </button>
                </span>
              );
            })}
            {phase === "answering" && renderedNodes < scenario.answer.length && (
              <span className="ans-cursor" />
            )}
            {activeCitation && (
              <div className="cite-drawer" key={activeCitation.id}>
                <div className="cite-drawer-head">
                  <span>
                    Source <span className="cite-drawer-id">{activeCitation.shortId}</span>
                  </span>
                  <button type="button" onClick={() => setOpenCite(null)} aria-label="Close source">
                    ✕
                  </button>
                </div>
                <div className="cite-drawer-quote">&ldquo;{activeCitation.excerpt}&rdquo;</div>
                <div className="cite-drawer-meta">
                  <span>{activeCitation.authority}</span>
                  <span>·</span>
                  <span>{activeCitation.jurisdiction}</span>
                  <span>·</span>
                  <span>{activeCitation.effective}</span>
                </div>
              </div>
            )}
          </>
        ) : (
          <span className="muted" style={{ fontSize: 13, fontFamily: "var(--f-mono)" }}>
            awaiting validated sources…
          </span>
        )}
      </div>

      <div className="askcard-foot">
        <span>
          {scenario.citations.length} citations · {scenario.sourcesFound} sources matched
        </span>
        <span>·</span>
        <span>
          confidence <span className="conf-high">{scenario.confidence}</span>
        </span>
        <span>·</span>
        <span>{scenario.elapsed}</span>
        <span style={{ marginLeft: "auto", display: "inline-flex", gap: 6 }}>
          {SCENARIOS.map((_, i) => (
            <span
              key={i}
              style={{
                width: 14,
                height: 2,
                background: i === scenarioIdx ? "var(--accent)" : "var(--ink-faint)",
                borderRadius: 1,
                transition: "background 200ms ease",
              }}
            />
          ))}
        </span>
      </div>
    </div>
  );
}
