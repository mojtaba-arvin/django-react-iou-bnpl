import { ApiClient } from "../api-client.client";
import MockAdapter from "axios-mock-adapter";
import { getGlobalSettings } from "../../context/global-settings.context";

// Mock the global settings and error handler
jest.mock("../../context/global-settings.context", () => ({
  getGlobalSettings: jest.fn(() => ({
    apiBaseUrl: "http://test-api.com",
  })),
}));

jest.mock("../../errorHandler/api-error.handler", () => ({
  ApiErrorHandler: jest.fn().mockImplementation(() => ({
    handle: jest.fn(),
  })),
}));

describe("ApiClient", () => {
  let apiClient: ApiClient;
  let mockAxios: MockAdapter;

  beforeEach(() => {
    // Create new instance for each test
    apiClient = new ApiClient();
    // Create mock adapter for the axios instance used by ApiClient
    mockAxios = new MockAdapter(apiClient["instance"]);
    localStorage.clear();
  });

  afterEach(() => {
    mockAxios.restore();
    jest.clearAllMocks();
  });

  describe("constructor", () => {
    it("should create axios instance with baseURL from global settings", () => {
      expect(getGlobalSettings).toHaveBeenCalled();
      expect(apiClient["instance"].defaults.baseURL).toBe(
        "http://test-api.com"
      );
    });
  });

  describe("request interceptor", () => {
    it("should add authorization header when token exists", async () => {
      const token = "test-token";
      localStorage.setItem("accessToken", token);

      // Mock a GET request
      mockAxios.onGet("/test").reply(200, { success: true });

      await apiClient.get("/test");

      // Verify the request was made with the auth header
      expect(mockAxios.history.get[0].headers?.Authorization).toBe(
        `Bearer ${token}`
      );
    });
  });

  describe("response interceptor", () => {
    it("should handle 401 error with token refresh", async () => {
      // Initial failed request
      mockAxios.onGet("/protected").replyOnce(401, {
        success: false,
        errors: [{ message: "token invalid" }],
      });

      // Mock the refresh token endpoint
      mockAxios.onPost("/auth/token/refresh/").reply(200, {
        success: true,
        data: {
          access: "new-access-token",
          refresh: "new-refresh-token",
        },
      });

      // Mock the retry of the original request
      mockAxios.onGet("/protected").replyOnce(200, {
        success: true,
        data: "protected-data",
      });

      localStorage.setItem("refreshToken", "old-refresh-token");

      const response = await apiClient.get("/protected");

      expect(response).toEqual({
        success: true,
        data: "protected-data",
      });
      expect(localStorage.getItem("accessToken")).toBe("new-access-token");
      expect(localStorage.getItem("refreshToken")).toBe("new-refresh-token");
    });

    it("should logout when refresh token fails", async () => {
      // Initial failed request
      mockAxios.onGet("/protected").replyOnce(401, {
        success: false,
        errors: [{ message: "token invalid" }],
      });

      // Mock failed refresh token request
      mockAxios.onPost("/auth/token/refresh/").reply(401, {
        success: false,
        errors: [{ message: "refresh token invalid" }],
      });

      localStorage.setItem("accessToken", "old-access-token");
      localStorage.setItem("refreshToken", "old-refresh-token");

      await expect(apiClient.get("/protected")).rejects.toThrow();

      expect(localStorage.getItem("accessToken")).toBeNull();
      expect(localStorage.getItem("refreshToken")).toBeNull();
    });
  });

  describe("public methods", () => {
    it("get should return response data", async () => {
      mockAxios.onGet("/test").reply(200, {
        success: true,
        data: "test-data",
      });

      const result = await apiClient.get("/test");
      expect(result).toEqual({
        success: true,
        data: "test-data",
      });
    });

    it("login should call auth endpoint with credentials", async () => {
      mockAxios.onPost("/auth/token/").reply(200, {
        success: true,
        data: {
          access: "access-token",
          refresh: "refresh-token",
        },
      });

      const loginData = { email: "test@test.com", password: "password" };
      const result = await apiClient.login(loginData);

      expect(result).toEqual({
        success: true,
        data: {
          access: "access-token",
          refresh: "refresh-token",
        },
      });
      expect(mockAxios.history.post[0].data).toBe(JSON.stringify(loginData));
    });
  });
});
