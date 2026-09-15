export function Header() {
  return (
    <header className="app-header">
      <div className="header-inner">
        <div className="brand-lockup"><div className="brand-mark" aria-hidden="true">IG</div><div><h1>IntakeGuard</h1><p>Enterprise Intake Control</p></div></div>
        <div className="header-status"><span className="operational-dot" aria-hidden="true" /><div><small>Guardrail Engine</small><strong>Operational</strong></div></div>
        <div className="header-meta"><span>Deterministic</span><span>No data retained</span></div>
      </div>
    </header>
  );
}
