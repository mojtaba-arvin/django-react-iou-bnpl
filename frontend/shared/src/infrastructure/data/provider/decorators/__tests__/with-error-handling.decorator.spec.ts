import { withErrorHandling } from "../with-error-handling.decorator";
import { ApiErrorHandler } from "../../../../errorHandler/api-error.handler";

describe("withErrorHandling", () => {
  const mockProvider = {
    getList: jest.fn(),
    getOne: jest.fn(),
    // TODO(mojtaba - 2025-06-14): Add other methods...
  };

  const mockErrorHandler = {
    handle: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should wrap all provider methods with error handling", () => {
    const decorated = withErrorHandling(
      mockProvider as any,
      mockErrorHandler as any
    );

    expect(decorated.getList).toBeDefined();
    expect(decorated.getOne).toBeDefined();
    // Check other methods...
  });

  it("should call error handler when method fails", async () => {
    const error = new Error("Test error");
    mockProvider.getList.mockRejectedValue(error);
    const decorated = withErrorHandling(
      mockProvider as any,
      mockErrorHandler as any
    );

    try {
      await decorated.getList("resource", {});
    } catch (e) {
      // Expected
    }

    expect(mockErrorHandler.handle).toHaveBeenCalledWith(error);
  });

  it("should not call error handler when method succeeds", async () => {
    mockProvider.getList.mockResolvedValue({ data: [] });
    const decorated = withErrorHandling(
      mockProvider as any,
      mockErrorHandler as any
    );

    await decorated.getList("resource", {});

    expect(mockErrorHandler.handle).not.toHaveBeenCalled();
  });
});
