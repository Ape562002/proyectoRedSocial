import { BrowserRouter, Routes, Route, Navigate} from 'react-router-dom'
import { LoginPage } from "./pages/loginPage"
import { Dashboard } from "./pages/Dashboard"
import { SearchPage } from "./pages/searchPage"
import { Profile } from "./pages/profilePage"
import { PerfilUsuario } from "./pages/perfilUsuario"
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
        <Route path="/search" element={<SearchPage/>}></Route>
        <Route path="/perfil/:userId" element={<PerfilUsuario />} />
        <Route path="/profile" element={<Profile/>}></Route>
        <Route path="/settings" element={<ModoOscuro/>}></Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
