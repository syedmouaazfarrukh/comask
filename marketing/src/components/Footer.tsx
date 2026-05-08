import { APP_URL } from "@/lib/links";

export function Footer() {
  return (
    <footer className="footer">
      <div className="container footer-row">
        <div className="footer-brand">
          <span className="appbar-mark" style={{ width: 24, height: 24, fontSize: 12 }}>C</span>
          <span className="footer-word">comask</span>
          <span className="footer-tag muted">// citation engine for energy compliance</span>
        </div>
        <div className="footer-links">
          <a href="#difference">The difference</a>
          <a href="#demo">Live answer</a>
          <a href="#coverage">Coverage</a>
          <a href="#use-cases">Use cases</a>
          <a href={APP_URL} target="_blank" rel="noreferrer">App</a>
        </div>
        <div className="footer-meta muted">
          © {new Date().getFullYear()} Comask · DashGen Solutions
        </div>
      </div>
    </footer>
  );
}
