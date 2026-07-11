import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../api';

export const summarizeVoiceNote = createAsyncThunk(
    'voice/summarize',
    async (transcript, { rejectWithValue }) => {
        try {
            const response = await api.post('/voice/summarize', { transcript });
            return response.data;
        } catch (err) {
            return rejectWithValue(err.response?.data?.detail || 'Summarization failed');
        }
    }
);

const voiceSlice = createSlice({
    name: 'voice',
    initialState: {
        isRecording: false,
        isProcessing: false,
        transcript: '',
        summary: '',
        error: null,
        permissionGranted: false,
        mediaRecorder: null,
        audioChunks: [],
    },
    reducers: {
        startRecording: (state) => {
            state.isRecording = true;
            state.error = null;
        },
        stopRecording: (state) => {
            state.isRecording = false;
        },
        setTranscript: (state, action) => {
            state.transcript = action.payload;
        },
        clearTranscript: (state) => {
            state.transcript = '';
        },
        setPermissionGranted: (state, action) => {
            state.permissionGranted = action.payload;
        },
        setError: (state, action) => {
            state.error = action.payload;
        },
        clearError: (state) => {
            state.error = null;
        },
        setAudioChunks: (state, action) => {
            state.audioChunks = action.payload;
        },
        setMediaRecorder: (state, action) => {
            state.mediaRecorder = action.payload;
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(summarizeVoiceNote.pending, (state) => {
                state.isProcessing = true;
                state.error = null;
            })
            .addCase(summarizeVoiceNote.fulfilled, (state, action) => {
                state.isProcessing = false;
                state.summary = action.payload.summary;
            })
            .addCase(summarizeVoiceNote.rejected, (state, action) => {
                state.isProcessing = false;
                state.error = action.payload;
            });
    },
});

export const {
    startRecording,
    stopRecording,
    setTranscript,
    clearTranscript,
    setPermissionGranted,
    setError,
    clearError,
    setAudioChunks,
    setMediaRecorder,
} = voiceSlice.actions;

export default voiceSlice.reducer;