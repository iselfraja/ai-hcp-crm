import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { GlobalStyles } from '@mui/material';
import LogInteraction from './components/LogInteraction';

function App() {
    return (
        <Router>
            <GlobalStyles
                styles={{
                    '@keyframes pulse': {
                        '0%': {
                            transform: 'scale(1)',
                            opacity: 1,
                        },
                        '50%': {
                            transform: 'scale(1.2)',
                            opacity: 0.7,
                        },
                        '100%': {
                            transform: 'scale(1)',
                            opacity: 1,
                        },
                    },
                }}
            />
            <Routes>
                <Route path="/" element={<LogInteraction />} />
                <Route path="*" element={<Navigate to="/" />} />
            </Routes>
        </Router>
    );
}

export default App;