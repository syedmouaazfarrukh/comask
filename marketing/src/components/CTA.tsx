import { APP_URL, DEMO_URL } from "@/lib/links";

export function CTA() {
  return (
    <section className="cta-sec section-pad">
      <div className="container">
        <div className="cta-card">
          <p className="kicker-accent">// Get access</p>
          <h2 className="display-lg mt-3">
            Ship filings with{" "}
            <span className="accent">citations attached.</span>
          </h2>
          <p
            className="body-lg muted mt-4"
            style={{ maxWidth: 620, margin: "16px auto 0" }}
          >
            Currently live for Colorado and Texas energy compliance. Federal
            coverage included. Reach out for an early-access demo or open the
            app if you already have credentials.
          </p>
          <div
            className="hero-cta"
            style={{ justifyContent: "center", marginTop: 28 }}
          >
            <a href={DEMO_URL} className="btn btn-solid btn-lg">
              Request a demo →
            </a>
            <a
              href={APP_URL}
              target="_blank"
              rel="noreferrer"
              className="btn btn-line btn-lg"
            >
              Open the app
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
