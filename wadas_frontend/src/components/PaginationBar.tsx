import * as React from "react";
import { Container, Pagination } from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";
import "../styles/App.css";

const PaginationBar = (props: {
    currentPage: number;
    totalPages: number;
    onPageChange: (number: number) => void;
}) => {
    const renderPaginationItems = () => {
        const pages = [];
        const showPages = 3;
        const sidePages = 1;

        pages.push(
            <Pagination.Item
                key={1}
                active={props.currentPage === 1}
                onClick={() => props.onPageChange(1)}
            >
                1
            </Pagination.Item>
        );

        if (props.currentPage > showPages) {
            pages.push(<Pagination.Ellipsis key="start-ellipsis" disabled />);
        }

        const start = Math.max(2, props.currentPage - sidePages);
        const end = Math.min(props.totalPages - 1, props.currentPage + sidePages);

        for (let i = start; i <= end; i++) {
            pages.push(
                <Pagination.Item
                    key={i}
                    active={props.currentPage === i}
                    onClick={() => props.onPageChange(i)}
                >
                    {i}
                </Pagination.Item>
            );
        }

        if (props.currentPage < props.totalPages - showPages + 1) {
            pages.push(<Pagination.Ellipsis key="end-ellipsis" disabled />);
        }

        if (props.totalPages > 1) {
            pages.push(
                <Pagination.Item
                    key={props.totalPages}
                    active={props.currentPage === props.totalPages}
                    onClick={() => props.onPageChange(props.totalPages)}
                >
                    {props.totalPages}
                </Pagination.Item>
            );
        }

        return pages;
    };

    return (
        <Container className="d-flex justify-content-center mt-3" style={{ height: "15%" }}>
            <Pagination>
                <Pagination.Prev
                    onClick={() => props.onPageChange(props.currentPage - 1)}
                    disabled={props.currentPage === 1}
                />
                {renderPaginationItems()}
                <Pagination.Next
                    onClick={() => props.onPageChange(props.currentPage + 1)}
                    disabled={props.currentPage === props.totalPages}
                />
            </Pagination>
        </Container>
    );
};

export default PaginationBar;
