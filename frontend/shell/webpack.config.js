const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const { ModuleFederationPlugin } = require("webpack").container;
const { DefinePlugin } = require("webpack");

module.exports = {
  entry: "./src/infrastructure/shell/shell-app.bootstrap.tsx",
  mode: "development",
  devServer: {
    historyApiFallback: {
      rewrites: [
        { from: /^\/customer(\/.*)?$/, to: "/index.html" },
        { from: /^\/merchant(\/.*)?$/, to: "/index.html" },
      ],
    },
    port: 3000,
    hot: true,
    static: {
      directory: path.resolve(__dirname, "public"),
      publicPath: "/",
    },
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
      "Access-Control-Allow-Headers":
        "X-Requested-With, content-type, Authorization",
    },
  },
  output: {
    publicPath: "/", // to get correct path of "/main.js" in the index.html
    clean: true,
  },
  resolve: {
    extensions: [".tsx", ".ts", ".js"],
    alias: {
      src: path.resolve(__dirname, "src"),
      "@bnpl/shared": path.resolve(__dirname, "../shared/src"),
    },
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        loader: "ts-loader",
        options: {
          configFile: "tsconfig.build.json",
        },
        exclude: [
          /node_modules/,
          /__tests__/,
          /__mocks__/,
          /\.spec\.tsx?$/,
          /src\/jest\.d\.ts/,
        ],
      },
    ],
  },
  plugins: [
    new ModuleFederationPlugin({
      name: "shell",
      remotes: {
        customer_app: "customer_app@http://localhost:3001/remoteEntry.js",
        merchant_app: "merchant_app@http://localhost:3002/remoteEntry.js",
      },
      shared: {
        react: {
          singleton: true,
          requiredVersion: "19.1.0",
          eager: true,
          strictVersion: true,
        },
        "react-dom": {
          singleton: true,
          requiredVersion: "19.1.0",
          eager: true,
          strictVersion: true,
        },
        "react-router-dom": {
          singleton: true,
          requiredVersion: "7.6.2",
          eager: true,
        },
        "react-admin": {
          singleton: true,
          requiredVersion: "5.8.3",
          eager: true,
        },
        "@tanstack/react-query": {
          singleton: true,
          requiredVersion: "5.80.7",
          eager: true,
        },
      },
    }),
    new HtmlWebpackPlugin({
      // default inject: true, so to prevent DOM Manipulation Conflict don't add manually main.js tag to html
      template: path.resolve(__dirname, "public", "index.html"),
    }),
    new DefinePlugin({
      "process.env.NODE_ENV": JSON.stringify(process.env.NODE_ENV),
      "process.env.REACT_APP_API_BASE_URL": JSON.stringify(
        process.env.REACT_APP_API_BASE_URL
      ),
      "process.env.REACT_APP_TELEMETRY_EXPORTER_URL": JSON.stringify(
        process.env.REACT_APP_TELEMETRY_EXPORTER_URL
      ),
      "process.env.REACT_APP_CURRENCY": JSON.stringify(
        process.env.REACT_APP_CURRENCY
      ),
      "process.env.REACT_APP_LOCALE": JSON.stringify(
        process.env.REACT_APP_LOCALE
      ),
    }),
  ],
};
