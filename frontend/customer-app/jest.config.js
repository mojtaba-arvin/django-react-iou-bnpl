const baseConfig = require("../jest.config.base");

module.exports = {
  ...baseConfig,
  displayName: "customer-app",
  moduleNameMapper: {
    "^src/(.*)$": "<rootDir>/src/$1",
  },
  passWithNoTests: true,
};
