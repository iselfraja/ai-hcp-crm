import { configureStore } from '@reduxjs/toolkit';
import authReducer from './redux/slices/authSlice';
import interactionReducer from './redux/slices/interactionSlice';
import chatReducer from './redux/slices/chatSlice';
import voiceReducer from './redux/slices/voiceSlice'; // NEW

export const store = configureStore({
    reducer: {
        auth: authReducer,
        interaction: interactionReducer,
        chat: chatReducer,
        voice: voiceReducer, // NEW
    },
});

export default store;