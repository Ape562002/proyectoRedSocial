import DropdownMenu from "../components/Base"
import "../components/profileModule.css"
import { useState, useEffect, useRef, use } from "react"

export function Profile(){
    const [texto, setTexto] = useState('')
    const [archivo, setArchivo] = useState(null)
    const [posts, setPosts] = useState([])
    const [nextUrl, setNextUrl] = useState(null)
    const [loading, setLoading] = useState(false)
    const [liked, setLiked] = useState(false)
    const [likedCount, setLikedCount] = useState("")
    const [comentarios, setComentarios] = useState("")
    const [comentariosVisibles, setComentariosVisibles] = useState({})
    const [comentarioText, setComentarioText] = useState("")
    const observerRef = useRef(null)
    const hasFetched = useRef(false);

    useEffect(() => {
        if (hasFetched.current) return

        hasFetched.current = true
        loadPosts("http://127.0.0.1:8000/posts/")
    }, [])

    const handleSubmit = async (e) => {
        e.preventDefault();

        const formData = new FormData();
        formData.append('comentario', texto)
        if (archivo) {
            formData.append('archivo',archivo)
        }

        try{
            const response = await fetch('http://127.0.0.1:8000/subir/',{
                method: 'POST',
                body: formData,
                headers: {
                    Authorization: `token ${localStorage.getItem("token")}`,
                }
            })

            if (response.ok){
                alert('Comentario enviado con exito')
                setTexto('')
                setArchivo(null)
            }else{
                const data = await response.json()
                alert('Error al enviar '+ JSON.stringify(data))
            }
        } catch (error) {
            alert('Error en el envio del comentario')
            console.log(archivo)
        }
    }

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

    return(
        <div>
            <h1 className="perfil">Profile</h1>

            <div className="inputSection">
                <form onSubmit={handleSubmit} encType="multipart/form-data">
                    <textarea 
                        name="texto" 
                        value={texto} 
                        onChange={(e) => setTexto(e.target.value)}>
                        placeholder="Escribe tu comentario" required
                    </textarea>
                    <input type="file" name="archivo" onChange={(e) => setArchivo(e.target.files[0])}/>
                    <button>Enviar</button>
                </form>
            </div>

            <div className="postsSection">
                {posts.map((post) => (
                    <div key={post.id} className="post">
                        <p className="postText">{post.comentario}</p>
                        <button onClick={() => toggleLike(post)}>
                            {liked ? '❤️' : '🤍'} {likedCount}
                        </button>
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

            <DropdownMenu/>
        </div>
    )
}