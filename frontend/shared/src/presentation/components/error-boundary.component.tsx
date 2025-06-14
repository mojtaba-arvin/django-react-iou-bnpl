import React from 'react';
import { logger } from '../../infrastructure/telemetry/logger.util';

interface ErrorBoundaryState {
  hasError: boolean;
}

export class ErrorBoundary extends React.Component<
  {
    children: React.ReactNode;
  },
  ErrorBoundaryState
> {
  state: ErrorBoundaryState = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    // Ensure componentStack is a string
    const stack = info.componentStack || '';
    logger.error(error, { componentStack: stack });
  }

  render() {
    if (this.state.hasError) {
      return <div>Application loading failed</div>;
    }
    return this.props.children;
  }
}
