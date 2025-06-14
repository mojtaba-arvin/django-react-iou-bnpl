import { maskEmail } from "../mask-email.util";

describe("maskEmail", () => {
  it("should mask the email correctly when username is longer than 3 characters", () => {
    expect(maskEmail("username@example.com")).toBe("use***@example.com");
  });

  it("should mask the email when username is exactly 3 characters", () => {
    expect(maskEmail("abc@example.com")).toBe("abc***@example.com");
  });

  it("should mask the email when username is shorter than 3 characters", () => {
    expect(maskEmail("ab@example.com")).toBe("ab***@example.com");
  });

  it("should handle single character username", () => {
    expect(maskEmail("a@example.com")).toBe("a***@example.com");
  });
});
