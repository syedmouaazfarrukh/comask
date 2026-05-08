export function CitationDifference() {
  return (
    <section id="difference" className="section-pad" style={{ borderTop: "1px solid var(--bd)" }}>
      <div className="container">
        <div className="section-head">
          <p className="kicker">The difference</p>
          <h2 className="display-lg">
            Most AI gives you a paragraph.
            <br />
            <span className="accent">We give you the rule.</span>
          </h2>
          <p>
            A retrieval-augmented chatbot stitches plausible-sounding text from
            whatever it found. That&rsquo;s not compliance. Comask works the
            other direction — every claim must trace to a specific clause in a
            specific document, or it doesn&rsquo;t ship.
          </p>
        </div>

        <div className="compare">
          <div className="compare-col">
            <span className="compare-label">Generic RAG chatbot</span>
            <h3 className="compare-title">A paragraph that sounds right</h3>
            <div className="compare-snippet">
              Colorado utilities are required to source a significant portion of
              their electricity from renewable energy under state law. The
              standard has been updated multiple times and applies broadly to
              investor-owned utilities operating in the state.
            </div>
            <ul className="compare-list">
              <li><span className="mark">×</span><span>No statute number. You verify it yourself.</span></li>
              <li><span className="mark">×</span><span>Hedged phrasing — &ldquo;significant&rdquo;, &ldquo;broadly&rdquo;.</span></li>
              <li><span className="mark">×</span><span>If a clause was repealed last quarter, it won&rsquo;t know.</span></li>
              <li><span className="mark">×</span><span>Confidence is an opinion, not a count of matches.</span></li>
            </ul>
          </div>

          <div className="compare-divider" aria-hidden />

          <div className="compare-col">
            <span className="compare-label is-accent">Comask</span>
            <h3 className="compare-title">A claim, pinned to a clause</h3>
            <div className="compare-snippet">
              IOUs must generate{" "}
              <span className="cite-anchor">30% of retail sales from renewables by 2020</span>{" "}
              <span className="cite-badge"><span className="cite-num">1</span>CRS § 40-2-124</span>,
              scaling to{" "}
              <span className="cite-anchor">100% clean energy by 2040</span>{" "}
              <span className="cite-badge"><span className="cite-num">2</span>HB 19-1261</span>.
              Annual filings per{" "}
              <span className="cite-badge"><span className="cite-num">3</span>4 CCR 723-3-3654</span>.
            </div>
            <ul className="compare-list">
              <li><span className="mark is-good">✓</span><span>Every fact is a click away from the source paragraph.</span></li>
              <li><span className="mark is-good">✓</span><span>Validation agent rejects claims with no matching excerpt.</span></li>
              <li><span className="mark is-good">✓</span><span>Effective dates surfaced — knows what&rsquo;s live today.</span></li>
              <li><span className="mark is-good">✓</span><span>Confidence is a count of authoritative matches, not vibes.</span></li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
