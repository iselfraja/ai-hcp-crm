import { createTheme } from '@mui/material/styles';

const theme = createTheme({
    palette: {
        mode: 'light',
        primary: {
            main: '#1976d2',
        },
        background: {
            default: '#f0f2f5',
            paper: '#ffffff',
        },
        text: {
            primary: '#1a2332',
            secondary: '#6b7a8a',
        },
    },
    typography: {
        fontFamily: '"Inter", "Roboto", "Helvetica", sans-serif',
    },
    shape: {
        borderRadius: 4,
    },
    components: {
        MuiPaper: {
            styleOverrides: {
                root: {
                    boxShadow: 'none',
                },
            },
        },
        MuiTextField: {
            styleOverrides: {
                root: {
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
                        '& textarea': {
                            padding: '8px 10px',
                        },
                    },
                },
            },
        },
        MuiSelect: {
            styleOverrides: {
                root: {
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
                select: {
                    padding: '8px 10px',
                },
            },
        },
        MuiButton: {
            styleOverrides: {
                root: {
                    textTransform: 'none',
                    fontWeight: 500,
                    borderRadius: '4px',
                },
                containedPrimary: {
                    backgroundColor: '#1976d2',
                    '&:hover': {
                        backgroundColor: '#1565c0',
                    },
                },
            },
        },
        MuiRadio: {
            styleOverrides: {
                root: {
                    '& .MuiSvgIcon-root': {
                        fontSize: 18,
                    },
                },
            },
        },
        MuiDivider: {
            styleOverrides: {
                root: {
                    borderColor: '#e8ecf1',
                },
            },
        },
    },
});

export default theme;