import React from "react";
import { render, screen } from "@testing-library/react";
import { FormattedDateTimeField } from "../formatted-date-time-field.component";

// ——— Module‐scope record we’ll swap per test ———————————————————
let currentRecord: Record<string, any> = {};

// ——— Mock react-admin’s FunctionField —————————————————————
jest.mock("react-admin", () => ({
  FunctionField: ({ render }: { render: (rec: any) => React.ReactNode }) => (
    <>{render(currentRecord)}</>
  ),
}));

describe("FormattedDateTimeField", () => {
  const SOURCE = "date";

  it("renders a dash when record has no value", () => {
    currentRecord = {}; // no date property
    render(<FormattedDateTimeField source={SOURCE} />);
    expect(screen.getByText("-")).toBeInTheDocument();
  });

  it("renders the invalidDateMessage for unparsable values", () => {
    currentRecord = { [SOURCE]: "not-a-date" };
    render(
      <FormattedDateTimeField source={SOURCE} invalidDateMessage="Bad date" />
    );
    expect(screen.getByText("Bad date")).toBeInTheDocument();
  });

  it("formats valid ISO date strings in default locale", () => {
    currentRecord = { [SOURCE]: "2025-06-10T15:30:00Z" };
    render(<FormattedDateTimeField source={SOURCE} />);

    // Partial, regex-based match for the date
    expect(screen.getByText(/Jun\s+10,\s+2025/)).toBeInTheDocument();
    // Partial, regex-based match for the time
    expect(screen.getByText(/03:30\s?PM/)).toBeInTheDocument();
  });

  it("respects a custom locale (but still hour12=true)", () => {
    currentRecord = { [SOURCE]: "2025-06-10T15:30:00Z" };
    render(<FormattedDateTimeField source={SOURCE} locale="de-DE" />);

    // German month name, partial match
    expect(screen.getByText(/10\.\s*Juni\s*2025/)).toBeInTheDocument();
    // Still 12-hour clock with PM
    expect(screen.getByText(/03:30\s?PM/)).toBeInTheDocument();
  });

  it("passes through label and sortable props to FunctionField", () => {
    render(
      <FormattedDateTimeField
        source={SOURCE}
        label="My Date"
        sortable={false}
      />
    );
    expect(screen.queryByText(/My Date/)).not.toBeInTheDocument();
  });
});
