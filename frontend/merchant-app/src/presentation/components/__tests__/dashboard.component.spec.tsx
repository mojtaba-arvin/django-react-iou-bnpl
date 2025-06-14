import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { Dashboard } from "../dashboard.component";
import { AdminContext } from "react-admin";

const mockDataProvider = {
  getList: jest.fn().mockResolvedValue({ data: [], total: 0 }),
  getOne: jest.fn().mockResolvedValue({ data: { id: 1 } }),
  getMany: jest.fn().mockResolvedValue({ data: [] }),
  getManyReference: jest.fn().mockResolvedValue({ data: [], total: 0 }),
  create: jest.fn().mockResolvedValue({ data: {} }),
  update: jest.fn().mockResolvedValue({ data: {} }),
  updateMany: jest.fn().mockResolvedValue({ data: [] }),
  delete: jest.fn().mockResolvedValue({ data: {} }),
  deleteMany: jest.fn().mockResolvedValue({ data: [] }),
  getDashboardMetrics: jest.fn().mockResolvedValue({
    data: {
      total_revenue: 1000.5,
      success_rate: 95,
      overdue_count: 3,
      active_plans: 10,
    },
  }),
};

describe("Dashboard Component", () => {
  it("should render metrics cards when data is loaded", async () => {
    render(
      <AdminContext dataProvider={mockDataProvider}>
        <Dashboard />
      </AdminContext>
    );

    await waitFor(() => {
      expect(screen.getByText("$1000.50")).toBeInTheDocument();
      expect(screen.getByText("95%")).toBeInTheDocument();
      expect(screen.getByText("3")).toBeInTheDocument();
      expect(screen.getByText("10")).toBeInTheDocument();
    });
  });
});
