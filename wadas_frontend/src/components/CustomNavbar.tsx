import * as React from 'react';
import {useEffect, useState} from 'react';
import {Container, Nav, Navbar} from "react-bootstrap";
import "../styles/App.css";
import {useNavigate, useLocation} from "react-router-dom";
// @ts-ignore
import logo from "../assets/wadas_logo.png";

const CustomNavbar = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [currentPath, setCurrentPath] = useState<string>(location.pathname);
    const [expanded, setExpanded] = useState(false);

    const handleNavClick = (path: string) => {
        navigate(path);
        setExpanded(false);
    };

    useEffect(() => {
        setCurrentPath(location.pathname);
    }, [location.pathname]);

    return (
        <Container>
            <Navbar bg="white" expand="lg" fixed="top" style={{padding: "0px"}} expanded={expanded}>
                <Container className="solid-grey-bottom-border" style={{padding: "8px"}}>
                    <Navbar.Brand href="/homepage" className="d-flex align-items-center" style={{fontWeight: "600"}}>
                        <img
                            src={logo}
                            alt="Logo"
                            style={{height: "40px", width: "40px", marginRight: "30px"}}
                        />
                        WADAS
                    </Navbar.Brand>
                    <Navbar.Toggle aria-controls="navbar-menu" onClick={() => setExpanded(!expanded)}/>
                    <Navbar.Collapse id="navbar-menu" role="navigation">
                        <Nav className="me-auto">
                            <Nav.Link
                                onClick={() => handleNavClick("/homepage")}
                                className={currentPath === "/homepage" || currentPath === "/" ? "selected-menu-item" : ""}
                            >
                                CAMERAS
                            </Nav.Link>
                            <Nav.Link
                                onClick={() => handleNavClick("/detections")}
                                className={currentPath === "/detections" ? "selected-menu-item" : ""}
                            >
                                DETECTION EVENTS
                            </Nav.Link>
                            <Nav.Link
                                onClick={() => handleNavClick("/actuations")}
                                className={currentPath === "/actuations" ? "selected-menu-item" : ""}
                            >
                                ACTUATION EVENTS
                            </Nav.Link>
                        </Nav>
                    </Navbar.Collapse>
                </Container>
            </Navbar>
        </Container>
    );
}

export default CustomNavbar;
