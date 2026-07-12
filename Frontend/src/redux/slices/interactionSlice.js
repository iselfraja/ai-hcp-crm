import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../api';

export const createInteraction = createAsyncThunk(
    'interaction/create',
    async (data, { rejectWithValue }) => {
        try {
            const response = await api.post('/interaction', data);
            return response.data;
        } catch (err) {
            return rejectWithValue(err.response?.data?.detail || 'Creation failed');
        }
    }
);

export const updateInteraction = createAsyncThunk(
    'interaction/update',
    async ({ id, data }, { rejectWithValue }) => {
        try {
            const response = await api.put(`/interaction/${id}`, data);
            return response.data;
        } catch (err) {
            return rejectWithValue(err.response?.data?.detail || 'Update failed');
        }
    }
);

export const fetchInteractions = createAsyncThunk(
    'interaction/fetch',
    async (_, { rejectWithValue }) => {
        try {
            const response = await api.get('/interaction');
            return response.data;
        } catch (err) {
            return rejectWithValue(err.response?.data?.detail || 'Fetch failed');
        }
    }
);

const interactionSlice = createSlice({
    name: 'interaction',
    initialState: {
        list: [],
        current: null,
        loading: false,
        error: null,
        successMessage: null,  // ✅ Added for success message
    },
    reducers: {
        setCurrentInteraction: (state, action) => {
            state.current = action.payload;
        },
        clearCurrent: (state) => {
            state.current = null;
        },
        clearSuccessMessage: (state) => {
            state.successMessage = null;
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchInteractions.pending, (state) => {
                state.loading = true;
            })
            .addCase(fetchInteractions.fulfilled, (state, action) => {
                state.loading = false;
                state.list = action.payload;
            })
            .addCase(fetchInteractions.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            })
            .addCase(createInteraction.pending, (state) => {
                state.loading = true;
                state.error = null;
                state.successMessage = null;
            })
            .addCase(createInteraction.fulfilled, (state, action) => {
                state.loading = false;
                state.list.unshift(action.payload);
                state.current = action.payload;
                state.successMessage = `✅ Interaction logged successfully! (ID: ${action.payload.id})`;  // ✅ Added
            })
            .addCase(createInteraction.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
                state.successMessage = null;
            })
            .addCase(updateInteraction.pending, (state) => {
                state.loading = true;
                state.error = null;
                state.successMessage = null;
            })
            .addCase(updateInteraction.fulfilled, (state, action) => {
                state.loading = false;
                const index = state.list.findIndex(i => i.id === action.payload.id);
                if (index !== -1) state.list[index] = action.payload;
                if (state.current?.id === action.payload.id) state.current = action.payload;
                state.successMessage = `✅ Interaction updated successfully! (ID: ${action.payload.id})`;  // ✅ Added
            })
            .addCase(updateInteraction.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
                state.successMessage = null;
            });
    },
});

export const { setCurrentInteraction, clearCurrent, clearSuccessMessage } = interactionSlice.actions;
export default interactionSlice.reducer;