import {
  trace,
  context,
  SpanStatusCode,
  Attributes,
} from '@opentelemetry/api';

/**
 * LogContext defines the shape of key-value pairs for log metadata.
 * Must align with Attributes to attach to spans.
 */
export type LogContext = Attributes;

/**
 * A logger that writes structured events to the active span and falls back to console.
 * - info: attaches a span event
 * - error: starts a child span for error, records exception, and marks span status
 */
export const logger = {
  info: (message: string, contextAttrs: LogContext = {}) => {
    // Retrieve the current active span from context
    const span = trace.getSpan(context.active());
    // Add a structured event to the span
    span?.addEvent('log.info', { message, ...contextAttrs });
    // Console fallback for visibility if tracing isn't configured
    console.log(`[INFO] ${message}`, contextAttrs);
  },

  error: (error: Error, contextAttrs: LogContext = {}) => {
    // Create a dedicated span for error handling
    const tracer = trace.getTracer('react-app-error');
    tracer.startActiveSpan('app.error', (span) => {
      span.recordException(error); // Attach exception detail
      span.setAttributes(contextAttrs); // Add user-provided context
      span.setStatus({ code: SpanStatusCode.ERROR }); // Mark span as error
      span.end(); // Ensure span closes promptly
    });
    // Always log to console as fallback
    console.error('[ERROR]', error, contextAttrs);
  },
};
