import { Spinner } from "react-bootstrap";
import * as React from "react";

const CustomSpinner = ({ className = "mt-5" }: { className?: string }) => {
    return (
        <div className={`text-center ${className}`}>
            <Spinner animation="border" role="status" />
        </div>
    );
};

export default CustomSpinner;
