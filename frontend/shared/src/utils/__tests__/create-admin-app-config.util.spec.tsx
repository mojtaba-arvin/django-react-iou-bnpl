import { createAdminAppConfig } from "../create-admin-app-config.util";
import { authProvider } from "../../infrastructure/auth/provider/auth.provider";
import { lightTheme } from "../../presentation/themes/light.theme";
import { AdminError } from "../../presentation/components/admin-error.component";
import type {
  AdminAppOptions,
  AdminCustomRoute,
} from "../../infrastructure/admin/config/admin-app.config";
import type { Theme } from "@mui/material/styles";

// Mock dependencies
jest.mock("../../infrastructure/telemetry/logger.util");
jest.mock("../../infrastructure/auth/provider/auth.provider");
jest.mock("../../infrastructure/data/provider/data-provider", () => ({
  dataProvider: jest.fn(),
}));
jest.mock("../../infrastructure/telemetry/data-provider-logger.util", () => ({
  wrapDataProviderWithLogging: jest.fn((provider) => provider),
}));
jest.mock("../../infrastructure/context/global-settings.context", () => ({
  getGlobalSettings: jest.fn(() => ({
    apiBaseUrl: "http://api.example.com",
    loginPath: "/login",
    registerPath: "/register",
  })),
}));
jest.mock("../../presentation/pages/login.page", () => ({
  createLoginPage: jest.fn(() => () => <div>Login</div>),
}));
jest.mock("../../presentation/pages/register.page", () => ({
  createRegisterPage: jest.fn(() => () => <div>Register</div>),
}));

describe("createAdminAppConfig", () => {
  const baseOptions: AdminAppOptions = {
    userType: "customer",
    onBack: jest.fn(),
    resources: [],
  };

  const mockCustomRoute: AdminCustomRoute = {
    path: "/hey",
    element: () => <div>hey</div>,
  };

  const mockTheme: Theme = {
    ...lightTheme,
    palette: {
      ...lightTheme.palette,
      primary: {
        ...lightTheme.palette.primary,
        main: "#ff0000",
      },
    },
  } as Theme;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should return basic admin configuration structure", () => {
    const result = createAdminAppConfig(baseOptions);

    expect(result).toEqual({
      basename: "",
      authProvider: expect.anything(),
      dataProvider: expect.anything(),
      loginPage: expect.anything(),
      catchAll: AdminError,
      theme: lightTheme,
      dashboard: undefined,
      resources: [],
      customRoutes: expect.arrayContaining([
        expect.objectContaining({ path: "/register" }),
      ]),
    });
  });

  it("should configure auth provider with correct paths and user type", () => {
    createAdminAppConfig({
      ...baseOptions,
      basename: "/admin",
      userType: "customer",
    });

    expect(authProvider.configure).toHaveBeenCalledWith({
      loginPath: "/admin/login",
      registerPath: "/admin/register",
      expectedUserType: "customer",
    });
  });

  it("should use custom theme when provided", () => {
    const result = createAdminAppConfig({ ...baseOptions, theme: mockTheme });
    expect(result.theme).toBe(mockTheme);
  });

  it("should include dashboard when provided", () => {
    const mockDashboard = () => <div>Dashboard</div>;
    const result = createAdminAppConfig({
      ...baseOptions,
      dashboard: mockDashboard,
    });
    expect(result.dashboard).toBe(mockDashboard);
  });

  it("should include resources when provided", () => {
    const mockResources = [{ name: "users" }];
    const result = createAdminAppConfig({
      ...baseOptions,
      resources: mockResources,
    });
    expect(result.resources).toBe(mockResources);
  });

  it("should merge custom routes with register route", () => {
    const result = createAdminAppConfig({
      ...baseOptions,
      customRoutes: [mockCustomRoute],
    });

    expect(result.customRoutes).toHaveLength(2);
    expect(result.customRoutes).toContainEqual(mockCustomRoute);
    expect(result.customRoutes).toContainEqual(
      expect.objectContaining({ path: "/register" })
    );
  });
});
