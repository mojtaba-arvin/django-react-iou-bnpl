const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const { ModuleFederationPlugin } = require("webpack").container;
const { DefinePlugin } = require("webpack");

module.exports = (env) => {
  // standalone or remote
  const isStandalone = env.standalone === "true";

  return {
    mode: env.production ? "production" : "development",

    // just standalone allowed to use root.render, for remote env root.render will be handle by shell
    entry: isStandalone
      ? path.resolve(
          __dirname,
          "src/infrastructure/standalone/standalone-app.bootstrap.tsx"
        )
      : path.resolve(
          __dirname,
          "src/infrastructure/federation/remote-entry.module.ts"
        ),

    output: {
      path: path.resolve(__dirname, "dist"),
      publicPath: isStandalone ? "http://localhost:3001/" : "auto",
      filename: isStandalone ? "[name].js" : undefined,
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
      ...(isStandalone
        ? [
            new HtmlWebpackPlugin({
              template: path.resolve(__dirname, "public", "index.html"),
            }),
          ]
        : [
            new ModuleFederationPlugin({
              name: "customer_app",
              filename: "remoteEntry.js",
              // No root.render files to prevent multi React Trees in shell
              exposes: {
                "./createAdminAppConfig":
                  "./src/application/services/create-admin-app-config.service.ts",
              },
              shared: {
                react: {
                  singleton: true,
                  requiredVersion: "19.1.0",
                  eager: false,
                },
                "react-dom": {
                  singleton: true,
                  requiredVersion: "19.1.0",
                  eager: false,
                },
                "react-router-dom": {
                  singleton: true,
                  requiredVersion: "7.6.2",
                  eager: false,
                },
                "react-admin": {
                  singleton: true,
                  requiredVersion: "5.8.3",
                  eager: false,
                },
                "@tanstack/react-query": {
                  singleton: true,
                  requiredVersion: "5.80.7",
                  eager: false,
                },
              },
            }),
          ]),
    ],

    devServer: {
      port: 3001,
      hot: true,
      historyApiFallback: true,
      static: {
        directory: path.resolve(__dirname, "public"),
        publicPath: "/",
      },
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods":
          "GET, POST, PUT, DELETE, PATCH, OPTIONS",
        "Access-Control-Allow-Headers":
          "X-Requested-With, content-type, Authorization",
      },
    },
  };
};
