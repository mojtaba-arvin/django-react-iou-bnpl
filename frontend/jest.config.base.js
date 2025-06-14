module.exports = {
  preset: "ts-jest",
  testEnvironment: "jsdom", // browser-like env to access window, document and DOM
  moduleFileExtensions: ["ts", "tsx", "js"],
  extensionsToTreatAsEsm: [".ts", ".tsx"],
  transform: {
    "^.+\\.(ts|tsx)$": [
      "ts-jest",
      {
        useESM: true,
        tsconfig: "tsconfig.json",
      },
    ],
  },
  testMatch: ["**/?(*.)+(spec|test).[jt]s?(x)"],
  testPathIgnorePatterns: [
    "<rootDir>/__tests__/test.setup.ts",
    "<rootDir>/dist/",
  ],
  setupFilesAfterEnv: ["<rootDir>/__tests__/test.setup.ts"],
};
