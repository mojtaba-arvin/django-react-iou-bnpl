jest.mock("../base-data.provider", () => ({
  baseDataProvider: { mockKey: "mocked base provider" },
}));

jest.mock("../decorators/with-error-handling.decorator", () => ({
  withErrorHandling: jest.fn(),
}));

import { baseDataProvider } from "../base-data.provider";
import { withErrorHandling } from "../decorators/with-error-handling.decorator";

describe("dataProvider", () => {
  it("should be created by decorating baseDataProvider with error handling", () => {
    (withErrorHandling as jest.Mock).mockClear();

    jest.isolateModules(() => {
      require("../data-provider");
    });

    expect(withErrorHandling).toHaveBeenCalledWith(
      baseDataProvider,
      expect.any(Object)
    );

    const callArgs = (withErrorHandling as jest.Mock).mock.calls[0];
    expect(callArgs[1].constructor.name).toBe("ApiErrorHandler");
  });
});
