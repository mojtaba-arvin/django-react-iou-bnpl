import { WebTracerProvider } from '@opentelemetry/sdk-trace-web';
import { getResource, getSpanProcessor, getSampler } from './telemetry.config';

/**
 * Initialize the WebTracerProvider with resource metadata, sampling, and span processing.
 * Must be called at the very start of application bootstrap (e.g., index.tsx).
 * Ensures that tracing is resilient and non-blocking in both dev and prod.
 */
export const initializeTracing = () => {
  const provider = new WebTracerProvider({
    resource: getResource('react-admin-frontend'), // custom service metadata
    sampler: getSampler(), // environment-based sampling
    spanProcessors: [getSpanProcessor()], // console or OTLP exporter
  });

  // Register provider globally to patch browser APIs automatically
  provider.register({
    // options: e.g., contextManager: ..., propagator: ...
  });

  return provider;
};
