import "bootstrap/dist/css/bootstrap.min.css";
import * as React from "react";
import {useState} from "react";
import {Alert, Button, Card, Container, Form} from "react-bootstrap";
import {useNavigate} from "react-router-dom";
import {baseUrl} from "./config";
import Image from "react-bootstrap/Image";
// @ts-ignore
import logo from "./assets/wadas_logo.png";


const LoginPage = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e: any) => {
        e.preventDefault();

        if (!username || !password) {
            setError("All fields are required.");
            setSuccess(false);
            return;
        }

        try {
            const response = await fetch(baseUrl.concat("api/v1/login"), {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({username, password}),
            });

            if (!response.ok) {
                setError("Invalid credentials.");
                setSuccess(false);
            } else {
                const data = await response.json();
                setSuccess(true);
                setError("");
                // Store the received tokens
                localStorage.setItem("accessToken", data.access_token);
                localStorage.setItem("refreshToken", data.refresh_token);
                navigate("/homepage");
            }
        } catch (err: any) {
            console.error(err.message);
            setError(`Generic Error - ${err.message}. Please contact the administrator.`);
        }
    };

    return (
        <div style={{height: "100vh", display: "flex", justifyContent: "center", alignItems: "center"}}>
            <Container className="d-flex justify-content-center">
                <Card style={{width: "100%", maxWidth: "25rem"}}>
                    <Card.Body className="text-center">
                        <Image src={logo} alt="WADAS Logo" width={100} className="mb-3"/>
                        <Card.Title className="mb-4">WADAS - Login</Card.Title>

                        {error && <Alert variant="danger">{error}</Alert>}
                        {success && <Alert variant="success">Login successful!</Alert>}

                        <Form onSubmit={handleSubmit}>
                            <Form.Group className="mb-3" controlId="formBasicEmail">
                                <Form.Label className={"text-semibold"}>Username</Form.Label>
                                <Form.Control
                                    className={"custom-input"}
                                    type="text"
                                    placeholder="Enter your username"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                />
                            </Form.Group>

                            <Form.Group className="mb-3" controlId="formBasicPassword">
                                <Form.Label className={"text-semibold"}>Password</Form.Label>
                                <Form.Control
                                    className={"custom-input"}
                                    type="password"
                                    placeholder="Enter your password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                            </Form.Group>

                            <div className="d-flex justify-content-center">
                                <Button variant="primary" type="submit"
                                        className="w-50 custom-button dark-background mt-3">
                                    Login
                                </Button>
                            </div>
                        </Form>
                    </Card.Body>
                </Card>
            </Container>
        </div>

    );
};

export default LoginPage;
