import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { AuthProvider } from './utils/Auth.jsx'

ReactDOM.createRoot(document.getElementById('root')).render(
    <AuthProvider>
      <App />
    </AuthProvider>
)
