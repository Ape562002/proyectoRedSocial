import { useState,useEffect } from "react";
import { useNavigate } from "react-router-dom";
import DropdownMenu from "../components/Base"
import "../components/ModoOscuro.css"
import "../components/SettingsModule.css"

export function ModoOscuro(){
    const [ isDarkMode, setIsDarkMode ] = useState(false)

    const navigate = useNavigate();

    useEffect(() =>{
        const savedMode = localStorage.getItem('darkMode');
        if(savedMode === 'true'){
            setIsDarkMode(true);
        }
    },[]);

    useEffect(() =>{
        if(isDarkMode){
            document.body.classList.add('dark-mode');
            localStorage.setItem('darkMode','true');
        }else{
            document.body.classList.remove('dark-mode');
            localStorage.setItem('darkMode','false');
        }
    },[isDarkMode]);

    const toggleDarkMode = () => {
        setIsDarkMode(prevMode => !prevMode);
    };

    return(
        <div>
            <h1 className="texto">Configuracion</h1>
            <DropdownMenu/>
            <div className="toggleContent">
                <button onClick={toggleDarkMode} className="b1">
                    {isDarkMode ? 'Desactivar modo oscuro' : 'Activar modo oscuro'}
                </button>
                <p>{isDarkMode ? 'Modo oscuro activado' : 'Modo claro activado'}</p>
            </div>
            <div className="contentEdit">
                <button className="buttonEdit" onClick={() => navigate(`/editProfile`)}>Editar perfil</button>
            </div>
        </div>
    )
}