import { ApiErrorHandler } from "../api-error.handler";
import { HttpError } from "react-admin";
import type { AxiosErrorResponse, RaError } from "../error-handler.types";

describe("ApiErrorHandler", () => {
  let errorHandler: ApiErrorHandler;

  beforeEach(() => {
    errorHandler = new ApiErrorHandler();
  });

  const createMockError = (data: {
    status?: number;
    message?: string;
    errors?: RaError[];
  }): AxiosErrorResponse => {
    return {
      response: {
        status: data.status || 400,
        data: {
          message: data.message || "Validation Error",
          errors: data.errors || [],
        },
      },
      message: data.message || "Error message",
    };
  };

  describe("handle", () => {
    it("should transform field-specific errors to react-admin format", () => {
      const mockError = createMockError({
        errors: [
          { field: "email", message: "Invalid email" },
          { field: "password", message: "Password too short" },
        ],
      });

      try {
        errorHandler.handle(mockError);
      } catch (error) {
        expect(error).toBeInstanceOf(HttpError);
        const httpError = error as HttpError;
        expect(httpError.message).toBe("Invalid email");
        expect(httpError.status).toBe(400);
        expect(httpError.body).toEqual({
          message: "Invalid email",
          errors: {
            email: "Invalid email",
            password: "Password too short",
          },
        });
      }
    });

    it("should use first error message as main message", () => {
      const mockError = createMockError({
        message: "General error",
        errors: [
          { field: "field1", message: "First error" },
          { field: "field2", message: "Second error" },
        ],
      });

      try {
        errorHandler.handle(mockError);
      } catch (error) {
        const httpError = error as HttpError;
        expect(httpError.message).toBe("First error");
      }
    });

    it("should handle errors with undefined field by using their message as main message", () => {
      const mockError = createMockError({
        message: "General error",
        errors: [
          { message: "Global error" },
          { field: "field1", message: "Field error" },
        ],
      });

      try {
        errorHandler.handle(mockError);
      } catch (error) {
        const httpError = error as HttpError;
        expect(httpError.message).toBe("Global error");
        expect(httpError.body.errors).toEqual({
          field1: "Field error",
        });
      }
    });

    it("should fall back to response message when no field errors exist", () => {
      const mockError = createMockError({
        status: 500,
        message: "Internal server error",
        errors: [],
      });

      try {
        errorHandler.handle(mockError);
      } catch (error) {
        const httpError = error as HttpError;
        expect(httpError.message).toBe("Internal server error");
        expect(httpError.status).toBe(500);
        expect(httpError.body).toEqual({
          message: "Internal server error",
        });
      }
    });

    it("should fall back to axios error message when no response data exists", () => {
      const mockError = {
        message: "Network Error",
        isAxiosError: true,
      } as unknown as AxiosErrorResponse;

      try {
        errorHandler.handle(mockError);
      } catch (error) {
        const httpError = error as HttpError;
        expect(httpError.message).toBe("Network Error");
        expect(httpError.status).toBe(500);
        expect(httpError.body).toEqual({
          message: "Network Error",
        });
      }
    });

    it("should use default message when no error information is available", () => {
      const mockError = {} as AxiosErrorResponse;

      try {
        errorHandler.handle(mockError);
      } catch (error) {
        const httpError = error as HttpError;
        expect(httpError.message).toBe("Server Error");
        expect(httpError.status).toBe(500);
        expect(httpError.body).toEqual({
          message: "Server Error",
        });
      }
    });

    it("should include all error fields in the errors object", () => {
      const mockError = createMockError({
        errors: [
          { field: "field1", message: "Error 1" },
          { field: "field2", message: "Error 2" },
          { field: "field3", message: "Error 3" },
        ],
      });

      try {
        errorHandler.handle(mockError);
      } catch (error) {
        const httpError = error as HttpError;
        expect(Object.keys(httpError.body.errors)).toHaveLength(3);
        expect(httpError.body.errors.field1).toBe("Error 1");
        expect(httpError.body.errors.field2).toBe("Error 2");
        expect(httpError.body.errors.field3).toBe("Error 3");
      }
    });
  });
});
