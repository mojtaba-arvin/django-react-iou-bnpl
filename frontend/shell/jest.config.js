const baseConfig = require("../jest.config.base");

module.exports = {
  ...baseConfig,
  rootDir: "./",
  displayName: "shell",
  moduleNameMapper: {
    "^src/(.*)$": "<rootDir>/src/$1",
  },
  passWithNoTests: true,
};
