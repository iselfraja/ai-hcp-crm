import React, { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
    Box,
    TextField,
    Button,
    Paper,
    Typography,
    CircularProgress,
    List,
    ListItem,
    ListItemText,
    Divider,
} from '@mui/material';
import { sendMessage, addUserMessage } from '../redux/slices/chatSlice';

const ChatPanel = () => {
    const dispatch = useDispatch();

    const [input, setInput] = useState('');

    const { messages, loading, error } = useSelector(
        (state) => state.chat
    );

    const { current } = useSelector(
        (state) => state.interaction
    );

    const messagesEndRef = useRef(null);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({
            behavior: 'smooth',
        });
    };

    const handleSend = async () => {
        if (!input.trim() || loading) return;

        const userMsg = input.trim();

        setInput('');

        dispatch(addUserMessage(userMsg));

        await dispatch(
            sendMessage({
                message: userMsg,
                interactionId: current?.id,
                hcpId: current?.hcp_id,
                currentFormData: current,
            })
        );
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const hasMessages = messages && messages.length > 0;

    return (
        <Box
            sx={{
                display: 'flex',
                flexDirection: 'column',
                height: '100%',
                minHeight: 0,
                p: 2,
            }}
        >
            {/* =========================
                AI ASSISTANT HEADER
            ========================== */}

            <Box
                sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                    mb: 0.5,
                    flexShrink: 0,
                }}
            >
                <Typography
                    variant="h6"
                    sx={{
                        fontSize: '1.25rem',
                    }}
                >
                    🤖
                </Typography>

                <Typography
                    variant="h6"
                    sx={{
                        fontWeight: 600,
                        color: '#1976d2',
                        fontSize: '1.25rem',
                    }}
                >
                    AI Assistant
                </Typography>
            </Box>

            {/* =========================
                SUBTITLE
            ========================== */}

            <Typography
                variant="body2"
                sx={{
                    color: '#6b7a8a',
                    fontSize: '0.875rem',
                    mb: 1.5,
                    textAlign: 'left',
                    flexShrink: 0,
                }}
            >
                Log Interaction details here via chat
            </Typography>

            {/* Divider */}

            <Divider
                sx={{
                    mb: 2,
                    borderColor: '#e0e4e8',
                    flexShrink: 0,
                }}
            />

            {/* =========================
                CHAT MESSAGE AREA
            ========================== */}

            <Paper
                variant="outlined"
                sx={{
                    flex: 1,
                    minHeight: 0,
                    overflowY: 'auto',
                    overflowX: 'hidden',
                    p: 2,
                    mb: 2,
                    bgcolor: '#fafbfc',
                    borderColor: '#e0e4e8',
                    borderRadius: 2,
                }}
            >
                {!hasMessages ? (
                    /* Initial Help Message */

                    <Box
                        sx={{
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'flex-start',
                            justifyContent: 'flex-start',
                            height: '100%',
                        }}
                    >
                        <Box
                            sx={{
                                bgcolor: '#e8f4fd',
                                borderRadius: 2,
                                p: 2.5,
                                maxWidth: '100%',
                                width: '100%',
                                textAlign: 'left',
                                boxSizing: 'border-box',
                            }}
                        >
                            <Typography
                                variant="body2"
                                sx={{
                                    color: '#1a2332',
                                    lineHeight: 1.6,
                                    fontSize: '0.875rem',
                                    textAlign: 'left',
                                }}
                            >
                                Log interaction details here (e.g., "Met Dr.
                                Smith, discussed Prodo-X efficacy, positive
                                sentiment, shared brochure") or ask for help.
                            </Typography>
                        </Box>
                    </Box>
                ) : (
                    /* Chat Messages */

                    <List dense sx={{ p: 0 }}>
                        {messages.map((msg, idx) => (
                            <ListItem
                                key={idx}
                                sx={{
                                    justifyContent:
                                        msg.role === 'user'
                                            ? 'flex-end'
                                            : 'flex-start',
                                    px: 0,
                                    py: 0.5,
                                }}
                            >
                                <Paper
                                    elevation={0}
                                    sx={{
                                        p: 1.5,
                                        bgcolor:
                                            msg.role === 'user'
                                                ? '#e3f2fd'
                                                : '#ffffff',
                                        maxWidth: '85%',
                                        border:
                                            '1px solid #e0e4e8',
                                        borderRadius: 2,
                                    }}
                                >
                                    <ListItemText
                                        primary={msg.content}
                                        primaryTypographyProps={{
                                            variant: 'body2',
                                            style: {
                                                whiteSpace: 'pre-wrap',
                                                wordBreak: 'break-word',
                                            },
                                        }}
                                    />
                                </Paper>
                            </ListItem>
                        ))}

                        {/* AI Loading Indicator */}

                        {loading && (
                            <ListItem
                                sx={{
                                    justifyContent: 'flex-start',
                                    px: 0,
                                }}
                            >
                                <Paper
                                    elevation={0}
                                    sx={{
                                        p: 1.5,
                                        bgcolor: '#f5f5f5',
                                        borderRadius: 2,
                                    }}
                                >
                                    <Box
                                        sx={{
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: 1,
                                        }}
                                    >
                                        <CircularProgress size={20} />

                                        <Typography
                                            variant="caption"
                                            color="text.secondary"
                                        >
                                            AI is thinking...
                                        </Typography>
                                    </Box>
                                </Paper>
                            </ListItem>
                        )}

                        <div ref={messagesEndRef} />
                    </List>
                )}
            </Paper>

            {/* =========================
                CHAT INPUT AREA
            ========================== */}

            <Box
                sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                    width: '100%',
                    flexShrink: 0,
                }}
            >
                {/* Input */}

                <TextField
                    fullWidth
                    placeholder="Describe Interaction..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyPress}
                    multiline
                    maxRows={3}
                    variant="outlined"
                    size="small"
                    disabled={loading}
                    sx={{
                        flex: 1,
                        minWidth: 0,

                        '& .MuiOutlinedInput-root': {
                            minHeight: '52px',
                            bgcolor: '#ffffff',
                            borderRadius: '10px',

                            '&:hover': {
                                bgcolor: '#ffffff',
                            },

                            '& fieldset': {
                                borderColor: '#9ca3af',
                            },

                            '&:hover fieldset': {
                                borderColor: '#222222',
                            },

                            '&.Mui-focused fieldset': {
                                borderColor: '#1976d2',
                            },
                        },
                    }}
                />

                {/* =========================
                    BLUE A / LOG BUTTON
                ========================== */}

                <Button
                    variant="contained"
                    onClick={handleSend}
                    disabled={loading || !input.trim()}
                    sx={{
                        bgcolor: '#1976d2',
                        color: '#ffffff',

                        minWidth: '52px',
                        width: '52px',
                        height: '52px',

                        p: 0,
                        flexShrink: 0,

                        borderRadius: '14px',

                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',

                        lineHeight: 1.1,
                        textTransform: 'none',

                        boxShadow: 'none',

                        '&:hover': {
                            bgcolor: '#1565c0',
                            boxShadow: 'none',
                        },

                        /*
                         * IMPORTANT:
                         * Keep button BLUE even when disabled
                         */
                        '&.Mui-disabled': {
                            bgcolor: '#1976d2',
                            color: '#ffffff',
                            opacity: 1,
                        },
                    }}
                >
                    <Box
                        component="span"
                        sx={{
                            display: 'block',
                            fontSize: '0.75rem',
                            fontWeight: 600,
                            color: '#ffffff',
                            lineHeight: 1.1,
                        }}
                    >
                        A
                    </Box>

                    <Box
                        component="span"
                        sx={{
                            display: 'block',
                            fontSize: '0.65rem',
                            fontWeight: 500,
                            color: '#ffffff',
                            lineHeight: 1.1,
                            mt: 0.25,
                        }}
                    >
                        Log
                    </Box>
                </Button>
            </Box>

            {/* =========================
                ERROR MESSAGE
            ========================== */}

            {error && (
                <Typography
                    color="error"
                    variant="caption"
                    sx={{
                        mt: 0.5,
                    }}
                >
                    {error}
                </Typography>
            )}
        </Box>
    );
};

export default ChatPanel;