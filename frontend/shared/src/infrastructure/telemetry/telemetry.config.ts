import {
  // Core span processors and exporters for handling trace data
  BatchSpanProcessor,
  ConsoleSpanExporter,
  SimpleSpanProcessor,
  ParentBasedSampler,
  TraceIdRatioBasedSampler,
} from '@opentelemetry/sdk-trace-base';

import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';

import {
  // Resource helpers to define service metadata
  defaultResource,
  resourceFromAttributes,
} from '@opentelemetry/resources';
import {
  // Standardized attribute keys for service identification
  ATTR_SERVICE_NAME,
  ATTR_SERVICE_VERSION,
} from '@opentelemetry/semantic-conventions';
import { getGlobalSettings } from '../context/global-settings.context';

const { nodeEnv, telemetryExporterUrl } = getGlobalSettings();

// Determine if the environment is development for conditional setup
const isDevelopment = nodeEnv === 'development';

/**
 * Build and merge default resource information with custom attributes.
 * @param serviceName - Unique name of the service (e.g., frontend app name)
 * @returns A merged Resource containing host, OS, process info + custom metadata
 */
export const getResource = (serviceName: string) => {
  // defaultResource includes auto-detected environment info
  const baseResource = defaultResource();
  // Add custom attributes: service name, version, and custom type
  const customResource = resourceFromAttributes({
    [ATTR_SERVICE_NAME]: serviceName,
    [ATTR_SERVICE_VERSION]: '1.0',
    'mf.type': 'remote',
  });
  // Merge ensures both default and custom info are combined
  return baseResource.merge(customResource);
};

/**
 * Choose a SpanProcessor based on the environment.
 * - Development: SimpleConsoleExporter for debugging in console
 * - Production: BatchSpanProcessor sending to OTLP collector
 */
export const getSpanProcessor = () => {
  if (isDevelopment || !telemetryExporterUrl) {
    // Simple processor writes spans immediately to console
    return new SimpleSpanProcessor(new ConsoleSpanExporter());
  }
  // Batch processor groups and sends spans in batches to reduce overhead
  return new BatchSpanProcessor(
    new OTLPTraceExporter({
      url: telemetryExporterUrl,
      // You can add headers or credentials here if needed
    })
  );
};

/**
 * Configure sampling strategy based on environment.
 * - Development: sample all traces for maximum visibility
 * - Production: sample a fraction (e.g., 10%) to reduce data volume
 */
export const getSampler = () =>
  isDevelopment
    ? new ParentBasedSampler({ root: new TraceIdRatioBasedSampler(1.0) })
    : new ParentBasedSampler({ root: new TraceIdRatioBasedSampler(0.1) });
