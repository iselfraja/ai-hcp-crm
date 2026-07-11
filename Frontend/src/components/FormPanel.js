import React, { useState, useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
    TextField,
    Button,
    Grid,
    MenuItem,
    FormControl,
    InputLabel,
    Select,
    Box,
    Typography,
    CircularProgress,
    Alert,
    Divider,
    Chip,
    RadioGroup,
    FormControlLabel,
    Radio,
    IconButton,
    InputAdornment,
    Snackbar,
    Paper,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import MicIcon from '@mui/icons-material/Mic';
import StopIcon from '@mui/icons-material/Stop';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import SearchIcon from '@mui/icons-material/Search';
import { createInteraction, updateInteraction } from '../redux/slices/interactionSlice';

const FormPanel = () => {
    const dispatch = useDispatch();
    const { extractedData, suggestedFollowups } = useSelector((state) => state.chat);
    const { current, loading, error } = useSelector((state) => state.interaction);

    const [formData, setFormData] = useState({
        hcp_name: '',
        date: new Date().toISOString().split('T')[0],
        interaction_type: 'Meeting',
        time: new Date().toTimeString().slice(0, 5),  // ✅ Auto set current time (HH:MM format)
        attendees: '',
        topics_discussed: '',
        materials: [{ name: '', quantity: 1 }],
        samples: [{ product_name: '', quantity: 1 }],
        sentiment: '',
        outcome: '',
        follow_up_actions: '',
    });

    // Voice recording states
    const [isRecording, setIsRecording] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [recordingError, setRecordingError] = useState(null);
    const [showSuccess, setShowSuccess] = useState(false);

    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);
    const streamRef = useRef(null);
    const recognitionRef = useRef(null);

    useEffect(() => {
        if (extractedData) {
            setFormData((prev) => ({
                ...prev,
                ...extractedData,
                date: extractedData.date || prev.date,
            }));
        }
    }, [extractedData]);

    useEffect(() => {
        if (suggestedFollowups && suggestedFollowups.length > 0) {
            const newFollowups = suggestedFollowups.map((action) => ({
                action,
                due_date: null,
            }));
            setFormData((prev) => ({
                ...prev,
                followups: newFollowups,
                follow_up_actions: newFollowups.map(f => f.action).join('; '),
            }));
        }
    }, [suggestedFollowups]);

    useEffect(() => {
        if (current) {
            setFormData({
                hcp_name: current.hcp?.name || '',
                date: current.date ? new Date(current.date).toISOString().split('T')[0] : new Date().toISOString().split('T')[0],
                interaction_type: current.interaction_type || 'Meeting',
                time: current.time || '19:36',
                attendees: current.attendees || '',
                topics_discussed: current.topics_discussed || '',
                materials: current.materials?.length ? current.materials : [{ name: '', quantity: 1 }],
                samples: current.samples?.length ? current.samples : [{ product_name: '', quantity: 1 }],
                sentiment: current.sentiment || '',
                outcome: current.outcome || '',
                follow_up_actions: current.follow_up_actions || '',
            });
        }
    }, [current]);

    useEffect(() => {
        if (transcript) {
            setFormData((prev) => ({
                ...prev,
                topics_discussed: transcript,
            }));
        }
    }, [transcript]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleArrayChange = (field, index, key, value) => {
        const newArray = [...formData[field]];
        newArray[index][key] = value;
        setFormData((prev) => ({ ...prev, [field]: newArray }));
    };

    const addArrayItem = (field, emptyItem) => {
        setFormData((prev) => ({ ...prev, [field]: [...prev[field], emptyItem] }));
    };

    const removeArrayItem = (field, index) => {
        if (formData[field].length > 1) {
            const newArray = formData[field].filter((_, i) => i !== index);
            setFormData((prev) => ({ ...prev, [field]: newArray }));
        }
    };

    // Voice Recording Functions
    const stopRecording = () => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
            mediaRecorderRef.current.stop();
        }
        if (recognitionRef.current) {
            try {
                recognitionRef.current.stop();
            } catch (e) { }
            recognitionRef.current = null;
        }
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }
        setIsRecording(false);
    };

    const startRecording = (stream) => {
        try {
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;
            audioChunksRef.current = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };

            mediaRecorder.onstop = () => {
                if (streamRef.current) {
                    streamRef.current.getTracks().forEach(track => track.stop());
                    streamRef.current = null;
                }

                if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    const recognition = new SpeechRecognition();
                    recognition.lang = 'en-US';
                    recognition.continuous = false;
                    recognition.interimResults = false;

                    recognition.onresult = (event) => {
                        const transcriptText = event.results[0][0].transcript;
                        setTranscript(transcriptText);
                        setIsRecording(false);
                        setRecordingError(null);
                    };

                    recognition.onerror = () => {
                        setRecordingError('Failed to transcribe audio. Please try again.');
                        setIsRecording(false);
                    };

                    recognition.onend = () => {
                        setIsRecording(false);
                    };

                    recognitionRef.current = recognition;
                    recognition.start();
                } else {
                    setRecordingError('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
                    setIsRecording(false);
                }
            };

            mediaRecorder.start();
            setIsRecording(true);
            setRecordingError(null);
        } catch (err) {
            setRecordingError('Failed to start recording: ' + err.message);
            setIsRecording(false);
        }
    };

    const handleMicClick = () => {
        if (isRecording) {
            stopRecording();
            return;
        }

        navigator.mediaDevices.getUserMedia({ audio: true })
            .then((stream) => {
                streamRef.current = stream;
                startRecording(stream);
            })
            .catch(() => {
                setRecordingError('Please allow microphone access.');
            });
    };

    const handleSummarizeVoiceNote = async () => {
        if (!transcript) {
            setRecordingError('Please record a voice note first.');
            return;
        }

        setIsProcessing(true);
        setRecordingError(null);

        try {
            const response = await fetch('http://localhost:8000/voice/summarize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ transcript: transcript }),
            });

            const data = await response.json();

            if (response.ok) {
                setFormData((prev) => ({
                    ...prev,
                    topics_discussed: data.summary || transcript,
                }));
                setTranscript('');
                setShowSuccess(true);
                setRecordingError(null);
            } else {
                setRecordingError(data.detail || 'Failed to summarize voice note.');
            }
        } catch (err) {
            setRecordingError('Failed to summarize: ' + err.message);
        } finally {
            setIsProcessing(false);
        }
    };

    const handleCloseSuccess = () => {
        setShowSuccess(false);
    };

    const handleSubmit = () => {
        const payload = {
            hcp_id: 1,
            interaction_type: formData.interaction_type,
            date: new Date(formData.date).toISOString(),
            time: formData.time,
            attendees: formData.attendees,
            topics_discussed: formData.topics_discussed,
            sentiment: formData.sentiment || 'Neutral',
            outcome: formData.outcome,
            follow_up_actions: formData.follow_up_actions,
            materials: formData.materials.filter(m => m.name.trim() !== ''),
            samples: formData.samples.filter(s => s.product_name.trim() !== ''),
        };
        if (current && current.id) {
            dispatch(updateInteraction({ id: current.id, data: payload }));
        } else {
            dispatch(createInteraction(payload));
        }
    };

    if (loading) return <CircularProgress />;
    if (error) return <Alert severity="error">{error}</Alert>;

    return (
        <Box
            className="form-scroll"
            sx={{
                flex: 1,
                overflowY: 'auto',
                overflowX: 'hidden',
                minHeight: 0,
                p: 3,
                backgroundColor: '#ffffff',
                '&::-webkit-scrollbar': {
                    width: '6px',
                },
                '&::-webkit-scrollbar-track': {
                    backgroundColor: '#f0f2f5',
                    borderRadius: '3px',
                },
                '&::-webkit-scrollbar-thumb': {
                    backgroundColor: '#c1c7cd',
                    borderRadius: '3px',
                    '&:hover': {
                        backgroundColor: '#a0a8b0',
                    },
                },
            }}
        >
            {/* Form Title */}
            <Typography
                variant="h5"
                sx={{
                    fontWeight: 600,
                    color: '#1a2332',
                    mb: 3,
                    fontSize: '1.5rem',
                }}
            >
                Log HCP Interaction
            </Typography>

            <Grid container spacing={2}>
                {/* Row 1: HCP Name + Interaction Type */}
                <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#1a2332', mb: 0.5, fontSize: '0.8rem' }}>
                        HCP Name
                    </Typography>
                    <TextField
                        fullWidth
                        placeholder="Search or select HCP..."
                        name="hcp_name"
                        value={formData.hcp_name}
                        onChange={handleChange}
                        size="small"
                        sx={inputStyles}
                    />
                </Grid>

                <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#1a2332', mb: 0.5, fontSize: '0.8rem' }}>
                        Interaction Type
                    </Typography>
                    <FormControl fullWidth size="small" sx={selectStyles}>
                        <Select
                            name="interaction_type"
                            value={formData.interaction_type}
                            onChange={handleChange}
                            displayEmpty
                        >
                            <MenuItem value="Meeting">Meeting</MenuItem>
                            <MenuItem value="Call">Call</MenuItem>
                            <MenuItem value="Email">Email</MenuItem>
                            <MenuItem value="Other">Other</MenuItem>
                        </Select>
                    </FormControl>
                </Grid>

                {/* Row 2: Date + Time */}
                <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#1a2332', mb: 0.5, fontSize: '0.8rem' }}>
                        Date
                    </Typography>
                    <TextField
                        fullWidth
                        type="date"
                        name="date"
                        value={formData.date}
                        onChange={handleChange}
                        size="small"
                        InputLabelProps={{ shrink: true }}
                        sx={inputStyles}
                    />
                </Grid>

                <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#1a2332', mb: 0.5, fontSize: '0.8rem' }}>
                        Time
                    </Typography>
                    <TextField
                        fullWidth
                        type="time"
                        name="time"
                        value={formData.time}
                        onChange={handleChange}
                        size="small"
                        InputLabelProps={{ shrink: true }}
                        sx={inputStyles}
                    />
                </Grid>

                {/* Row 3: Attendees - Full Width */}
                <Grid item xs={12}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#1a2332', mb: 0.5, fontSize: '0.8rem' }}>
                        Attendees
                    </Typography>
                    <TextField
                        fullWidth
                        placeholder="Enter names or search..."
                        name="attendees"
                        value={formData.attendees}
                        onChange={handleChange}
                        size="small"
                        sx={inputStyles}
                    />
                </Grid>

                {/* Topics Discussed - Resizable Textarea with Microphone at Bottom */}
                <Grid item xs={12}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#1a2332', mb: 0.5, fontSize: '0.8rem' }}>
                        Topics Discussed
                    </Typography>
                    <Box sx={{ position: 'relative' }}>
                        <textarea
                            name="topics_discussed"
                            value={formData.topics_discussed}
                            onChange={handleChange}
                            placeholder="Enter key discussion points..."
                            style={{
                                width: '100%',
                                minHeight: '80px',
                                padding: '8px 10px 40px 10px',
                                fontSize: '0.85rem',
                                fontFamily: 'inherit',
                                backgroundColor: '#fafafa',
                                border: '1px solid #d9dde3',
                                borderRadius: '4px',
                                resize: 'vertical',
                                outline: 'none',
                                boxSizing: 'border-box',
                            }}
                            onFocus={(e) => {
                                e.target.style.borderColor = '#1976d2';
                            }}
                            onBlur={(e) => {
                                e.target.style.borderColor = '#d9dde3';
                            }}
                        />
                        <Box sx={{
                            position: 'absolute',
                            bottom: '8px',
                            right: '8px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: 1,
                        }}>
                            <IconButton
                                onClick={handleMicClick}
                                size="small"
                                sx={{
                                    color: isRecording ? '#f44336' : '#1976d2',
                                    backgroundColor: isRecording ? 'rgba(244, 67, 54, 0.1)' : 'transparent',
                                    padding: '4px',
                                    '&:hover': {
                                        backgroundColor: isRecording ? 'rgba(244, 67, 54, 0.2)' : 'rgba(25, 118, 210, 0.1)',
                                    },
                                    animation: isRecording ? 'pulse 1.5s ease-in-out infinite' : 'none',
                                }}
                            >
                                {isRecording ? <StopIcon fontSize="small" /> : <MicIcon fontSize="small" />}
                            </IconButton>
                        </Box>
                    </Box>
                    {isRecording && (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                            <Box sx={{
                                width: 8,
                                height: 8,
                                borderRadius: '50%',
                                bgcolor: '#f44336',
                                animation: 'pulse 1s ease-in-out infinite',
                            }} />
                            <Typography variant="caption" color="error">
                                Recording... Click the stop button (red) to finish
                            </Typography>
                        </Box>
                    )}
                    {recordingError && (
                        <Alert severity="error" sx={{ mt: 0.5, fontSize: '0.75rem' }} onClose={() => setRecordingError(null)}>
                            {recordingError}
                        </Alert>
                    )}
                </Grid>

                {/* Summarize from Voice Note */}
                <Grid item xs={12}>
                    <Button
                        variant="text"
                        size="small"
                        startIcon={isProcessing ? <CircularProgress size={14} /> : <AutoAwesomeIcon sx={{ fontSize: '0.9rem' }} />}
                        onClick={handleSummarizeVoiceNote}
                        disabled={isProcessing || !transcript}
                        sx={{
                            textTransform: 'none',
                            color: '#1976d2',
                            fontSize: '0.8rem',
                            fontWeight: 500,
                            padding: '4px 0',
                            '&:hover': {
                                backgroundColor: 'transparent',
                                textDecoration: 'underline',
                            },
                            '&:disabled': {
                                color: '#b0b8c4',
                            },
                        }}
                    >
                        {isProcessing ? 'Summarizing...' : 'Summarize from Voice Note (Requires Consent)'}
                    </Button>
                    {transcript && !isProcessing && (
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5, fontSize: '0.7rem' }}>
                            Voice note recorded. Click the button above to generate summary.
                        </Typography>
                    )}
                </Grid>

                <Grid item xs={12}>
                    <Divider sx={{ my: 1.5, borderColor: '#e8ecf1' }} />
                </Grid>

                {/* Materials Shared / Samples Distributed */}
                <Grid item xs={12}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#1a2332', fontSize: '0.9rem', mb: 1.5 }}>
                        Materials Shared / Samples Distributed
                    </Typography>

                    {/* Materials Shared Box */}
                    <Paper
                        variant="outlined"
                        sx={{
                            p: 2,
                            mb: 2,
                            borderRadius: '4px',
                            borderColor: '#d9dde3',
                            backgroundColor: '#ffffff',
                            boxShadow: 'none',
                        }}
                    >
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                            <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#1a2332', fontSize: '0.8rem' }}>
                                Materials Shared
                            </Typography>
                            <Button
                                size="small"
                                startIcon={<AddIcon sx={{ fontSize: '0.9rem' }} />}
                                onClick={() => addArrayItem('materials', { name: '', quantity: 1 })}
                                sx={{
                                    textTransform: 'none',
                                    fontSize: '0.75rem',
                                    color: '#1976d2',
                                    border: '1px solid #d9dde3',
                                    borderRadius: '4px',
                                    padding: '2px 10px',
                                    minHeight: '28px',
                                    '&:hover': {
                                        backgroundColor: '#f5f7fa',
                                        borderColor: '#1976d2',
                                    },
                                }}
                            >
                                🔍 Search/Add
                            </Button>
                        </Box>

                        {formData.materials.every(m => !m.name) ? (
                            <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic', fontSize: '0.8rem' }}>
                                No materials added.
                            </Typography>
                        ) : (
                            formData.materials.map((item, idx) => (
                                <Grid container spacing={1} key={idx} sx={{ mb: 1 }}>
                                    <Grid item xs={8}>
                                        <TextField
                                            fullWidth
                                            placeholder="Material name..."
                                            value={item.name}
                                            onChange={(e) => handleArrayChange('materials', idx, 'name', e.target.value)}
                                            size="small"
                                            sx={inputStyles}
                                        />
                                    </Grid>
                                    <Grid item xs={2}>
                                        <TextField
                                            fullWidth
                                            type="number"
                                            placeholder="Qty"
                                            value={item.quantity}
                                            onChange={(e) => handleArrayChange('materials', idx, 'quantity', parseInt(e.target.value) || 1)}
                                            size="small"
                                            sx={inputStyles}
                                        />
                                    </Grid>
                                    <Grid item xs={2}>
                                        <Button
                                            size="small"
                                            color="error"
                                            onClick={() => removeArrayItem('materials', idx)}
                                            disabled={formData.materials.length === 1}
                                            sx={{
                                                textTransform: 'none',
                                                fontSize: '0.7rem',
                                                color: '#f44336',
                                                minWidth: 'auto',
                                                padding: '2px 8px',
                                            }}
                                        >
                                            Remove
                                        </Button>
                                    </Grid>
                                </Grid>
                            ))
                        )}
                    </Paper>

                    {/* Samples Distributed Box */}
                    <Paper
                        variant="outlined"
                        sx={{
                            p: 2,
                            borderRadius: '4px',
                            borderColor: '#d9dde3',
                            backgroundColor: '#ffffff',
                            boxShadow: 'none',
                        }}
                    >
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                            <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#1a2332', fontSize: '0.8rem' }}>
                                Samples Distributed
                            </Typography>
                            <Button
                                size="small"
                                startIcon={<AddIcon sx={{ fontSize: '0.9rem' }} />}
                                onClick={() => addArrayItem('samples', { product_name: '', quantity: 1 })}
                                sx={{
                                    textTransform: 'none',
                                    fontSize: '0.75rem',
                                    color: '#1976d2',
                                    border: '1px solid #d9dde3',
                                    borderRadius: '4px',
                                    padding: '2px 10px',
                                    minHeight: '28px',
                                    '&:hover': {
                                        backgroundColor: '#f5f7fa',
                                        borderColor: '#1976d2',
                                    },
                                }}
                            >
                                Add Sample
                            </Button>
                        </Box>

                        {formData.samples.every(s => !s.product_name) ? (
                            <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic', fontSize: '0.8rem' }}>
                                No samples added.
                            </Typography>
                        ) : (
                            formData.samples.map((item, idx) => (
                                <Grid container spacing={1} key={idx} sx={{ mb: 1 }}>
                                    <Grid item xs={8}>
                                        <TextField
                                            fullWidth
                                            placeholder="Product name..."
                                            value={item.product_name}
                                            onChange={(e) => handleArrayChange('samples', idx, 'product_name', e.target.value)}
                                            size="small"
                                            sx={inputStyles}
                                        />
                                    </Grid>
                                    <Grid item xs={2}>
                                        <TextField
                                            fullWidth
                                            type="number"
                                            placeholder="Qty"
                                            value={item.quantity}
                                            onChange={(e) => handleArrayChange('samples', idx, 'quantity', parseInt(e.target.value) || 1)}
                                            size="small"
                                            sx={inputStyles}
                                        />
                                    </Grid>
                                    <Grid item xs={2}>
                                        <Button
                                            size="small"
                                            color="error"
                                            onClick={() => removeArrayItem('samples', idx)}
                                            disabled={formData.samples.length === 1}
                                            sx={{
                                                textTransform: 'none',
                                                fontSize: '0.7rem',
                                                color: '#f44336',
                                                minWidth: 'auto',
                                                padding: '2px 8px',
                                            }}
                                        >
                                            Remove
                                        </Button>
                                    </Grid>
                                </Grid>
                            ))
                        )}
                    </Paper>
                </Grid>

                <Grid item xs={12}>
                    <Divider sx={{ my: 1.5, borderColor: '#e8ecf1' }} />
                </Grid>

                {/* Observed/Inferred HCP Sentiment */}
                <Grid item xs={12}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#1a2332', mb: 1, fontSize: '0.8rem' }}>
                        Observed/Inferred HCP Sentiment
                    </Typography>
                    <RadioGroup
                        row
                        name="sentiment"
                        value={formData.sentiment}
                        onChange={handleChange}
                        sx={{ gap: 2 }}
                    >
                        <FormControlLabel
                            value="Positive"
                            control={<Radio size="small" sx={{ '& .MuiSvgIcon-root': { fontSize: 18 } }} />}
                            label={
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontSize: '0.8rem' }}>
                                    <span>😊</span> Positive
                                </Box>
                            }
                            sx={{ mr: 0 }}
                        />
                        <FormControlLabel
                            value="Neutral"
                            control={<Radio size="small" sx={{ '& .MuiSvgIcon-root': { fontSize: 18 } }} />}
                            label={
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontSize: '0.8rem' }}>
                                    <span>😐</span> Neutral
                                </Box>
                            }
                            sx={{ mr: 0 }}
                        />
                        <FormControlLabel
                            value="Negative"
                            control={<Radio size="small" sx={{ '& .MuiSvgIcon-root': { fontSize: 18 } }} />}
                            label={
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontSize: '0.8rem' }}>
                                    <span>😞</span> Negative
                                </Box>
                            }
                            sx={{ mr: 0 }}
                        />
                    </RadioGroup>
                </Grid>

                {/* Outcomes - Resizable Textarea */}
                <Grid item xs={12}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#1a2332', mb: 0.5, fontSize: '0.8rem' }}>
                        Outcomes
                    </Typography>
                    <textarea
                        name="outcome"
                        value={formData.outcome}
                        onChange={handleChange}
                        placeholder="Key outcomes or agreements..."
                        style={{
                            width: '100%',
                            minHeight: '60px',
                            padding: '8px 10px',
                            fontSize: '0.85rem',
                            fontFamily: 'inherit',
                            backgroundColor: '#fafafa',
                            border: '1px solid #d9dde3',
                            borderRadius: '4px',
                            resize: 'vertical',
                            outline: 'none',
                            boxSizing: 'border-box',
                        }}
                        onFocus={(e) => {
                            e.target.style.borderColor = '#1976d2';
                        }}
                        onBlur={(e) => {
                            e.target.style.borderColor = '#d9dde3';
                        }}
                    />
                </Grid>

                {/* Follow-up Actions - Resizable Textarea */}
                <Grid item xs={12}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#1a2332', mb: 0.5, fontSize: '0.8rem' }}>
                        Follow-up Actions
                    </Typography>
                    <textarea
                        name="follow_up_actions"
                        value={formData.follow_up_actions}
                        onChange={handleChange}
                        placeholder="Enter next steps or tasks..."
                        style={{
                            width: '100%',
                            minHeight: '60px',
                            padding: '8px 10px',
                            fontSize: '0.85rem',
                            fontFamily: 'inherit',
                            backgroundColor: '#fafafa',
                            border: '1px solid #d9dde3',
                            borderRadius: '4px',
                            resize: 'vertical',
                            outline: 'none',
                            boxSizing: 'border-box',
                        }}
                        onFocus={(e) => {
                            e.target.style.borderColor = '#1976d2';
                        }}
                        onBlur={(e) => {
                            e.target.style.borderColor = '#d9dde3';
                        }}
                    />
                </Grid>

                {/* AI Suggested Follow-ups */}
                {suggestedFollowups && suggestedFollowups.length > 0 && (
                    <Grid item xs={12}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#1a2332', mb: 1, fontSize: '0.8rem' }}>
                            AI Suggested Follow-ups:
                        </Typography>
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                            {suggestedFollowups.map((item, idx) => (
                                <Box
                                    key={idx}
                                    sx={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: 1,
                                        padding: '4px 8px',
                                        cursor: 'pointer',
                                        borderRadius: '4px',
                                        '&:hover': {
                                            backgroundColor: '#f5f7fa',
                                        },
                                    }}
                                    onClick={() => {
                                        const currentActions = formData.follow_up_actions ? formData.follow_up_actions + '; ' : '';
                                        setFormData(prev => ({
                                            ...prev,
                                            follow_up_actions: currentActions + item
                                        }));
                                    }}
                                >
                                    <Typography sx={{ color: '#1976d2', fontSize: '1rem' }}>→</Typography>
                                    <Typography sx={{ color: '#1976d2', fontSize: '0.8rem', cursor: 'pointer' }}>
                                        {item}
                                    </Typography>
                                </Box>
                            ))}
                        </Box>
                    </Grid>
                )}

                {/* Log Interaction Button */}
                <Grid item xs={12}>
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={handleSubmit}
                        fullWidth
                        disabled={loading}
                        sx={{
                            mt: 2,
                            py: 1.5,
                            bgcolor: '#1976d2',
                            textTransform: 'none',
                            fontSize: '0.9rem',
                            fontWeight: 500,
                            borderRadius: '4px',
                            '&:hover': {
                                bgcolor: '#1565c0',
                            }
                        }}
                    >
                        {current ? 'Update Interaction' : 'Log Interaction'}
                    </Button>
                </Grid>
            </Grid>

            {/* Success Snackbar */}
            <Snackbar
                open={showSuccess}
                autoHideDuration={4000}
                onClose={handleCloseSuccess}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
            >
                <Alert onClose={handleCloseSuccess} severity="success" variant="filled">
                    Voice note summarized successfully! 🎉
                </Alert>
            </Snackbar>
        </Box>
    );
};

