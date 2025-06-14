import React from "react";
import { render } from "@testing-library/react";
import { StandaloneAppBootstrap } from "../standalone-app.bootstrap";
import type {
  AdminAppProps,
  ResourceConfig,
} from "../../admin/config/admin-app.config";
import type { AuthProvider, DataProvider } from "react-admin";
import { createTheme } from "@mui/material";

describe("StandaloneAppBootstrap", () => {
  // Mock auth provider
  const mockAuthProvider: AuthProvider = {
    login: jest.fn().mockResolvedValue(undefined),
    logout: jest.fn().mockResolvedValue(undefined),
    checkAuth: jest.fn().mockResolvedValue(undefined),
    checkError: jest.fn().mockResolvedValue(undefined),
    getPermissions: jest.fn().mockResolvedValue(undefined),
  };

  // Mock data provider
  const mockDataProvider: DataProvider = {
    getList: jest.fn().mockResolvedValue({ data: [], total: 0 }),
    getOne: jest.fn().mockResolvedValue({ data: {} }),
    getMany: jest.fn().mockResolvedValue({ data: [] }),
    getManyReference: jest.fn().mockResolvedValue({ data: [], total: 0 }),
    create: jest.fn().mockResolvedValue({ data: {} }),
    update: jest.fn().mockResolvedValue({ data: {} }),
    updateMany: jest.fn().mockResolvedValue({ data: [] }),
    delete: jest.fn().mockResolvedValue({ data: {} }),
    deleteMany: jest.fn().mockResolvedValue({ data: [] }),
  };

  // Mock login page component
  const MockLoginPage = () => <div>Login</div>;

  // Mock catch-all component
  const MockCatchAll = () => <div>Not Found</div>;

  // Mock resource config
  const mockResources: ResourceConfig[] = [
    {
      name: "users",
      list: () => <div>User List</div>,
      icon: () => <span>👤</span>,
    },
  ];

  const mockCreateAdminAppConfig = jest.fn(
    (): AdminAppProps => ({
      basename: "/test",
      resources: mockResources,
      authProvider: mockAuthProvider,
      dataProvider: mockDataProvider,
      loginPage: MockLoginPage,
      catchAll: MockCatchAll,
      theme: createTheme(),
    })
  );

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should render without crashing", () => {
    const { container } = render(
      <StandaloneAppBootstrap
        createAdminAppConfig={mockCreateAdminAppConfig}
      />
    );
    expect(container).toBeInTheDocument();
  });

  it("should call createAdminAppConfig with correct parameters", () => {
    const basename = "/test";

    // Simulate the correct URL for the basename
    window.history.pushState({}, "Test page", "/test");

    render(
      <StandaloneAppBootstrap
        createAdminAppConfig={mockCreateAdminAppConfig}
        basename={basename}
      />
    );

    expect(mockCreateAdminAppConfig).toHaveBeenCalledWith({
      onBack: expect.any(Function),
      basename,
    });
  });

  it("should pass all required props to AdminApp", () => {
    const basename = "/test";
    render(
      <StandaloneAppBootstrap
        createAdminAppConfig={mockCreateAdminAppConfig}
        basename={basename}
      />
    );

    const adminAppProps = mockCreateAdminAppConfig.mock.results[0].value;
    expect(adminAppProps).toMatchObject({
      basename: expect.any(String),
      resources: expect.any(Array),
      authProvider: expect.objectContaining({
        login: expect.any(Function),
        logout: expect.any(Function),
        checkAuth: expect.any(Function),
      }),
      dataProvider: expect.objectContaining({
        getList: expect.any(Function),
        create: expect.any(Function),
        update: expect.any(Function),
      }),
      loginPage: expect.any(Function),
      catchAll: expect.any(Function),
    });
  });
});
