export function KnowledgeGraph() {
  return (
    <section id="graph" className="section-pad" style={{ borderTop: "1px solid var(--bd)" }}>
      <div className="container">
        <div className="section-head">
          <p className="kicker">Knowledge graph</p>
          <h2 className="display-lg">
            See exactly which authorities
            <br />
            <span className="accent">grounded the answer.</span>
          </h2>
          <p>
            Every response opens onto a graph showing the question, the
            documents that matched, their relevance scores, and how each one
            contributed to the synthesized answer. Click a node, get the
            paragraph. It&rsquo;s the audit trail your filings need.
          </p>
        </div>

        <div className="kg-wrap">
          <svg
            className="kg-svg"
            viewBox="0 0 1000 420"
            xmlns="http://www.w3.org/2000/svg"
            role="img"
            aria-label="Knowledge graph diagram"
          >
            <defs>
              <linearGradient id="edge-fed" x1="0" x2="1">
                <stop offset="0%" stopColor="rgba(34,211,238,0)" />
                <stop offset="50%" stopColor="rgba(129,140,248,0.55)" />
                <stop offset="100%" stopColor="rgba(34,211,238,0)" />
              </linearGradient>
              <linearGradient id="edge-state" x1="0" x2="1">
                <stop offset="0%" stopColor="rgba(34,211,238,0)" />
                <stop offset="50%" stopColor="rgba(52,211,153,0.55)" />
                <stop offset="100%" stopColor="rgba(34,211,238,0)" />
              </linearGradient>
              <linearGradient id="edge-region" x1="0" x2="1">
                <stop offset="0%" stopColor="rgba(34,211,238,0)" />
                <stop offset="50%" stopColor="rgba(244,114,182,0.45)" />
                <stop offset="100%" stopColor="rgba(34,211,238,0)" />
              </linearGradient>
              <radialGradient id="q-glow" cx="0.5" cy="0.5" r="0.5">
                <stop offset="0%" stopColor="rgba(34,211,238,0.45)" />
                <stop offset="100%" stopColor="rgba(34,211,238,0)" />
              </radialGradient>
            </defs>

            {/* Question pill */}
            <ellipse cx="170" cy="210" rx="135" ry="80" fill="url(#q-glow)" />
            <rect x="40" y="180" width="260" height="60" rx="10" fill="#0c1220" stroke="#22d3ee" strokeWidth="1.5" />
            <text x="170" y="210" textAnchor="middle" fill="#f1f5fb" fontFamily="Inter" fontSize="13" fontWeight="600">
              Q: RES requirements for IOUs?
            </text>
            <text x="170" y="228" textAnchor="middle" fill="#7d8597" fontFamily="JetBrains Mono" fontSize="10" letterSpacing="1">
              JURISDICTION = Colorado
            </text>

            {/* Edges */}
            <path d="M 300 210 Q 450 80 580 80" fill="none" stroke="url(#edge-state)" strokeWidth="2" />
            <path d="M 300 210 Q 450 150 580 150" fill="none" stroke="url(#edge-state)" strokeWidth="2" />
            <path d="M 300 210 Q 450 220 580 220" fill="none" stroke="url(#edge-state)" strokeWidth="2" />
            <path d="M 300 210 Q 450 290 580 290" fill="none" stroke="url(#edge-fed)" strokeWidth="2" />
            <path d="M 300 210 Q 450 350 580 350" fill="none" stroke="url(#edge-region)" strokeWidth="1.6" strokeDasharray="3 3" />

            {/* Source nodes */}
            <SourceNode x={580} y={50} title="CRS § 40-2-124" sub="Colorado statute" score="0.95" colorVar="#34d399" primary />
            <SourceNode x={580} y={120} title="4 CCR 723-3-3654" sub="Colorado regulation" score="0.91" colorVar="#34d399" primary />
            <SourceNode x={580} y={190} title="HB 19-1261" sub="Clean Energy Plan" score="0.87" colorVar="#34d399" primary />
            <SourceNode x={580} y={260} title="FERC Order 888" sub="Federal · transmission" score="0.62" colorVar="#818cf8" />
            <SourceNode x={580} y={330} title="NERC TPL-001-5" sub="Reliability standard" score="0.41" colorVar="#f472b6" dim />

            {/* Synthesis node */}
            <path d="M 800 90 Q 880 90 880 210 Q 880 330 800 330" fill="none" stroke="rgba(34,211,238,0.20)" strokeWidth="1.4" strokeDasharray="2 4" />
            <rect x="830" y="180" width="140" height="60" rx="10" fill="#0c1220" stroke="#22d3ee" strokeWidth="1.5" />
            <text x="900" y="206" textAnchor="middle" fill="#f1f5fb" fontFamily="Inter" fontSize="13" fontWeight="700">
              Validated answer
            </text>
            <text x="900" y="224" textAnchor="middle" fill="#22d3ee" fontFamily="JetBrains Mono" fontSize="10" letterSpacing="1">
              3 INLINE CITES
            </text>
          </svg>

          <div style={{ display: "flex", gap: 18, flexWrap: "wrap", marginTop: 18, fontFamily: "var(--f-mono)", fontSize: 11, color: "var(--ink-muted)", letterSpacing: "0.06em" }}>
            <LegendDot color="var(--auth-state)" label="Colorado · state" />
            <LegendDot color="var(--auth-federal)" label="Federal · eCFR / FERC" />
            <LegendDot color="var(--auth-region)" label="Regional · NERC / WECC" />
            <span style={{ marginLeft: "auto" }}>Edge thickness = relevance score</span>
          </div>
        </div>
      </div>
    </section>
  );
}

function SourceNode({
  x,
  y,
  title,
  sub,
  score,
  colorVar,
  primary,
  dim,
}: {
  x: number;
  y: number;
  title: string;
  sub: string;
  score: string;
  colorVar: string;
  primary?: boolean;
  dim?: boolean;
}) {
  const w = 200;
  const h = 50;
  return (
    <g opacity={dim ? 0.55 : 1}>
      <rect
        x={x}
        y={y - h / 2}
        width={w}
        height={h}
        rx="8"
        fill="#11182a"
        stroke={colorVar}
        strokeWidth={primary ? 1.5 : 1}
      />
      <circle cx={x + 12} cy={y} r="3.5" fill={colorVar} />
      <text x={x + 24} y={y - 4} fill="#f1f5fb" fontFamily="Inter" fontSize="13" fontWeight="600">
        {title}
      </text>
      <text x={x + 24} y={y + 12} fill="#7d8597" fontFamily="JetBrains Mono" fontSize="10" letterSpacing="0.5">
        {sub}
      </text>
      <text x={x + w - 12} y={y + 4} textAnchor="end" fill={colorVar} fontFamily="JetBrains Mono" fontSize="11" fontWeight="700">
        {score}
      </text>
    </g>
  );
}

function LegendDot({ color, label }: { color: string; label: string }) {
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
      <span style={{ width: 8, height: 8, borderRadius: 2, background: color }} />
      {label}
    </span>
  );
}
