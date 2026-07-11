import React, { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { Grid, Paper, Typography, Box } from '@mui/material';
import FormPanel from './FormPanel';
import ChatPanel from './ChatPanel';
import { clearChat } from '../redux/slices/chatSlice';
import { clearCurrent } from '../redux/slices/interactionSlice';

const LogInteraction = () => {
    const dispatch = useDispatch();

    useEffect(() => {
        dispatch(clearChat());
        dispatch(clearCurrent());
    }, [dispatch]);

    return (
        <Box sx={{
            height: '100vh',
            overflow: 'hidden',
            bgcolor: '#f0f2f5',
            p: 3,
            display: 'flex',
            flexDirection: 'column',
        }}>

            <Grid container spacing={3} sx={{ flex: 1, minHeight: 0 }}>
                {/* Left Panel - Form */}
                <Grid item xs={12} md={7} sx={{ height: '100%', minHeight: 0 }}>
                    <Paper sx={{
                        height: '100%',
                        display: 'flex',
                        flexDirection: 'column',
                        borderRadius: 2,
                        border: '1px solid #e0e4e8',
                        overflow: 'hidden',
                    }}>
                        <FormPanel />
                    </Paper>
                </Grid>

                {/* Right Panel - Chat */}
                <Grid item xs={12} md={5} sx={{ height: '100%', minHeight: 0 }}>
                    <Paper sx={{
                        height: '100%',
                        display: 'flex',
                        flexDirection: 'column',
                        borderRadius: 2,
                        border: '1px solid #e0e4e8',
                        overflow: 'hidden',
                    }}>
                        <ChatPanel />
                    </Paper>
                </Grid>
            </Grid>
        </Box>
    );
};

export default LogInteraction;