import { useState,useEffect, useRef, use } from "react"
import DropdownMenu from "../components/Base"
import "../components/DashboardModule.css"

export function Dashboard(){
    const [recomensaciones, setRecomensaciones] = useState([])
    const [pagina, setPagina] = useState(1)
    const [hayMas, setHayMas] = useState(true)
    const [loading, setLoading] = useState(false)
    const [liked, setLiked] = useState({})
    const [likedCount, setLikedCount] = useState({})
    const [comentarios, setComentarios] = useState({})
    const [comentariosVisibles, setComentariosVisibles] = useState({})
    const [comentarioText, setComentarioText] = useState("")
    const observerRef = useRef()
    const hasFetched = useRef(false)

    useEffect(() => {
        if (hasFetched.current) return
        hasFetched.current = true
        cargarRecomensaciones(1)
    }, [])

    const cargarRecomensaciones = async (paginaActual) => {
        if (loading || !hayMas) return
        setLoading(true)

        try{
            const res = await fetch(
                `http://127.0.0.1:8000/feed/recomendados/?pagina=${paginaActual}`,
                {
                    headers: {
                        Authorization: `Token ${localStorage.getItem("token")}`
                    }
                }
            )

            if (res.ok) {
                const data = await res.json()

                const likedInit = {}
                const countInit = {}
                data.recomendaciones.forEach(post => {
                    likedInit[post.id] = post.is_liked || false
                    countInit[post.id] = post.likes_count || 0
                })
                setLiked(prev => ({ ...prev, ...likedInit }))
                setLikedCount(prev => ({ ...prev, ...countInit }))

                setRecomensaciones(prev => [...prev, ...data.recomendaciones])
                setHayMas(data.hay_mas)
                setPagina(paginaActual + 1)
            }
        } catch (error) {
            console.error("Error fetching recommendations:", error)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                if (entries[0].isIntersecting && hayMas && !loading) {
                    cargarRecomensaciones(pagina)
                }
            },
            { threshold: 1 }
        )
        if (observerRef.current) observer.observe(observerRef.current)
        return () => observer.disconnect()
    }, [hayMas, loading, pagina])

    const toggleLike = async (post) => {
        try{
            const res = await fetch(`http://127.0.0.1:8000/posts/${post.id}/like/`, {
                method: 'POST',
                headers: {
                    Authorization: `Token ${localStorage.getItem("token")}`
                }
            })
            const data = await res.json()
            setLiked(prev => ({ ...prev, [post.id]: data.liked }))
            setLikedCount(prev => ({ ...prev, [post.id]: data.likes_count }))
        } catch (error) {
            console.error("Error toggling like:", error)
        }
    }

    const submitComment = async (post) => {
        if (!comentarioText.trim()) return
        try{
            const res = await fetch(`http://127.0.0.1:8000/posts/${post.id}/comentario/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Token ${localStorage.getItem("token")}`
                },
                body: JSON.stringify({ texto: comentarioText })
            })
            const newComment = await res.json()
            setComentarios(prev => ({ 
                ...prev,
                [post.id]: [...(prev[post.id] || []), newComment] 
            }))
            setComentarioText("")
        } catch (error) {
            console.error("Error submitting comment:", error)
        }
    }

    const fetchComentarios = async (postId) => {
        try{
            const res = await fetch(`http://127.0.0.1:8000/posts/${postId}/comentarios/`, {
                headers: {
                    Authorization: `Token ${localStorage.getItem("token")}`
                }
            })
            const data = await res.json()
            setComentarios(prev => ({ ...prev, [postId]: data.results }))
                
        } catch (error) {
            console.error("Error fetching comments:", error)
        }
    }

    const toggleComentarios = (postId) => {
        setComentariosVisibles(prev => ({ ...prev, [postId]: !prev[postId] }))
        if (!comentarios[postId]) fetchComentarios(postId)
    }

    return(
        <div>
            <h1 className="perfil">Para ti</h1>

            <div className="postsSection">
                {recomensaciones.map(post => (
                    <div key={post.id} className="post">
                        <p className="postText">{post.comentario}</p>
                        <button onClick={() => toggleLike(post)}>
                            {liked[post.id] ? "❤️" : "🤍"} {likedCount[post.id] || 0}
                        </button>
                        {post.formato === "jpg" && (
                            <img src={post.archivo} alt="Archivo adjunto" className="postImage"/>
                        )}
                        {post.formato === "mp4" && (
                            <video controls src={post.archivo} className="postImage"/>
                        )}
                        {post.formato === "NaN" && null}

                        <div className="comentariosSection">
                            <input 
                                type="text" 
                                placeholder="Escribe un comentario..." 
                                value={comentarioText}
                                onChange={(e) => setComentarioText(e.target.value)}
                            />
                        </div>
                        <button onClick={() => submitComment(post)}>Comentar</button>
                        <button onClick={() => toggleComentarios(post.id)}>
                            ver comentarios 
                        </button>
                        {comentariosVisibles[post.id] && (
                            comentarios[post.id]?.map(c => (
                                <p key={c.id}><b>{c.usuario}</b> {c.contenido} </p>
                            ))
                        )}
                    </div>
                ))}

            </div>
            <DropdownMenu/>
        </div>
    )
}