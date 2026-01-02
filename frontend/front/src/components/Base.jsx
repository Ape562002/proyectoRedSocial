import { useState,useEffect } from "react";
import "./BaseModule.css";

const DropdownMenu = () => {
    const [isOpen, setIsOpen] = useState(false);

    useEffect(() =>{
        const savedMode = localStorage.getItem('darkMode');
        if(savedMode === 'true'){
            document.body.classList.add('dark-mode');
        }else{
            document.body.classList.remove('dark-mode');
        }
    },[]);

    const logout = async () => {
        try{
            const response = await fetch("http://127.0.0.1:8000/logout/",{
                method: "POST",
                headers: {
                    "Content-Type":"application/json",
                    Authorization: `Token ${localStorage.getItem("token")}`,
                },
            });

            if(response.ok){
                localStorage.removeItem("token")
                window.location.href = "/login"
            }else{
                console.log("Error en logout")
            }
        }catch(error){
            console.error("Error en la peticion de logout",error)
        }
    }

    return(
        <div className={`dropdown ${isOpen ? "open" : ""}`}>
            <button onClick={() => setIsOpen(!isOpen)} className="dropdownButton">☰</button>
            <ul>
                <li><a href="/">Inicio</a></li>
                <li><a href="/profile">Perfil</a></li>
                <li><a href="/settings">Configuracion</a></li>
                <li><button onClick={logout}>logout</button></li>
            </ul>
        </div>
    )
}

export default DropdownMenu;
