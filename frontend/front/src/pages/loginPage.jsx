import { useState,useEffect } from "react"
import { useNavigate } from "react-router-dom"
import "../components/loginModule.css"

export function LoginPage(){
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    const navi = useNavigate();

    useEffect(()=>{
        const storedUser = localStorage.getItem("token")
        if (storedUser){
            navi("/dashboard");
        }
    },[])

    const handleSubmit = async(e) => {
        e.preventDefault();

        try{
            const response = await fetch("http://127.0.0.1:8000/login/",{
                method: "POST",
                headers: {
                    "Content-type":"application/json",
                },
                body: JSON.stringify({ username,password })
            });

            const data = await response.json();

            if(response.ok){
                localStorage.setItem("token", data.token);
                navi("/dashboard");
            }else{
                alert("Credenciales incorrectas");
            }
        }catch(error){
            console.error("Error en la solicitud:", error)
        }
    }

    const redi = () => {
        navi("/registro");
    }

    return(
        <div>
            <div className="container">
                <h1>Ingresa a RedBack</h1>
                <form onSubmit={handleSubmit}>
                    <div className="usuario">
                        <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required/>
                        <label>Usuario</label>
                    </div>
                    <div className="usuario">
                        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required/>
                        <label>Contraseña</label>
                    </div>
                    <button>Enviar</button>
                </form>
                <button onClick={redi}>Registro</button>
            </div>
        </div>
    )
}