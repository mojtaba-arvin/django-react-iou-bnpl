import { jwtDecode } from "jwt-decode";
import { authProvider } from "../auth.provider";
import { apiClient } from "../../../http/api-client.client";

jest.mock("jwt-decode", () => ({
  jwtDecode: jest.fn(),
}));

jest.mock("../../../http/api-client.client", () => ({
  apiClient: {
    login: jest.fn(),
    logout: jest.fn(),
  },
}));

jest.mock("../../../errorHandler/api-error.handler", () => {
  return {
    ApiErrorHandler: jest.fn().mockImplementation(() => ({
      handle: jest.fn(),
    })),
  };
});

jest.mock("../../../../utils/mask-email.util", () => ({
  maskEmail: jest.fn((email: string) => `masked_${email}`),
}));

describe("authProvider", () => {
  const validConfig = {
    loginPath: "/login",
    registerPath: "/register",
    expectedUserType: "admin",
  };

  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
    authProvider.configure(validConfig);
  });

  describe("login", () => {
    it("should store tokens and userEmail on successful login with correct userType", async () => {
      const mockAccessToken = "access.token";
      const mockRefreshToken = "refresh.token";
      const mockDecoded = {
        email: "user@example.com",
        user_type: "admin",
      };

      (apiClient.login as jest.Mock).mockResolvedValue({
        data: {
          access: mockAccessToken,
          refresh: mockRefreshToken,
        },
      });
      (jwtDecode as jest.Mock).mockReturnValue(mockDecoded);

      await authProvider.login({
        username: "user@example.com",
        password: "pass123",
        user_type: "admin",
      });

      expect(localStorage.getItem("accessToken")).toBe(mockAccessToken);
      expect(localStorage.getItem("refreshToken")).toBe(mockRefreshToken);
      expect(localStorage.getItem("userEmail")).toBe(mockDecoded.email);
    });

    it("should reject login if user_type mismatches", async () => {
      (apiClient.login as jest.Mock).mockResolvedValue({
        data: { access: "x", refresh: "y" },
      });
      (jwtDecode as jest.Mock).mockReturnValue({
        user_type: "guest",
        email: "a",
      });

      await expect(
        authProvider.login({
          username: "x",
          password: "y",
          user_type: "admin",
        })
      ).rejects.toThrow("Only admin account types can log in.");
    });
  });

  describe("logout", () => {
    it("should clear localStorage on logout", async () => {
      localStorage.setItem("accessToken", "a");
      localStorage.setItem("refreshToken", "b");
      localStorage.setItem("userEmail", "c");

      await authProvider.logout({});

      expect(localStorage.getItem("accessToken")).toBeNull();
      expect(localStorage.getItem("refreshToken")).toBeNull();
      expect(localStorage.getItem("userEmail")).toBeNull();
    });
  });

  describe("checkError", () => {
    it("should handle 401 error and clear tokens", async () => {
      localStorage.setItem("accessToken", "token");
      const result = authProvider.checkError({ status: 401 });

      await expect(result).rejects.toThrow("Authentication failed");
      expect(localStorage.getItem("accessToken")).toBeNull();
    });

    it("should resolve for other errors", async () => {
      await expect(
        authProvider.checkError({ status: 500 })
      ).resolves.toBeUndefined();
    });
  });

  describe("getIdentity", () => {
    it("should return masked email identity", async () => {
      localStorage.setItem("userEmail", "test@example.com");
      const identity = await authProvider.getIdentity!();
      expect(identity.fullName).toBe("masked_test@example.com");
    });
  });

  describe("configure", () => {
    it("should throw if config is incomplete", () => {
      expect(() => authProvider.configure({ loginPath: "/login" })).toThrow(
        "UserTypeBasedAuthProviderConfig is incomplete."
      );
    });
  });
});
