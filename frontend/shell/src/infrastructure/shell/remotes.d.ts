declare module "customer_app/createAdminAppConfig" {
  const createAdminAppConfig: (
    options: import("@bnpl/shared").RemoteAppSetup
  ) => import("@bnpl/shared").AdminAppProps;
  export default createAdminAppConfig;
}

declare module "merchant_app/createAdminAppConfig" {
  const createAdminAppConfig: (
    options: import("@bnpl/shared").RemoteAppSetup
  ) => import("@bnpl/shared").AdminAppProps;
  export default createAdminAppConfig;
}
