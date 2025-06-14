import React from "react";
import { render, screen } from "@testing-library/react";
import get from "lodash/get";

// 1- Prepare a mutable listContext that our mock will return
let listContext: { data: any[]; isLoading: boolean } = {
  data: [],
  isLoading: false,
};

// 2- Mock react-admin (must come before importing PlanList)
jest.mock("react-admin", () => {
  return {
    List: ({
      children,
      actions,
    }: {
      children: React.ReactNode;
      actions?: React.ReactNode;
    }) => (
      <div>
        {actions}
        {children}
      </div>
    ),
    Datagrid: ({ children }: { children: React.ReactNode }) => (
      <div data-testid="datagrid">{children}</div>
    ),
    TextField: ({ source }: any) => (
      <span data-testid={`text-${source}`}>
        {get(listContext.data[0], source)}
      </span>
    ),
    NumberField: ({ source }: any) => (
      <span data-testid={`number-${source}`}>
        {get(listContext.data[0], source)}
      </span>
    ),
    DateField: ({ source }: any) => (
      <span data-testid={`date-${source}`}>
        {get(listContext.data[0], source)}
      </span>
    ),
    FunctionField: ({ render }: { render: (r: any) => React.ReactNode }) => (
      <span data-testid="func">{render(listContext.data[0])}</span>
    ),
    Pagination: () => <div data-testid="pagination" />,
    useListContext: () => listContext,
    LinearProgress: () => <div data-testid="ra-progress" />,
    useTranslate: () => (key: string) => key,
    TopToolbar: ({ children }: any) => (
      <div data-testid="toolbar">{children}</div>
    ),
    CreateButton: ({ label }: any) => (
      <button data-testid="create-btn">{label}</button>
    ),
  };
});

// 3- Mock MUI
jest.mock("@mui/material", () => ({
  Chip: ({ label }: any) => <span data-testid="chip">{label}</span>,
  LinearProgress: () => <div data-testid="mui-progress" />,
  Box: ({ children }: any) => <div>{children}</div>,
  Typography: ({ children }: any) => <span>{children}</span>,
}));

// 4- Now import the component under test
import { PlanList } from "../plan-list.component";

describe("PlanList", () => {
  // A sample plan as `any` to avoid strict type errors
  const SAMPLE_PLAN: any = {
    id: 123,
    template_plan: { name: "Gold" },
    start_date: "2025-01-01",
    status: "active",
    progress: {
      percentage: 42,
      paid: 2,
      total: 5,
      next_due_date: "2025-02-01",
      days_remaining: 10,
    },
    customer_email: "foo@bar.com",
  };

  beforeEach(() => {
    // default context: one record, not loading
    listContext = { data: [SAMPLE_PLAN], isLoading: false };
  });

  it("shows a loading indicator when isLoading=true", () => {
    listContext = { data: [], isLoading: true };
    render(
      <PlanList
        showCreateButton={false}
        showCustomerEmail={false}
        children={<></>}
      />
    );
    expect(screen.getByTestId("ra-progress")).toBeInTheDocument();
  });

  it("renders all expected fields for one plan row", () => {
    render(
      <PlanList
        showCreateButton={false}
        showCustomerEmail={false}
        children={<></>}
      />
    );

    // ID
    expect(screen.getByTestId("text-id")).toHaveTextContent("123");
    // Plan name via FunctionField
    expect(screen.getAllByTestId("func")[0]).toHaveTextContent("Gold");
    // Start date
    expect(screen.getByTestId("date-start_date")).toHaveTextContent(
      "2025-01-01"
    );
    // Status chip
    expect(screen.getByTestId("chip")).toHaveTextContent("active");
    // Progress counts
    expect(screen.getByText("2/5 installments")).toBeInTheDocument();
    // Next due date
    expect(
      screen.getByTestId("date-progress.next_due_date")
    ).toHaveTextContent("2025-02-01");
    // Days remaining
    expect(
      screen.getByTestId("number-progress.days_remaining")
    ).toHaveTextContent("10");
  });

  it("does not render customer email by default", () => {
    render(
      <PlanList
        showCreateButton={false}
        showCustomerEmail={false}
        children={<></>}
      />
    );
    expect(screen.queryByTestId("text-customer_email")).toBeNull();
  });

  it("renders customer email when showCustomerEmail=true", () => {
    render(
      <PlanList
        showCreateButton={false}
        showCustomerEmail={true}
        children={<></>}
      />
    );
    expect(screen.getByTestId("text-customer_email")).toHaveTextContent(
      "foo@bar.com"
    );
  });

  it("renders a CreateButton when showCreateButton=true", () => {
    render(
      <PlanList
        showCreateButton={true}
        showCustomerEmail={false}
        children={<></>}
      />
    );
    expect(screen.getByTestId("create-btn")).toHaveTextContent("Create Plan");
  });
});
