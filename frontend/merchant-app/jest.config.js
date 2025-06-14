const baseConfig = require("../jest.config.base");

module.exports = {
  ...baseConfig,
  displayName: "merchant-app",
  moduleNameMapper: {
    "^src/(.*)$": "<rootDir>/src/$1",
  },
};
