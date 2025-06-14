import { registerInstrumentations } from '@opentelemetry/instrumentation';
import { FetchInstrumentation } from '@opentelemetry/instrumentation-fetch';
import { XMLHttpRequestInstrumentation } from '@opentelemetry/instrumentation-xml-http-request';
import { DocumentLoadInstrumentation } from '@opentelemetry/instrumentation-document-load';

/**
 * Register auto-instrumentations to capture common browser events:
 * - Fetch API calls
 * - XHR requests
 * - Document load lifecycle
 * These generate spans without manual instrumentation in app code.
 */
export const registerAutoInstrumentations = () => {
  registerInstrumentations({
    instrumentations: [
      new FetchInstrumentation({
        ignoreUrls: [/localhost:3000\/sockjs-node/], // skip dev-tools noise
        propagateTraceHeaderCorsUrls: [/.+/], // forward trace headers universally
      }),
      new XMLHttpRequestInstrumentation(),
      new DocumentLoadInstrumentation(),
    ],
  });
};
