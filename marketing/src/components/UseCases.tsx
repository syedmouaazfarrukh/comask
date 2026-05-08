type UseCase = {
  q: string;
  blurb: string;
  tags: string[];
};

const USE_CASES: UseCase[] = [
  {
    q: "Are co-ops exempt from Colorado&rsquo;s RES?",
    blurb:
      "Get a yes/no answer pinned to the carve-out language — no scrolling through 80 pages of statute to find it.",
    tags: ["RES", "CRS § 40-2-124", "Carve-outs"],
  },
  {
    q: "When must we file the next ERP?",
    blurb:
      "Comask reads the cadence rule directly and surfaces the rolling deadline based on your last filing.",
    tags: ["IRP / ERP", "4 CCR 723-3-3603", "Deadlines"],
  },
  {
    q: "What counts as a Qualifying Facility under PURPA?",
    blurb:
      "Definitions answer with the precise statutory thresholds and the FERC orders that interpret them.",
    tags: ["PURPA", "FERC Order 671", "Definitions"],
  },
  {
    q: "What are the penalties for RES non-compliance?",
    blurb:
      "Penalty structure pulled from statute and PUC rule — including the conditions that trigger each tier.",
    tags: ["Enforcement", "Penalties", "PUC rule"],
  },
  {
    q: "How does a rate case proceed at the CPUC?",
    blurb:
      "Process questions return the actual procedural rule — what gets filed, when, and what the Commission must do.",
    tags: ["Procedure", "Rate cases", "PUC rules"],
  },
  {
    q: "How do IOU and muni RES requirements differ?",
    blurb:
      "Side-by-side answers from a single statute section, with each utility class&rsquo;s threshold called out distinctly.",
    tags: ["Comparisons", "Utilities", "Standards"],
  },
];

export function UseCases() {
  return (
    <section id="use-cases" className="section-pad" style={{ borderTop: "1px solid var(--bd)" }}>
      <div className="container">
        <div className="section-head">
          <p className="kicker">What people ask it</p>
          <h2 className="display-lg">
            The questions energy teams
            <br />
            <span className="accent">stop dreading.</span>
          </h2>
          <p>
            Each question routes through the same pipeline — intent, source
            search, synthesis, validation — and lands on a cited answer with
            the regulation excerpts attached.
          </p>
        </div>

        <div className="grid-3">
          {USE_CASES.map((u) => (
            <div key={u.q} className="use-card">
              <div className="use-q" dangerouslySetInnerHTML={{ __html: u.q }} />
              <p className="use-blurb">{u.blurb}</p>
              <div className="use-tags">
                {u.tags.map((t) => (
                  <span key={t} className="use-tag">{t}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
