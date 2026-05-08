import { APP_URL, DEMO_URL } from "@/lib/links";

export function AppBar() {
  return (
    <header className="appbar">
      <div className="container appbar-row">
        <a href="#top" className="appbar-brand">
          <span className="appbar-mark">C</span>
          <span className="word-mark">
            com<span className="accent-letter">ask</span>
          </span>
        </a>
        <nav className="appbar-nav">
          <a href="#difference">The difference</a>
          <a href="#demo">Live answer</a>
          <a href="#coverage">Coverage</a>
          <a href="#use-cases">Use cases</a>
          <a href={APP_URL} target="_blank" rel="noreferrer" className="btn btn-line btn-sm">
            Open app →
          </a>
        </nav>
      </div>
    </header>
  );
}
