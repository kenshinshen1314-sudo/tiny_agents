import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Game from './game/index.tsx'
import Collection from './pages/Collection'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Game />} />
        <Route path="/collection" element={<Collection />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
