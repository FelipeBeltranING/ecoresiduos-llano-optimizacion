import axios, { AxiosError } from "axios";

const DEFAULT_API_URL = "/api/v1";

interface ApiErrorPayload {
  detail?: string | Array<{ msg?: string }>;
}


export class ApiError extends Error {
  readonly status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}


export function normalizeBaseUrl(url: string | undefined): string {
  const value = url?.trim();
  if (!value) return DEFAULT_API_URL;
  return value.replace(/\/+$/, "");
}

export const API_URL = normalizeBaseUrl(import.meta.env.VITE_API_URL);

export const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 20_000,
  headers: {
    Accept: "application/json",
  },
});

function messageFromResponse(status: number, payload: ApiErrorPayload | undefined): string {
  if (typeof payload?.detail === "string" && payload.detail.trim()) {
    return payload.detail;
  }

  if (Array.isArray(payload?.detail)) {
    const firstMessage = payload.detail.find((item) => item?.msg)?.msg;
    if (firstMessage) return firstMessage;
  }

  if (status === 401 || status === 403) return "No tiene permisos para realizar esta acción.";
  if (status === 404) return "El recurso solicitado no existe.";
  if (status >= 500) return "El servidor presentó un error. Intente de nuevo más tarde.";
  return "No se pudo completar la solicitud.";
}

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiErrorPayload>) => {
    if (axios.isCancel(error)) {
      return Promise.reject(error);
    }

    if (error.code === "ECONNABORTED") {
      return Promise.reject(
        new ApiError("La solicitud tardó demasiado. Verifique su conexión e intente de nuevo."),
      );
    }

    if (!error.response) {
      return Promise.reject(
        new ApiError("No se pudo conectar con el servidor. Verifique que la API esté disponible."),
      );
    }

    const { status, data } = error.response;
    return Promise.reject(new ApiError(messageFromResponse(status, data), status));
  },
);
