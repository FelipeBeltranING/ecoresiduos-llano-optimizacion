import { QueryClient } from "@tanstack/react-query";

/**
 * Shared TanStack Query client.
 * The network layer already normalizes failures into ApiError, so a single retry is enough.
 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 0,
    },
  },
});
