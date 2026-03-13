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

    const [modalAbierto, setModelAbierto] = useState(false)
    const [categorias, setCategorias] = useState([])
    const [categoriaSeleccionadas, setCategoriaSeleccionadas] = useState([])
    const [nuevaCategoria, setNuevaCategoria] = useState("")

    const observerRef = useRef(null)
    const hasFetched = useRef(false);

    useEffect(() => {
        if (hasFetched.current) return

        hasFetched.current = true
        loadPosts("http://127.0.0.1:8000/posts/")
        fetchCategorias()
    }, [])

    const fetchCategorias = async () => {
        try {
            const res = await fetch("http://127.0.0.1:8000/categorias/", {
                headers: {
                    Authorization: `Token ${localStorage.getItem("token")}`,
                }
            })
            const data = await res.json()
            setCategorias(data)
        } catch (error) {
            console.error("Error al cargar las categorias", error)
        }
    }

    const toggleCategoria = (Id) => {
        setCategoriaSeleccionadas(prev => 
            prev.includes(Id) ? prev.filter(c => c !== Id) : [...prev, Id]
        )
    }

    const agregarCategoria = async () => {
        const nombre = nuevaCategoria.trim()
        if (!nombre) return
        if(categorias.some(c => c.nombre.toLowerCase() === nombre.toLowerCase())){
            setNuevaCategoria("")
            return
        }
        const nueva = { id: `nueva_${nombre}`, nombre }
        setCategorias(prev => [...prev, nueva])
        setCategoriaSeleccionadas(prev => [...prev, nueva.id])
        setNuevaCategoria("")
    }

    const publicar = async () => {
        const formData = new FormData();
        if (texto) formData.append('comentario', texto)
        if (archivo) formData.append('archivo', archivo)

        const idsExistentes = categoriaSeleccionadas.filter(id => !String(id).startsWith('nueva_'))
        const nombresNuevos = categoriaSeleccionadas
            .filter(id => String(id).startsWith('nueva_'))
            .map(id => String(id).replace('nueva_', ''))

        try {
            const idsNuevos = await Promise.all(
                nombresNuevos.map(async (nombre) => {
                    const res = await fetch("http://127.0.0.1:8000/categorias/crear/", {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            Authorization: `Token ${localStorage.getItem("token")}`,
                        },
                        body: JSON.stringify({ nombre }),
                    })
                    const data = await res.json()
                    return data.id
                })
            )
            
            const todosLosIds = [...idsExistentes, ...idsNuevos]
            todosLosIds.forEach(id => formData.append('categorias', id))

            const response = await fetch('http://127.0.0.1:8000/subir/',{
                method: 'POST',
                body: formData,
                headers: {
                    Authorization: `token ${localStorage.getItem("token")}`,
                }
            })

            if (response.ok){
                const nuevaPublicacion = await response.json()
                setPosts(prev => [nuevaPublicacion, ...prev])
                alert('Comentario enviado con exito')
                setTexto('')
                setArchivo(null)
                setCategoriaSeleccionadas([])
                setModelAbierto(false)
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
                const likedInit = {}
                const countInit = {}
                data.results.forEach(post => {
                    likedInit[post.id] = post.liked || false
                    countInit[post.id] = post.likes_count || 0
                })
                setLiked(prev => ({...prev, ...likedInit}))
                setLikedCount(prev => ({...prev, ...countInit}))
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
            setLiked(prev => ({...prev, [post.id]: data.liked}))
            setLikedCount(prev => ({...prev, [post.id]: data.likes_count}))
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

            setComentarios(prev => ({
                ...prev,
                [post.id]: [...(prev[post.id] || []), newComment]
            }))

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
                <textarea 
                    name="texto" 
                    value={texto} 
                    onChange={(e) => setTexto(e.target.value)}
                    placeholder="Escribe tu comentario"
                />
                <input type="file" name="archivo" onChange={(e) => setArchivo(e.target.files[0])}/>
                <button
                    onClick={() => setModelAbierto(true)}
                    disabled={!texto && !archivo}
                >Siguiente</button>
            </div>

            {modalAbierto && (
                <div className="modal-overlay">
                    <div className="modal">
                        <h2>Selecciona Categorias</h2>
                        <p className="modal-subtitulo">Seleccione una o mas categorias</p>
                        <div className="categorias-grid">
                            {categorias.map(cat => (
                                <button
                                    key={cat.id}
                                    onClick={() => toggleCategoria(cat.id)}
                                    className={`categoria-chip ${categoriaSeleccionadas.includes(cat.id) ? 'seleccionada' : ''}`}
                                >
                                    {categoriaSeleccionadas.includes(cat.id) && <span>'✓ '</span>}
                                    {cat.nombre}
                                </button>
                            ))}
                        </div>
                        <div className="nueva-categoria">
                            <input
                                type="text"
                                placeholder="Nueva categoría"
                                value={nuevaCategoria}
                                onChange={(e) => setNuevaCategoria(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && agregarCategoria()}
                            />
                            <button onClick={agregarCategoria}>Agregar</button>
                        </div>
                        <div className="modal-botones">
                            <button onClick={() => setModelAbierto(false)}>Cancelar</button>
                            <button
                                onClick={publicar}
                                disabled={categoriaSeleccionadas.length === 0}
                            >Publicar</button>
                        </div>
                    </div>
                </div>
            )}

            <div className="postsSection">
                {posts.map((post) => (
                    <div key={post.id} className="post">
                        <p className="postText">{post.comentario}</p>
                        <button onClick={() => toggleLike(post)}>
                            {liked[post.id] ? '❤️' : '🤍'} {likedCount[post.id]}
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