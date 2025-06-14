import React from "react";
import { render, screen } from "@testing-library/react";

// Mutable context values
let recordContext: any = null;
let globalSettings: { currency: string; locale: string } = {
  currency: "USD",
  locale: "en-US",
};

// 1- Mock react-admin before importing PlanShow
jest.mock("react-admin", () => ({
  Show: ({ children, title }: any) => (
    <div>
      {title}
      {children}
    </div>
  ),
  SimpleShowLayout: ({ children }: any) => <div>{children}</div>,
  TextField: ({ source }: any) => (
    <span data-testid={`text-${source}`}>{recordContext?.[source]}</span>
  ),
  DateField: ({ source }: any) => (
    <span data-testid={`date-${source}`}>{recordContext?.[source]}</span>
  ),
  NumberField: ({ source }: any) => (
    <span data-testid={`number-${source}`}>{recordContext?.[source]}</span>
  ),
  FunctionField: ({ label, source, render }: any) => (
    <span data-testid={`func-${label || source || "unknown"}`}>
      {render(recordContext)}
    </span>
  ),
  ArrayField: ({ source, children }: any) => (
    <div data-testid="array-field">
      {recordContext?.[source]?.map((item: any, index: number) => {
        const previousRecordContext = recordContext;
        recordContext = item;
        const rendered =
          typeof children === "function" ? children(item) : children;
        recordContext = previousRecordContext;
        return <div key={index}>{rendered}</div>;
      })}
    </div>
  ),
  Datagrid: ({ children }: any) => (
    <div data-testid="datagrid">{children}</div>
  ),
  Labeled: ({ children }: any) => <div data-testid="labeled">{children}</div>,
  useRecordContext: () => recordContext,
  useTranslate: () => (key: string) => key,
}));

// 2- Mock MUI components
jest.mock("@mui/material", () => ({
  Box: ({ children }: any) => <div>{children}</div>,
  Chip: ({ label }: any) => <span data-testid="chip">{label}</span>,
  Typography: ({ children, variant }: any) => (
    <div data-testid={`typography-${variant}`}>{children}</div>
  ),
  LinearProgress: ({ variant, value }: any) => (
    <div data-testid="progress">{value}</div>
  ),
}));

// 3- Mock global settings hook and currency formatter
jest.mock(
  "../../../../infrastructure/context/global-settings.context",
  () => ({
    useGlobalSettings: () => globalSettings,
  })
);
jest.mock("../../../../utils/currency-formatter.util", () => ({
  formatCurrency: (amount: number, currency: string, locale: string) =>
    `${currency} ${Number(amount).toFixed(2)}`,
}));

// 4- Now import the component under test
import { PlanShow } from "../plan-show.component";

// Sample plan record
const SAMPLE_PLAN = {
  id: 99,
  template_plan: {
    name: "Silver",
    total_amount: "1500",
    installment_count: 3,
    installment_period: 15,
  },
  start_date: "2025-05-01",
  status: "active",
  progress: {
    percentage: 0.5,
    paid: 1,
    total: 3,
    next_due_date: "2025-06-01",
    days_remaining: 30,
  },
  customer_email: "user@example.com",
  installments: [
    {
      sequence_number: 1,
      due_date: "2025-06-01",
      amount: 500,
      paid_at: "2025-06-02",
      status: "paid",
    },
  ],
};

describe("PlanShow", () => {
  beforeEach(() => {
    recordContext = SAMPLE_PLAN;
    globalSettings = { currency: "EUR", locale: "de-DE" };
  });

  it("renders the title with ID and plan name", () => {
    render(<PlanShow showCustomerEmail={false} children={<></>} />);
    expect(screen.getByTestId("typography-h5")).toHaveTextContent(
      "Plan #99 - Silver"
    );
  });

  // TODO
  //   it("renders basic fields", () => {
  //     render(<PlanShow children={<></>} />);
  //     expect(screen.getByTestId("text-id")).toHaveTextContent("99");
  //     expect(screen.getByTestId("func-name")).toHaveTextContent("Silver");
  //     expect(screen.getByTestId("date-start_date")).toHaveTextContent(
  //       "2025-05-01"
  //     );
  //     expect(screen.getByTestId("chip")).toHaveTextContent("active");
  //   });

  it("renders progress section and progress bar", () => {
    render(<PlanShow children={<></>} />);
    // paid/installments
    expect(screen.getByText("1/3 installments paid")).toBeInTheDocument();
    // progress bar value
    expect(screen.getByTestId("progress")).toHaveTextContent("0.5");
  });

  // TODO
  //   it("formats total amount using currency formatter", () => {
  //     render(<PlanShow children={<></>} />);
  //     screen.getAllByTestId("func").forEach((el) => console.log(el.textContent));

  //     const funcs = screen.getAllByTestId("func");
  //     // The first one is probably for total amount
  //     expect(funcs[0]).toHaveTextContent("EUR 1500.00");
  //   });

  //   it("renders installments array with one row", () => {
  //     render(<PlanShow showCustomerEmail={false} children={<></>} />);
  //     expect(screen.getByTestId("array-field")).toBeInTheDocument();
  //     // sequence number
  //     expect(screen.getByTestId("number-sequence_number")).toHaveTextContent(
  //       "1"
  //     );
  //     // due date
  //     expect(screen.getByTestId("date-due_date")).toHaveTextContent(
  //       "2025-06-01"
  //     );
  //     // amount
  //     expect(
  //       screen.getAllByTestId("func-installmentAmount")[1]
  //     ).toHaveTextContent("EUR 500.00");
  //     // paid_at date
  //     expect(screen.getByTestId("date-paid_at")).toHaveTextContent("2025-06-02");
  //     // installment status chip
  //     expect(screen.getAllByTestId("chip")[1]).toHaveTextContent("paid");
  //   });

  it("conditionally renders customer email when prop is true", () => {
    render(<PlanShow showCustomerEmail={true} children={<></>} />);
    expect(screen.getByTestId("text-customer_email")).toHaveTextContent(
      "user@example.com"
    );
  });

  it("hides customer email when prop is false", () => {
    render(<PlanShow showCustomerEmail={false} children={<></>} />);
    expect(screen.queryByTestId("text-customer_email")).toBeNull();
  });
});