// ✅ Input Styles - Compact, professional, matching reference
const inputStyles = {
    '& .MuiOutlinedInput-root': {
        backgroundColor: '#fafafa',
        borderRadius: '4px',
        minHeight: '40px',
        fontSize: '0.85rem',
        '& fieldset': {
            borderColor: '#d9dde3',
            borderWidth: '1px',
        },
        '&:hover fieldset': {
            borderColor: '#b0b8c4',
        },
        '&.Mui-focused fieldset': {
            borderColor: '#1976d2',
            borderWidth: '1px',
        },
        '& input': {
            padding: '8px 10px',
            height: 'auto',
        },
    },
    '& .MuiInputLabel-root': {
        fontSize: '0.8rem',
    },
};

const selectStyles = {
    '& .MuiOutlinedInput-root': {
        backgroundColor: '#fafafa',
        borderRadius: '4px',
        minHeight: '40px',
        fontSize: '0.85rem',
        '& fieldset': {
            borderColor: '#d9dde3',
            borderWidth: '1px',
        },
        '&:hover fieldset': {
            borderColor: '#b0b8c4',
        },
        '&.Mui-focused fieldset': {
            borderColor: '#1976d2',
            borderWidth: '1px',
        },
    },
    '& .MuiSelect-select': {
        padding: '8px 10px',
    },
};

export default FormPanel;