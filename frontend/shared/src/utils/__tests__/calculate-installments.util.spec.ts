import { calculateInstallments } from "../calculate-installments.util";

describe("calculateInstallments", () => {
  it("should return correct installment breakdown with equal amounts", () => {
    const result = calculateInstallments("100.00", 4, 30, "2025-01-01");
    expect(result).toEqual([
      { sequence: 1, amount: "25.00", dueDate: "2025-01-01" },
      { sequence: 2, amount: "25.00", dueDate: "2025-01-31" },
      { sequence: 3, amount: "25.00", dueDate: "2025-03-02" },
      { sequence: 4, amount: "25.00", dueDate: "2025-04-01" },
    ]);
  });

  it("should distribute remaining cents to earlier installments", () => {
    const result = calculateInstallments("100.01", 3, 10, "2025-06-01");
    expect(result).toEqual([
      { sequence: 1, amount: "33.34", dueDate: "2025-06-01" },
      { sequence: 2, amount: "33.34", dueDate: "2025-06-11" },
      { sequence: 3, amount: "33.33", dueDate: "2025-06-21" },
    ]);
  });

  it("should return empty array for invalid totalAmount", () => {
    expect(calculateInstallments("", 3, 10, "2025-06-01")).toEqual([]);
  });

  it("should return empty array for count <= 0", () => {
    expect(calculateInstallments("100.00", 0, 10, "2025-06-01")).toEqual([]);
  });

  it("should return empty array for period <= 0", () => {
    expect(calculateInstallments("100.00", 3, 0, "2025-06-01")).toEqual([]);
  });

  it("should return empty array for invalid startDate", () => {
    expect(calculateInstallments("100.00", 3, 10, "")).toEqual([]);
  });

  it("should handle 1 installment correctly", () => {
    const result = calculateInstallments("55.55", 1, 30, "2025-01-01");
    expect(result).toEqual([
      { sequence: 1, amount: "55.55", dueDate: "2025-01-01" },
    ]);
  });

  it("should avoid floating point errors by using cents", () => {
    const result = calculateInstallments("10.01", 3, 1, "2025-01-01");
    expect(result.map((i) => i.amount)).toEqual(["3.34", "3.34", "3.33"]);
  });
});
