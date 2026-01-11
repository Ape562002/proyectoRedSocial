import { useEffect } from "react";
import DropdownMenu from "../components/Base"
import { useParams } from "react-router-dom"
import { useState } from "react";


export function PerfilUsuario() {
    const { userId } = useParams()
    const [usuario, setUsuario] = useState(null);
    const [posts, setPosts] = useState([]);
    const [friendStatus, setFriendStatus] = useState('none');
    const [requestId, setRequestId] = useState(null);

    useEffect(() => {
        fetch(`http://127.0.0.1:8000/comprobar_solicitud/${userId}/`, {
            headers: { Authorization: `Token ${localStorage.getItem("token")}` }
        })
            .then(res => res.json())
            .then(data => {
                setFriendStatus(data.status); 
                if (data.request_id) {
                    setRequestId(data.request_id);
                }
                console.log(data);
            });
    }, [userId]);

    const handleFriendAction = async () => {
        if (friendStatus === 'none') {
                await fetch(`http://127.0.0.1:8000/enviar_solicitud/${userId}/`, {
                method: 'POST',
                headers: { Authorization: `Token ${localStorage.getItem("token")}` }
            });
            setFriendStatus('pending_sent');
        }
    }

    useEffect(() => {
        fetch(`http://127.0.0.1:8000/perfil_usuario/${userId}/`, {
            headers: {
            Authorization: `token ${localStorage.getItem("token")}`,
            }
        })
            .then(res => res.json())
            .then(data => setUsuario(data));
    }, [userId]);

    useEffect(() => {
        fetch(`http://127.0.0.1:8000/posts/user/${userId}/`, {
            headers: {
            Authorization: `Token ${localStorage.getItem("token")}`
            }
        })
            .then(res => res.json())
            .then(data => setPosts(data.results));
    }, [userId]);

    const renderButton = () => {
        switch (friendStatus) {
            case 'friends':
                return <button disabled>Amigos</button>;
            case 'pending_sent':
                return <button disabled>Solicitud Enviada</button>;
            case 'pending_received':
                return (
                    <>
                    <button onClick={accept}>Aceptar</button>
                    <button onClick={reject}>Rechazar</button>
                    </>
                );

            default:
                return (
                    <button onClick={handleFriendAction}>
                    Agregar amigo
                    </button>
                );
        }    
    }

    const accept = async () => {
        await fetch(`http://127.0.0.1:8000/aceptar_solicitud/${requestId}/`, {
            method: 'POST',
            headers: {
            Authorization: `Token ${localStorage.getItem("token")}`
            }
        });

        setFriendStatus('friends');
    };

    const reject = async () => {
        await fetch(`http://127.0.0.1:8000/rechazar_solicitud/${requestId}/`, {
            method: 'POST',
            headers: {
            Authorization: `Token ${localStorage.getItem("token")}`
            }
        });

        setFriendStatus('none');
    };
    

    if (!usuario) return <p>Cargando...</p>;

    return (
        <div>
            <h1>Perfil de Usuario</h1>

            <h2>{usuario.username}</h2>
            {renderButton()}

            {posts.map((post) => (
                <div key={post.id} className="post">
                    <h3>{post.comentario}</h3>
                    {post.formato === "jpg" && (
                            <img src={post.archivo} alt="Archivo adjunto" className="postImage"/>
                    )}
                    {post.formato === "mp4" && (
                        <video controls src={post.archivo} className="postImage"/>
                    )}
                </div>
            ))}
            
            <DropdownMenu />
        </div>
    )
}