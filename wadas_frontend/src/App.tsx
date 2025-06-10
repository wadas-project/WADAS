import * as React from "react";
import {BrowserRouter as Router, Route, Routes} from "react-router-dom";
import LoginPage from "./LoginPage";
import Cameras from "./Cameras";
import DetectionEvents from "./DetectionEvents";
import ActuationEvents from "./ActuationEvents";

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/homepage" element={<Cameras/>}/>
                <Route path="/detections" element={<DetectionEvents/>}/>
                <Route path="/actuations" element={<ActuationEvents/>}/>
                <Route path="/" element={<LoginPage/>}/>
            </Routes>
        </Router>
    );
}

export default App;
