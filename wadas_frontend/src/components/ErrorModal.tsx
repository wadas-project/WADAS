import React, { createContext, useCallback, useContext, useMemo, useState } from "react";
import { Modal } from "react-bootstrap";

type ErrorModalState = {
    title: string;
    message: string;
};

type ErrorModalContextValue = {
    hideError: () => void;
    showError: (message: string, title?: string) => void;
};

const ErrorModalContext = createContext<ErrorModalContextValue | undefined>(undefined);

export const ErrorModalProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [errorState, setErrorState] = useState<ErrorModalState | null>(null);

    const hideError = useCallback(() => {
        setErrorState(null);
    }, []);

    const showError = useCallback((message: string, title = "Error") => {
        setErrorState({ title, message });
    }, []);

    const value = useMemo(
        () => ({
            hideError,
            showError,
        }),
        [hideError, showError]
    );

    return (
        <ErrorModalContext.Provider value={value}>
            {children}
            <Modal show={errorState !== null} onHide={hideError} centered>
                <Modal.Header closeButton>
                    <Modal.Title>{errorState?.title ?? "Error"}</Modal.Title>
                </Modal.Header>
                <Modal.Body>{errorState?.message}</Modal.Body>
            </Modal>
        </ErrorModalContext.Provider>
    );
};

export function useErrorModal(): ErrorModalContextValue {
    const context = useContext(ErrorModalContext);

    if (!context) {
        throw new Error("useErrorModal must be used within ErrorModalProvider");
    }

    return context;
}
