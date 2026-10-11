import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from "react-router-dom"
import './index.css'
import App from './App.tsx'
import { AuthProvider } from './contexts/AuthProvider'
import { CollectionProvider } from './contexts/CollectionProvider'
import { ThemeProvider } from './contexts/ThemeProvider'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider>
      <AuthProvider>
        <CollectionProvider>
          <BrowserRouter>
            <App />
          </BrowserRouter>
        </CollectionProvider>
      </AuthProvider>
    </ThemeProvider>
  </StrictMode>,
)
