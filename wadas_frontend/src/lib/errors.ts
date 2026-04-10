export type AppErrorCode =
    | "AUTH_REQUIRED"
    | "NETWORK_ERROR"
    | "HTTP_ERROR"
    | "PARSE_ERROR"
    | "UNKNOWN_ERROR";

type AppErrorOptions = {
    code: AppErrorCode;
    status?: number;
    userMessage?: string;
    details?: string;
    cause?: unknown;
};

export class AppError extends Error {
    code: AppErrorCode;
    status?: number;
    userMessage: string;
    details?: string;
    cause?: unknown;

    constructor(message: string, options: AppErrorOptions) {
        super(message);
        this.name = "AppError";
        this.code = options.code;
        this.status = options.status;
        this.userMessage = options.userMessage ?? "Unexpected error.";
        this.details = options.details;
        this.cause = options.cause;
    }
}

export function isUnauthorizedError(error: unknown): boolean {
    return error instanceof AppError && error.code === "AUTH_REQUIRED";
}

export function normalizeError(error: unknown): AppError {
    if (error instanceof AppError) {
        return error;
    }

    if (error instanceof Error) {
        return new AppError(error.message, {
            code: "UNKNOWN_ERROR",
            userMessage: "Unexpected error. Please contact the administrator.",
            cause: error,
        });
    }

    return new AppError("Unknown error", {
        code: "UNKNOWN_ERROR",
        userMessage: "Unexpected error. Please contact the administrator.",
        cause: error,
    });
}

export function getErrorMessage(error: unknown): string {
    return normalizeError(error).userMessage;
}

export async function buildHttpError(response: Response): Promise<AppError> {
    const details = await extractErrorDetails(response);

    if (response.status === 401) {
        return new AppError("Unauthorized", {
            code: "AUTH_REQUIRED",
            status: response.status,
            userMessage: "Session expired. Please log in again.",
            details,
        });
    }

    const genericMessage = `Request failed with status ${response.status}.`;

    return new AppError(genericMessage, {
        code: "HTTP_ERROR",
        status: response.status,
        userMessage: details ?? genericMessage,
        details,
    });
}

async function extractErrorDetails(response: Response): Promise<string | undefined> {
    try {
        const contentType = response.headers.get("content-type") ?? "";

        if (contentType.includes("application/json")) {
            const payload = await response.json();
            const detail = getMessageFromPayload(payload);
            return detail ?? undefined;
        }

        const text = (await response.text()).trim();
        return text || undefined;
    } catch {
        return undefined;
    }
}

function getMessageFromPayload(payload: unknown): string | null {
    if (!payload || typeof payload !== "object") {
        return null;
    }

    const record = payload as Record<string, unknown>;
    const candidates = ["message", "detail", "error", "description"];

    for (const key of candidates) {
        const value = record[key];
        if (typeof value === "string" && value.trim()) {
            return value.trim();
        }
    }

    return null;
}
