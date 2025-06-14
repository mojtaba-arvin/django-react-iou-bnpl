import type { DataProvider } from "react-admin";
import { logger } from "../logger.util";
import { getGlobalSettings } from "../../context/global-settings.context";
import { wrapDataProviderWithLogging } from "../data-provider-logger.util";

jest.mock("../logger.util", () => ({
  logger: {
    info: jest.fn(),
    error: jest.fn(),
  },
}));

jest.mock("../../context/global-settings.context", () => ({
  getGlobalSettings: jest.fn(),
}));

describe("wrapDataProviderWithLogging", () => {
  const mockGetGlobalSettings = getGlobalSettings as jest.Mock;
  const mockLoggerInfo = logger.info as jest.Mock;
  const mockLoggerError = logger.error as jest.Mock;

  beforeEach(() => {
    jest.clearAllMocks();
    mockGetGlobalSettings.mockReturnValue({
      redactedKeys: ["password", "secret"],
    });
  });

  const createMockDataProvider = () =>
  ({
    getOne: jest.fn(),
    getList: jest.fn(),
  } as unknown as DataProvider);

  it("should call original method and log metadata and result", async () => {
    const mockDP = createMockDataProvider();
    mockDP.getOne = jest
      .fn()
      .mockResolvedValue({ data: { id: 1, name: "Alice" } });

    const wrapped = wrapDataProviderWithLogging(mockDP);
    const result = await wrapped.getOne("users", { id: 1 });

    expect(mockDP.getOne).toHaveBeenCalledWith("users", { id: 1 });
    expect(mockLoggerInfo).toHaveBeenCalledWith("DP call: getOne", {
      resource: "users",
      id: 1,
    });
    expect(mockLoggerInfo).toHaveBeenCalledWith("DP success: getOne", {
      resource: "users",
      op: "getOne",
    });
    expect(result).toEqual({ data: { id: 1, name: "Alice" } });
  });

  it("should redact sensitive fields in params.filter", async () => {
    const mockDP = createMockDataProvider();
    mockDP.getList = jest
      .fn()
      .mockResolvedValue({ data: [{ id: 1 }], total: 1 });

    const wrapped = wrapDataProviderWithLogging(mockDP);
    await wrapped.getList("secrets", {
      filter: { password: "123", token: "abc" },
      pagination: { page: 1, perPage: 10 },
    });

    expect(mockLoggerInfo).toHaveBeenCalledWith("DP call: getList", {
      resource: "secrets",
      pagination: '{"page":1,"perPage":10}',
      filter: '{"password":"[REDACTED]","token":"abc"}',
    });
  });

  it("should log error with redacted params and rethrow", async () => {
    const mockDP = createMockDataProvider();
    const error = new Error("Access denied");
    mockDP.getOne = jest.fn().mockRejectedValue(error);

    const wrapped = wrapDataProviderWithLogging(mockDP);
    const params = { id: 1, password: "secret123" };

    await expect(wrapped.getOne("admins", params)).rejects.toThrow("Access denied");

    expect(mockLoggerError).toHaveBeenCalledWith(error, {
      resource: "admins",
      op: "getOne",
      params: '{"id":1,"password":"[REDACTED]"}',
    });
  });

  it("should not crash when filter or params is null", async () => {
    const mockDP = createMockDataProvider();
    mockDP.getOne = jest.fn().mockResolvedValue({ data: { id: 1 } });

    const wrapped = wrapDataProviderWithLogging(mockDP);
    await wrapped.getOne("users", null as any);

    expect(mockLoggerInfo).toHaveBeenCalledWith("DP call: getOne", {
      resource: "users",
    });
  });

  it("should leave unrelated properties untouched", () => {
    const mockDP = createMockDataProvider();
    mockDP.customProp = "someValue";

    const wrapped = wrapDataProviderWithLogging(mockDP);
    expect((wrapped as any).customProp).toBe("someValue");
  });
});
