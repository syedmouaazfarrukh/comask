type Source = {
  tier: "federal" | "state" | "region";
  tag: string;
  name: string;
  blurb: string;
  count: string;
};

const SOURCES: Source[] = [
  {
    tier: "federal",
    tag: "Federal · eCFR",
    name: "Title 18 (FERC)",
    blurb: "Federal Energy Regulatory Commission rules — transmission, wholesale markets, hydro licensing.",
    count: "Indexed",
  },
  {
    tier: "federal",
    tag: "Federal · eCFR",
    name: "Title 40 (EPA)",
    blurb: "Environmental rules touching electric generation — emissions, reporting, criteria pollutants.",
    count: "Indexed",
  },
  {
    tier: "federal",
    tag: "Federal Register",
    name: "FERC · EPA · DOE rulemakings",
    blurb: "Live notices and final rules from the agencies that move the goalposts on energy compliance.",
    count: "53 documents",
  },
  {
    tier: "state",
    tag: "Colorado · statute",
    name: "CRS Title 40",
    blurb: "Colorado Revised Statutes for utilities — RES, IRP, rate-making, GHG targets.",
    count: "Full title",
  },
  {
    tier: "state",
    tag: "Colorado · regulation",
    name: "4 CCR 723",
    blurb: "Colorado PUC rules — net metering, interconnection, compliance filings, ERPs.",
    count: "Full chapter",
  },
  {
    tier: "state",
    tag: "Colorado · PUC",
    name: "Commission decisions",
    blurb: "Recent PUC orders that interpret the rules in practice — what regulators are actually accepting.",
    count: "Live ingest",
  },
  {
    tier: "region",
    tag: "Regional",
    name: "NERC reliability standards",
    blurb: "BES reliability standards — the operating spine federal regulators enforce nationwide.",
    count: "Indexed",
  },
  {
    tier: "region",
    tag: "Regional · roadmap",
    name: "WECC, SPP, Xcel tariffs",
    blurb: "Regional reliability and utility tariffs — expanding alongside Texas and other state buildouts.",
    count: "On roadmap",
  },
];

export function Coverage() {
  return (
    <section id="coverage" className="section-pad" style={{ borderTop: "1px solid var(--bd)" }}>
      <div className="container">
        <div className="section-head">
          <p className="kicker">Coverage</p>
          <h2 className="display-lg">
            The authorities Comask reads,
            <br />
            <span className="accent">so you don&rsquo;t skim them.</span>
          </h2>
          <p>
            We don&rsquo;t train on Reddit threads. The corpus is exclusively
            primary sources — federal regulations, state statutes, commission
            decisions, reliability standards. Authority level is preserved on
            every chunk so the system knows what binds and what guides.
          </p>
        </div>

        <div className="grid-4">
          {SOURCES.map((s) => (
            <div key={s.name} className={`cov-card ${s.tier}`}>
              <span className="cov-stripe" />
              <span className="cov-tag">{s.tag}</span>
              <span className="cov-name">{s.name}</span>
              <span className="cov-blurb">{s.blurb}</span>
              <span className="cov-count">{s.count}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
