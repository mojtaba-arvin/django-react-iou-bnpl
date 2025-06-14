import { baseDataProvider } from "../base-data.provider";
import { apiClient } from "../../../http/api-client.client";
import { convertListResponse } from "../../../adapters/react-admin/response-converters.adapter";

jest.mock("../../../http/api-client.client");
jest.mock("../../../adapters/react-admin/response-converters.adapter");

describe("baseDataProvider", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("getList", () => {
    it("should make correct API call with pagination and filters", async () => {
      const mockResponse = { data: [] };
      (apiClient.get as jest.Mock).mockResolvedValue(mockResponse);
      (convertListResponse as jest.Mock).mockReturnValue({
        data: [],
        total: 0,
      });

      await baseDataProvider.getList("resources", {
        pagination: { page: 1, perPage: 10 },
        filter: { name: "test" },
      });

      expect(apiClient.get).toHaveBeenCalledWith("/resources/", {
        params: { page: 1, page_size: 10, name: "test" },
      });
    });
  });

  describe("getOne", () => {
    it("should make correct API call with id", async () => {
      const mockResponse = { data: { id: 1 } };
      (apiClient.get as jest.Mock).mockResolvedValue(mockResponse);

      await baseDataProvider.getOne("resources", { id: 1 });

      expect(apiClient.get).toHaveBeenCalledWith("/resources/1/");
    });
  });

  // TODO(mojtaba - 2025-06-14): Add similar tests for other methods (create, etc.)
});
