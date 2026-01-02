import { BrowserRouter, Routes, Route, Navigate} from 'react-router-dom'
import { LoginPage } from "./pages/loginPage"
import { Dashboard } from "./pages/Dashboard"
import { Profile } from "./pages/profilePage"
import { Register } from "./pages/registerPage"
import { ModoOscuro } from "./pages/Settings"

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/login"/>}></Route>
        <Route path="/login" element={<LoginPage/>}></Route>
        <Route path="/registro" element={<Register/>}></Route>
        <Route path="/dashboard" element={<Dashboard/>}></Route>
        <Route path="/profile" element={<Profile/>}></Route>
        <Route path="/settings" element={<ModoOscuro/>}></Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
