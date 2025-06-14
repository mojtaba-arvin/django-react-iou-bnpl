import React, { ReactNode } from "react";

// 1- Stub react-admin before anything else
jest.mock("react-admin", () => ({
  Admin: ({ children }: { children: ReactNode }) => (
    <div data-testid="stub-admin">{children}</div>
  ),
  Resource: ({ name }: { name: string }) => (
    <div data-testid={`stub-resource-${name}`}>Resource:{name}</div>
  ),
  CustomRoutes: ({ children }: { children: ReactNode }) => (
    <div data-testid="stub-custom-routes">{children}</div>
  ),
}));

// 2- Stub Route so it just returns its element (avoiding needing <Routes>)
jest.mock("react-router-dom", () => {
  const actual = jest.requireActual("react-router-dom");
  return {
    ...actual,
    Route: ({ element }: { element: ReactNode }) => <>{element}</>,
  };
});

import { render, screen } from "@testing-library/react";
import { createTheme } from "@mui/material";
import { MemoryRouter } from "react-router-dom";

import { AdminApp } from "../admin-app.component";
import type { AdminAppProps } from "../../../infrastructure/admin/config/admin-app.config";
import type { DataProvider } from "react-admin";

// ——— mocks ————————————————————————————————————————————————
const mockResource = {
  name: "users",
  list: () => <div>List</div>,
};

const mockCustomRoute = {
  path: "/custom",
  element: () => <div>Custom Page</div>,
};

const dataProvider = {
  getList: jest.fn(() => Promise.resolve({ data: [], total: 0 })),
  getOne: jest.fn(() => Promise.resolve({ data: {} })),
  getMany: jest.fn(() => Promise.resolve({ data: [] })),
  getManyReference: jest.fn(() => Promise.resolve({ data: [], total: 0 })),
  create: jest.fn(() => Promise.resolve({ data: {} })),
  update: jest.fn(() => Promise.resolve({ data: {} })),
  updateMany: jest.fn(() => Promise.resolve({ data: [] })),
  delete: jest.fn(() => Promise.resolve({ data: {} })),
  deleteMany: jest.fn(() => Promise.resolve({ data: [] })),
} as unknown as DataProvider;

const props: AdminAppProps = {
  theme: createTheme(),
  basename: "/admin",
  authProvider: {
    login: () => Promise.resolve(),
    logout: () => Promise.resolve(),
    checkAuth: () => Promise.resolve(),
    checkError: () => Promise.resolve(),
    getPermissions: () => Promise.resolve(),
  },
  dataProvider,
  loginPage: () => <div>Login</div>,
  dashboard: () => <div>Dashboard</div>,
  catchAll: () => <div>Not Found</div>,
  resources: [mockResource],
  customRoutes: [mockCustomRoute],
};

// ——— tests ————————————————————————————————————————————————
describe("AdminApp", () => {
  beforeEach(() => {
    render(
      <MemoryRouter>
        <AdminApp {...props} />
      </MemoryRouter>
    );
  });

  it("renders the Admin wrapper", () => {
    expect(screen.getByTestId("stub-admin")).toBeInTheDocument();
  });

  it("renders resources with the correct name", () => {
    expect(screen.getByTestId("stub-resource-users")).toHaveTextContent(
      "Resource:users"
    );
  });

  it("renders custom routes", () => {
    expect(screen.getByText("Custom Page")).toBeInTheDocument();
  });
});
