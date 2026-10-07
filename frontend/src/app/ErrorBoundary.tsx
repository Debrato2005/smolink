import { Component, type ReactNode } from 'react';

export class ErrorBoundary extends Component<
  { children: ReactNode },
  { failed: boolean }
> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    if (this.state.failed)
      return (
        <main className="unavailable">
          <h1>The page could not load.</h1>
          <p role="alert">Reload the page to try again.</p>
          <a href="/" className="button-link">
            Reload Smolink
          </a>
        </main>
      );
    return this.props.children;
  }
}
