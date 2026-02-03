import { useEffect } from "react";
import DropdownMenu from "../components/Base"
import { useParams } from "react-router-dom"
import { useState, useRef } from "react";


export function PerfilUsuario() {
    const { userId } = useParams()
    const [usuario, setUsuario] = useState(null);
    const [posts, setPosts] = useState([]);
    const [nextUrl, setNextUrl] = useState(null)
    const [loading, setLoading] = useState(false)
    const [liked, setLiked] = useState(false)
    const [likedCount, setLikedCount] = useState("")
    const [comentarios, setComentarios] = useState("")
    const [comentariosVisibles, setComentariosVisibles] = useState({})
    const [comentarioText, setComentarioText] = useState("")
    const [friendStatus, setFriendStatus] = useState('none');
    const [requestId, setRequestId] = useState(null);
    const observerRef = useRef(null)
    const hasFetched = useRef(false);

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
         if (hasFetched.current) return

        hasFetched.current = true
        loadPosts(`http://127.0.0.1:8000/posts/user/${userId}/`)
    }, [userId]);

    const loadPosts = async (url) => {
        if (!url || loading) return;
        setLoading(true);

        try {
            const res = await fetch(url, {
                headers: {
                    Authorization: `Token ${localStorage.getItem("token")}`,
                }
            });

            if (res.ok) {
                const data = await res.json();
                setPosts((prevPosts) => [...prevPosts, ...data.results]);
                console.log(data.results);
                setNextUrl(data.next);
                setLoading(false);
            }
        } catch (error) {
            console.error("Error al cargar los posts", error);
        }
    }

    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                if (entries[0].isIntersecting && nextUrl && !loading) {
                    loadPosts(nextUrl);
                }
            },
            { threshold: 1 }
        )
        if (observerRef.current) {
            observer.observe(observerRef.current);
        }

        return () => observer.disconnect();
    }, [nextUrl]);

    const toggleLike = async (post) => {
        try {
            const res = await fetch(`http://127.0.0.1:8000/posts/${post.id}/like/`,
                {
                    method: 'POST',
                    headers: {
                        Authorization: `Token ${localStorage.getItem("token")}`,
                    }
                }
            )

            const data = await res.json()
            setLiked(data.liked)
            setLikedCount(data.likes_count)
        } catch (error) {
            return console.error("Error al dar like", error)
        }
    }

    const submitComment = async (post) => {
        if (!comentarioText.trim()) return
        try {
            const res = await fetch(`http://127.0.0.1:8000/posts/${post.id}/comentario/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Token ${localStorage.getItem("token")}`,
                },
                body: JSON.stringify({
                    contenido: comentarioText
                })
            })

            const newComment = await res.json()

            setComentarioText("")
        } catch (error) {
            console.error("Error al enviar comentario", error)
        }
    }

    const fetchComentarios = async (postId) => {
        try {
            const res = await fetch(`http://127.0.0.1:8000/posts/${postId}/comentarios/`, {
                headers: {
                    Authorization: `Token ${localStorage.getItem("token")}`,
                }
            })

            const data = await res.json()
            console.log(data)
            setComentarios(prev => ({...prev, [postId]: data.results}))
        } catch (error) {
            console.error("Error al cargar comentarios", error)
        }
    }

    const toggleComentarios = (postId) => {
        setComentariosVisibles(prev => ({
            ...prev,
            [postId]: !prev[postId]
        }));

        if (!comentarios[postId]) {
            fetchComentarios(postId);
        }
    };

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
            <div>
                {posts.map((post) => (
                    <div key={post.id} className="post">
                        <button onClick={() => toggleLike(post)}>
                            {liked ? '❤️' : '🤍'} {likedCount}
                        </button>
                        <h3>{post.comentario}</h3>
                        {post.formato === "jpg" && (
                                <img src={post.archivo} alt="Archivo adjunto" className="postImage"/>
                        )}
                        {post.formato === "mp4" && (
                            <video controls src={post.archivo} className="postImage"/>
                        )}
                        
                        <div className="comentariosSection">
                            <input
                                type="text"
                                value={comentarioText}
                                onChange={(e) => setComentarioText(e.target.value)}
                                placeholder="Escribe tu comentario"
                            />
                            <button onClick={() => submitComment(post)}>Enviar Comentario</button>
                            <button onClick={() => toggleComentarios(post.id)}>Ver comentarios</button>

                            {comentariosVisibles[post.id] &&
                                comentarios[post.id]?.map(c => (
                                    <p key={c.id}>
                                    <b>{c.usuario}</b> {c.contenido}
                                    </p>
                                ))
                            }
                        </div>
                    </div>
                ))}
                <div ref={observerRef}>
                    {loading && <p>Cargando más posts...</p>}
                </div>
            </div>

            
            <DropdownMenu />
        </div>
    )
}