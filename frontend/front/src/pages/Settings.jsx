import { useState,useEffect } from "react";
import DropdownMenu from "../components/Base"
import "../components/ModoOscuro.css"

export function ModoOscuro(){
    const [ isDarkMode, setIsDarkMode ] = useState(false)

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
            <h1>Configuracion</h1>
            <DropdownMenu/>
            <button onClick={toggleDarkMode} className="b1">
                {isDarkMode ? 'Desactivar modo oscuro' : 'Activar modo oscuro'}
            </button>
            <p>{isDarkMode ? 'Modo oscuro activado' : 'Modo claro activado'}</p>
        </div>
    )
}