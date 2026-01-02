import { useState,useEffect } from "react"
import { useNavigate } from "react-router-dom"
import "../components/RegistroModule.css"

export function Register(){
    const [username, setUsername] = useState("")
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [pass2, setPass2] = useState("")

    const navi = useNavigate();

    useEffect(()=>{
        const storedUser = localStorage.getItem("token")
        if(storedUser){
            navi("/dashboard");
        }
    },[])

    const handleSubmit = async(e) => {
        e.preventDefault();

        if(password == pass2){
            try{
                const response = await fetch("http://127.0.0.1:8000/resgister/",{
                    method: "POST",
                    headers: {
                        "Content-type":"application/json",
                    },
                    body:JSON.stringify({ username,email,password})
                })

                const data = await response.json();

                if(response.ok){
                    localStorage.setItem("token", data.token);
                    navi("/dashboard");
                }else{
                    console.error("error: ",error);
                }
            }catch(error){
                console.error("Error en la solicitud: ",error);
            }
        }else{
            console.log("las contraseñas no coinciden");
        }
    }

    return(
        <div className="hola">
            <div className="container">
                <h1>Registro</h1>
                <form onSubmit={handleSubmit}>
                    <div className="usuario">
                        <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required/>
                        <label>Usuario</label>
                    </div>
                    <div className="usuario">
                        <input type="text" value={email} onChange={(e) => setEmail(e.target.value)} required/>
                        <label>Email</label>
                    </div>
                    <div className="usuario">
                        <input type="text" value={password} onChange={(e) => setPassword(e.target.value)} required/>
                        <label>Contraseña</label>
                    </div>
                    <div className="usuario">
                        <input type="text" value={pass2} onChange={(e) => setPass2(e.target.value)} required/>
                        <label>Repita la contraseña</label>
                    </div>
                    <button>Registrar</button>
                </form>
            </div>
        </div>
    )
}