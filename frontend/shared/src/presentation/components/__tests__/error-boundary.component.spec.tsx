import React from "react";
import { render, screen } from "@testing-library/react";
import { ErrorBoundary } from "../error-boundary.component";
import { logger } from "../../../infrastructure/telemetry/logger.util";

describe("ErrorBoundary", () => {
  // suppress React error logging in test output
  beforeAll(() => {
    jest.spyOn(console, "error").mockImplementation(() => {});
  });
  afterAll(() => {
    (console.error as jest.Mock).mockRestore();
  });

  it("renders children when no error is thrown", () => {
    render(
      <ErrorBoundary>
        <div>All good</div>
      </ErrorBoundary>
    );
    expect(screen.getByText("All good")).toBeInTheDocument();
  });

  it("catches errors from children, shows fallback, and logs error", () => {
    const testError = new Error("Boom!");
    const errorSpy = jest.spyOn(logger, "error").mockImplementation();

    // Component that throws on render
    const Bomb: React.FC = () => {
      throw testError;
    };

    render(
      <ErrorBoundary>
        <Bomb />
      </ErrorBoundary>
    );

    // Fallback UI
    expect(screen.getByText("Application loading failed")).toBeInTheDocument();

    // Ensure logger.error was called
    expect(errorSpy).toHaveBeenCalledTimes(1);

    const calls = errorSpy.mock.calls;
    expect(calls[0]).toBeDefined();

    // Cast the first call to [Error, { componentStack: string }]
    const [loggedError, meta] = calls[0] as [
      Error,
      { componentStack: string }
    ];

    expect(loggedError).toBe(testError);
    expect(meta.componentStack).toEqual(expect.any(String));

    errorSpy.mockRestore();
  });
});
