import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { RegisterPage, createRegisterPage } from "../register.page";
import { useNotify, useTranslate } from "react-admin";
import { useNavigate } from "react-router-dom";
import { RegisterPageProps } from "../register.types";
import { apiClient } from "../../../infrastructure/http/api-client.client";

// Mock dependencies
jest.mock("react-admin", () => ({
  ...jest.requireActual("react-admin"),
  useNotify: jest.fn(),
  useTranslate: jest.fn(),
  Notification: () => <div data-testid="notification" />,
}));

jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: jest.fn(),
}));

jest.mock("../../../infrastructure/http/api-client.client", () => ({
  apiClient: {
    register: jest.fn(),
  },
}));

jest.mock("../../components/public-layout.component", () => ({
  PublicLayout: jest.fn(({ children }) => <div>{children}</div>),
}));

jest.mock("../../components/back-to-home-button.component", () => ({
  BackToHomeButton: jest.fn(({ onClick }) => (
    <button onClick={onClick}>Back</button>
  )),
}));

describe("RegisterPage", () => {
  const mockNotify = jest.fn();
  const mockNavigate = jest.fn();
  const mockTranslate = jest.fn((key) => key);
  const mockRegister = apiClient.register as jest.Mock;

  beforeEach(() => {
    (useNotify as jest.Mock).mockReturnValue(mockNotify);
    (useTranslate as jest.Mock).mockReturnValue(mockTranslate);
    (useNavigate as jest.Mock).mockReturnValue(mockNavigate);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  const defaultProps: RegisterPageProps = {
    loginPath: "/login",
    userType: "customer",
  };

  it("renders the registration form with all elements", () => {
    render(<RegisterPage {...defaultProps} />);

    expect(
      screen.getByRole("heading", { name: "Create Account" })
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Email *")).toBeInTheDocument();
    expect(screen.getByLabelText("Password *")).toBeInTheDocument();
    expect(screen.getByLabelText("Confirm Password *")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Sign Up" })
    ).toBeInTheDocument();
    expect(screen.getByText("Already have an account?")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Sign in" })).toHaveAttribute(
      "href",
      "/login"
    );
  });

  it("shows back button when onBack prop is provided", () => {
    const mockOnBack = jest.fn();
    render(<RegisterPage {...defaultProps} onBack={mockOnBack} />);

    const backButton = screen.getByRole("button", { name: "Back" });
    expect(backButton).toBeInTheDocument();

    fireEvent.click(backButton);
    expect(mockOnBack).toHaveBeenCalled();
  });

  it("updates form fields when typed", () => {
    render(<RegisterPage {...defaultProps} />);

    const emailInput = screen.getByLabelText("Email *");
    const passwordInput = screen.getByLabelText("Password *");
    const confirmPasswordInput = screen.getByLabelText("Confirm Password *");

    fireEvent.change(emailInput, { target: { value: "test@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "password123" } });
    fireEvent.change(confirmPasswordInput, {
      target: { value: "password123" },
    });

    expect(emailInput).toHaveValue("test@example.com");
    expect(passwordInput).toHaveValue("password123");
    expect(confirmPasswordInput).toHaveValue("password123");
  });

  describe("form validation", () => {
    it("shows error when password is too short", async () => {
      render(<RegisterPage {...defaultProps} />);

      fireEvent.change(screen.getByLabelText("Email *"), {
        target: { value: "valid@example.com" },
      });
      fireEvent.change(screen.getByLabelText("Password *"), {
        target: { value: "short" },
      });
      fireEvent.change(screen.getByLabelText("Confirm Password *"), {
        target: { value: "short" },
      });
      fireEvent.click(screen.getByRole("button", { name: "Sign Up" }));

      await waitFor(() => {
        expect(mockTranslate).toHaveBeenCalledWith(
          "Password must be at least 8 characters"
        );
        expect(mockNotify).toHaveBeenCalledWith("ra.message.invalid_form", {
          type: "error",
        });
      });
    });

    it("shows error when passwords don't match", async () => {
      render(<RegisterPage {...defaultProps} />);

      fireEvent.change(screen.getByLabelText("Email *"), {
        target: { value: "valid@example.com" },
      });
      fireEvent.change(screen.getByLabelText("Password *"), {
        target: { value: "password123" },
      });
      fireEvent.change(screen.getByLabelText("Confirm Password *"), {
        target: { value: "differentpassword" },
      });
      fireEvent.click(screen.getByRole("button", { name: "Sign Up" }));

      await waitFor(() => {
        expect(mockTranslate).toHaveBeenCalledWith("Passwords do not match");
        expect(mockNotify).toHaveBeenCalledWith("ra.message.invalid_form", {
          type: "error",
        });
      });
    });

    it("does not show errors when form is valid", async () => {
      mockRegister.mockResolvedValueOnce({});
      render(<RegisterPage {...defaultProps} />);

      fireEvent.change(screen.getByLabelText("Email *"), {
        target: { value: "valid@example.com" },
      });
      fireEvent.change(screen.getByLabelText("Password *"), {
        target: { value: "password123" },
      });
      fireEvent.change(screen.getByLabelText("Confirm Password *"), {
        target: { value: "password123" },
      });
      fireEvent.click(screen.getByRole("button", { name: "Sign Up" }));

      await waitFor(() => {
        expect(mockNotify).not.toHaveBeenCalledWith(
          "ra.message.invalid_form",
          {
            type: "error",
          }
        );
        expect(mockRegister).toHaveBeenCalled();
      });
    });
  });

  describe("form submission", () => {
    it("calls register API with correct parameters on valid form", async () => {
      mockRegister.mockResolvedValueOnce({});
      render(<RegisterPage {...defaultProps} />);

      fireEvent.change(screen.getByLabelText("Email *"), {
        target: { value: "test@example.com" },
      });
      fireEvent.change(screen.getByLabelText("Password *"), {
        target: { value: "password123" },
      });
      fireEvent.change(screen.getByLabelText("Confirm Password *"), {
        target: { value: "password123" },
      });
      fireEvent.click(screen.getByRole("button", { name: "Sign Up" }));

      await waitFor(() => {
        expect(mockRegister).toHaveBeenCalledWith({
          email: "test@example.com",
          password: "password123",
          user_type: "customer",
        });
        expect(mockNotify).toHaveBeenCalledWith(
          "Registration successful! Please log in.",
          {
            type: "success",
          }
        );
        expect(mockNavigate).toHaveBeenCalledWith("/login");
      });
    });

    it("shows API errors when registration fails", async () => {
      const error = {
        body: {
          errors: {
            email: "Email already exists",
          },
          message: "Registration failed",
        },
      };
      mockRegister.mockRejectedValueOnce(error);
      render(<RegisterPage {...defaultProps} />);

      fireEvent.change(screen.getByLabelText("Email *"), {
        target: { value: "exists@example.com" },
      });
      fireEvent.change(screen.getByLabelText("Password *"), {
        target: { value: "password123" },
      });
      fireEvent.change(screen.getByLabelText("Confirm Password *"), {
        target: { value: "password123" },
      });
      fireEvent.click(screen.getByRole("button", { name: "Sign Up" }));

      await waitFor(() => {
        expect(screen.getByText("Email already exists")).toBeInTheDocument();
        expect(mockNotify).toHaveBeenCalledWith("ra.message.invalid_form", {
          type: "error",
        });
      });
    });
  });

  describe("createRegisterPage", () => {
    it("returns a component with the provided props", () => {
      const mockOnBack = jest.fn();
      const RegisterComponent = createRegisterPage({
        loginPath: "/my-login",
        userType: "merchant",
        onBack: mockOnBack,
      });

      const { getByRole } = render(<RegisterComponent />);

      expect(getByRole("link", { name: "Sign in" })).toHaveAttribute(
        "href",
        "/my-login"
      );
    });
  });
});
