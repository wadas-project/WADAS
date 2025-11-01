import * as React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import LoginPage from "./LoginPage";
import Cameras from "./Cameras";
import DetectionEvents from "./DetectionEvents";
import ActuationEvents from "./ActuationEvents";
import Logs from "./Logs";
import Actuators from "./components/Actuators";

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<LoginPage />} />
                <Route path="/homepage" element={<Cameras />} />
                <Route path="/detections" element={<DetectionEvents />} />
                <Route path="/actuations" element={<ActuationEvents />} />
                <Route path="/logs" element={<Logs />} />
                 <Route path="/actuators" element={<Actuators />} />
            </Routes>
        </Router>
    );
}

export default App;
