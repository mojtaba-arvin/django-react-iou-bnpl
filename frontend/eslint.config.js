import js from "@eslint/js";
import tseslint from "@typescript-eslint/eslint-plugin";
import tsparser from "@typescript-eslint/parser";
import react from "eslint-plugin-react";
import reactHooks from "eslint-plugin-react-hooks";

export default [
  {
    ignores: [
      "**/*.d.ts",
      "**/*.js",
      "**/*.cjs",
      "**/*.mjs",
      "**/__tests__/**/*",
      "**/*.spec.ts",
      "**/*.spec.tsx",
    ],
  },
  js.configs.recommended,
  {
    files: ["**/*.ts", "**/*.tsx"],
    languageOptions: {
      parser: tsparser,
      parserOptions: {
        ecmaVersion: 2020,
        sourceType: "module",
        project: "./tsconfig.root.json",
        ecmaFeatures: {
          jsx: true,
        },
      },
      globals: {
        // Common browser globals
        window: true,
        document: true,
        navigator: true,
        // Common Node.js globals
        process: true,
        __dirname: true,
      },
    },
    plugins: {
      "@typescript-eslint": tseslint,
      react: react,
      "react-hooks": reactHooks,
    },
    settings: {
      react: {
        version: "detect",
      },
    },
    rules: {
      // Basic rules
      indent: ["error", 2],
      quotes: ["error", "single"],
      semi: ["error", "always"],

      // Disable ESLint's core rule (replaced by @typescript-eslint version)
      "no-unused-vars": "off",

      // TypeScript rules
      "@typescript-eslint/interface-name-prefix": "off",
      "@typescript-eslint/explicit-function-return-type": "off",
      "@typescript-eslint/explicit-module-boundary-types": "off",
      "@typescript-eslint/no-explicit-any": "warn",
      "@typescript-eslint/no-unsafe-call": "error",
      "@typescript-eslint/no-unsafe-member-access": "error",
      "@typescript-eslint/no-unsafe-return": "error",
      "@typescript-eslint/no-unsafe-assignment": "error",
      "@typescript-eslint/no-misused-promises": "error",
      "@typescript-eslint/require-await": "error",
      "@typescript-eslint/no-unused-vars": [
        "error",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
          caughtErrorsIgnorePattern: "^_"
        }
      ],
      "@typescript-eslint/member-ordering": [
        "error",
        {
          default: [
            "public-static-field",
            "private-static-field",
            "public-instance-field",
            "private-instance-field",
            "constructor",
            "public-static-method",
            "private-static-method",
            "public-instance-method",
            "private-instance-method",
          ],
        },
      ],

      // React rules
      "react/react-in-jsx-scope": "off",
      "no-undef": "off", // for React 17+
      "react/jsx-uses-react": "error",
      "react/jsx-uses-vars": "error",

      // React Hooks rules
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "warn",
    },
  },
];
