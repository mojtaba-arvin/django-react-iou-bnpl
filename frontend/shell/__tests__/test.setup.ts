import "@testing-library/jest-dom";

// TextEncoder polyfills
import { TextEncoder } from "util";
global.TextEncoder = TextEncoder;
