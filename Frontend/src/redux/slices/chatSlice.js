import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../api';

export const sendMessage = createAsyncThunk(
    'chat/send',
    async ({ message, interactionId, hcpId, currentFormData }, { rejectWithValue }) => {
        try {
            const response = await api.post('/agent/chat', {
                message,
                interaction_id: interactionId,
                hcp_id: hcpId,
                current_form_data: currentFormData
            });
            return response.data;
        } catch (err) {
            return rejectWithValue(err.response?.data?.detail || 'Chat error');
        }
    }
);

const chatSlice = createSlice({
    name: 'chat',
    initialState: {
        messages: [],
        extractedData: null,
        suggestedFollowups: [],
        interactionId: null,
        loading: false,
        error: null,
        toolCalls: [],
    },
    reducers: {
        clearChat: (state) => {
            state.messages = [];
            state.extractedData = null;
            state.suggestedFollowups = [];
            state.interactionId = null;
            state.toolCalls = [];
        },
        addUserMessage: (state, action) => {
            state.messages.push({ role: 'user', content: action.payload });
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(sendMessage.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(sendMessage.fulfilled, (state, action) => {
                state.loading = false;
                state.messages.push({ role: 'assistant', content: action.payload.message });
                state.extractedData = action.payload.interaction_data || null;
                state.suggestedFollowups = action.payload.suggested_followups || [];
                state.interactionId = action.payload.interaction_id || null;
                state.toolCalls = action.payload.tool_calls || [];
            })
            .addCase(sendMessage.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
                state.messages.push({
                    role: 'assistant',
                    content: `Error: ${action.payload || 'Failed to process request'}`
                });
            });
    },
});

export const { clearChat, addUserMessage } = chatSlice.actions;
export default chatSlice.reducer;