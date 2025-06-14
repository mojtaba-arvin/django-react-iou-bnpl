// ─── Infrastructure / context ───────────────────
export {
  useGlobalSettings,
  getGlobalSettings,
  GlobalSettingsProvider,
} from './infrastructure/context/global-settings.context';

// ─── Infrastructure / telemetry ─────────────────
export {
  logger,
  type LogContext,
} from './infrastructure/telemetry/logger.util';
export { registerAutoInstrumentations } from './infrastructure/telemetry/instrumentations.util';
export { initializeTracing } from './infrastructure/telemetry/telemetry.provider';

// ─── Infrastructure / react-admin ───────────────
export type * from './infrastructure/admin/config/admin-app.config';
export { dataProvider } from './infrastructure/data/provider/data-provider';

// ─── Infrastructure / bootstrap ───────────────
export * from './infrastructure/standalone/standalone-app.bootstrap';

// ─── Domain ─────────────────────────────────────
export type * from './domain/plan/entities/plan.entity';
export type * from './domain/installment/entities/installment.entities';
export type * from './domain/dashboard/value-objects/dashboard.vo';

// ─── Application ────────────────────────────────
export type * from './application/installment/dtos/installment.dtos';

// ─── Presentation / Components ──────────────────
export { ErrorBoundary } from './presentation/components/error-boundary.component';
export { AdminApp } from './presentation/components/admin-app.component';
export { PublicLayout } from './presentation/components/public-layout.component';
export { FormattedDateTimeField } from './presentation/components/formatted-date-time-field.component';

// ─── Presentation / Pages ───────────────────────
export * from './presentation/pages/login.page';
export * from './presentation/pages/register.page';

// ─── Presentation / Admin Resources ─────────────
export { PlanList } from './presentation/admin-resources/plans/plan-list.component';
export { PlanShow } from './presentation/admin-resources/plans/plan-show.component';

// ─── Utils ───────────────────────────────────────
export { createAdminAppConfig } from './utils/create-admin-app-config.util';
export { calculateInstallments } from './utils/calculate-installments.util';
