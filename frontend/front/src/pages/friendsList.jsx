import { useState, useEffect } from "react"
import DropdownMenu from "../components/Base"
import { useNavigate } from "react-router-dom"
import "../components/friendsModule.css"

export function Friends(){
    const [users,setUsers] = useState([])
    const navigate = useNavigate();
    
    useEffect(() => {
        fetch("http://127.0.0.1:8001/api/amigos/",{
            headers: {
                Authorization: `token ${localStorage.getItem("token")}`
            }
        })
        .then(res => res.json())
        .then(data => setUsers(data.amigos));
    },[])

    return(
        <div className="friends-container">
            <h1 className="title">Amigos</h1>

            <div className="friends-grid">
                {users.map(user => (
                    <div key={user.id} className="friend-card">
                        <img src={`http://127.0.0.1:8000/${user.foto_perfil}`} alt="foto" className="friend-avatar" />
                        <p className="friend-name">{user.username}</p>
                        <div className="friend-actions">
                            <button onClick={() => navigate(`/perfil/${user.id}`)} className="btn-profile">
                                Ver perfil
                            </button>
                            <button onClick={() => navigate(`/chatPage/${user.id}`)} className="btn-message">
                                Enviar mensaje
                            </button>
                        </div>
                    </div>
                ))}
            </div>
            <DropdownMenu/>
        </div>
    )
}