import {
  convertDeleteResponse,
  convertListResponse,
  convertSingleResponse,
  normalizeData,
} from "../response-converters.adapter";

describe("normalizeData", () => {
  it("returns array if input is already an array", () => {
    const input = [{ id: 1 }, { id: 2 }];
    expect(normalizeData(input)).toEqual(input);
  });

  it("returns empty array for empty object", () => {
    expect(normalizeData({})).toEqual([]);
  });

  it("throws error for non-array non-empty object", () => {
    expect(() => normalizeData({ id: 1 })).toThrow(
      "Expected array but got object"
    );
  });

  it("throws error for null", () => {
    expect(() => normalizeData(null)).toThrow("Expected array but got object");
  });
});

describe("convertListResponse", () => {
  it("converts a successful list response", () => {
    const response = {
      success: true,
      message: "",
      data: [{ id: 1 }, { id: 2 }],
      errors: [],
      pagination: {
        total_items: 10,
        total_pages: 2,
        current_page: 1,
        page_size: 5,
        next: "url?page=2",
        previous: null,
      },
    };

    const result = convertListResponse(response);
    expect(result.data).toEqual(response.data);
    expect(result.total).toBe(10);
    expect(result.pageInfo?.hasNextPage).toBe(true);
    expect(result.pageInfo?.hasPreviousPage).toBe(false);
  });

  it("throws on failure response", () => {
    const response = {
      success: false,
      message: "Error!",
      data: [],
      errors: [],
    };
    expect(() => convertListResponse(response)).toThrow("Error!");
  });
});

describe("convertSingleResponse", () => {
  it("returns data for success", () => {
    const response = {
      success: true,
      message: "",
      data: { id: 1 },
      errors: [],
    };
    expect(convertSingleResponse(response)).toEqual({ data: { id: 1 } });
  });

  it("throws error with message or first error message", () => {
    const response = {
      success: false,
      message: "Generic error",
      data: { id: 0 },
      errors: [{ code: 400, message: "Field error", field: "id" }],
    };
    expect(() => convertSingleResponse(response)).toThrow("Field error");
  });
});

describe("convertDeleteResponse", () => {
  it("returns deleted data on success", () => {
    const response = {
      success: true,
      message: "",
      data: { id: 1 },
      errors: [],
    };
    expect(convertDeleteResponse(response)).toEqual({ data: { id: 1 } });
  });

  it("throws error message on failure", () => {
    const response = {
      success: false,
      message: "Delete failed",
      data: { id: 0 },
      errors: [],
    };
    expect(() => convertDeleteResponse(response)).toThrow("Delete failed");
  });
});
