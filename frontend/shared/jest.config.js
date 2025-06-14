const baseConfig = require("../jest.config.base");

module.exports = {
  ...baseConfig,
  displayName: "shared",
  moduleNameMapper: {
    "^src/(.*)$": "<rootDir>/src/$1",
  },
};
