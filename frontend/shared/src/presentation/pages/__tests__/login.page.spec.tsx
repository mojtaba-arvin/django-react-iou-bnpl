import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { LoginPage, createLoginPage } from "../login.page";
import { useLogin, useNotify, useTranslate } from "react-admin";
import { LoginPageProps } from "../login.types";

// Mock dependencies
jest.mock("react-admin", () => ({
  ...jest.requireActual("react-admin"),
  useLogin: jest.fn(),
  useNotify: jest.fn(),
  useTranslate: jest.fn(),
  Notification: () => <div data-testid="notification" />,
}));

jest.mock("../../components/public-layout.component", () => ({
  PublicLayout: jest.fn(({ children }) => <div>{children}</div>),
}));

jest.mock("../../components/back-to-home-button.component", () => ({
  BackToHomeButton: jest.fn(({ onClick }) => (
    <button onClick={onClick}>Back</button>
  )),
}));

describe("LoginPage", () => {
  const mockLogin = jest.fn(() => Promise.resolve(undefined));
  const mockNotify = jest.fn();
  const mockTranslate = jest.fn((key) => key);

  beforeEach(() => {
    (useLogin as jest.Mock).mockReturnValue(mockLogin);
    (useNotify as jest.Mock).mockReturnValue(mockNotify);
    (useTranslate as jest.Mock).mockReturnValue(mockTranslate);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  const defaultProps: LoginPageProps = {
    registerPath: "/register",
    userType: "customer",
  };

  it("renders the login form with all elements", () => {
    render(<LoginPage {...defaultProps} />);

    expect(
      screen.getByRole("heading", { name: "Sign In" })
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Email *")).toBeInTheDocument();
    expect(screen.getByLabelText("Password *")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Sign In" })
    ).toBeInTheDocument();
    expect(screen.getByText("Don't have an account?")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Sign up" })).toHaveAttribute(
      "href",
      "/register"
    );
  });

  it("shows back button when onBack prop is provided", () => {
    const mockOnBack = jest.fn();
    render(<LoginPage {...defaultProps} onBack={mockOnBack} />);

    const backButton = screen.getByRole("button", { name: "Back" });
    expect(backButton).toBeInTheDocument();

    fireEvent.click(backButton);
    expect(mockOnBack).toHaveBeenCalled();
  });

  it("updates email and password fields when typed", () => {
    render(<LoginPage {...defaultProps} />);

    const emailInput = screen.getByLabelText("Email *");
    const passwordInput = screen.getByLabelText("Password *");

    fireEvent.change(emailInput, { target: { value: "test@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "password123" } });

    expect(emailInput).toHaveValue("test@example.com");
    expect(passwordInput).toHaveValue("password123");
  });

  it("calls login function with correct parameters on form submit", async () => {
    render(<LoginPage {...defaultProps} />);

    fireEvent.change(screen.getByLabelText("Email *"), {
      target: { value: "test@example.com" },
    });
    fireEvent.change(screen.getByLabelText("Password *"), {
      target: { value: "password123" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Sign In" }));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        username: "test@example.com",
        password: "password123",
        user_type: "customer",
      });
    });
  });

  it("shows error notification when login fails", async () => {
    const error = new Error("");
    mockLogin.mockRejectedValueOnce(error);
    render(<LoginPage {...defaultProps} />);

    fireEvent.change(screen.getByLabelText("Email *"), {
      target: { value: "test@example.com" },
    });
    fireEvent.change(screen.getByLabelText("Password *"), {
      target: { value: "wrong" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Sign In" }));

    await waitFor(() => {
      expect(mockNotify).toHaveBeenCalledWith("Invalid email or password", {
        type: "error",
      });
    });
  });
});

describe("createLoginPage", () => {
  it("returns a component with the provided props", () => {
    const mockOnBack = jest.fn();
    const LoginComponent = createLoginPage({
      registerPath: "/custom-register",
      userType: "merchant",
      onBack: mockOnBack,
    });

    const { getByRole } = render(<LoginComponent />);

    expect(getByRole("link", { name: "Sign up" })).toHaveAttribute(
      "href",
      "/custom-register"
    );
  });
});
