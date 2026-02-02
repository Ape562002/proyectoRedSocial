import { useState,useEffect, use } from "react"
import imageCompression from "browser-image-compression"
import DropdownMenu from "../components/Base"

export function EditProfile(){
    const [username,setUsername] = useState("")
    const [email,setEmail] = useState("")
    const [descripcion, setDescripcion] = useState("");
    const [perfilPrivado, setPerfilPrivado] = useState(false);
    const [fotoPerfil, setFotoPerfil] = useState(null);
    const [preview, setPreview] = useState(null);

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    useEffect(() => {
        const fetchPerfil = async () => {
            try{
                const res = await fetch("http://127.0.0.1:8000/perfil_detalle/", {
                    method:"GET",
                    headers:{
                        Authorization: `Token ${localStorage.getItem("token")}`,
                    }
                });

                const data = await res.json();
                console.log(data)

                if(!res.ok) throw data;

                setUsername(data.user.username);
                setEmail(data.user.email);
                if(data.perfil.descripcion !== null){
                    setDescripcion(data.perfil.descripcion);
                }
                if(data.perfil.privado !== false){
                    setPerfilPrivado(data.perfil.privado);
                }

                if(data.perfil.foto_perfil){
                    setPreview(`http://127.0.0.1:8000${data.perfil.foto_perfil}`);
                }
            }catch(err){
                setError(err)
            }
        }

        fetchPerfil();
    }, []);

    const handleFileChange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        try{
            const options = {
                maxSizeMB: 1,
                maxWidthOrHeight: 1920,
                useWebWorker: true
            };
            const compressedBlob = await imageCompression(file, options);

            const extension = file.name.split('.').pop();
            const uniqueName = `${Date.now()}_${Math.random().toString(36).substring(2, 15)}.${extension}`;

            const compressedFile = new File(
                [compressedBlob],
                uniqueName,
                { type: file.type }
            )
            setFotoPerfil(compressedFile);
            setPreview(URL.createObjectURL(compressedFile));
        }catch(err){
            console.error("Error al comprimir la imagen:", err);
            setError("Error al comprimir la imagen");
        }
    }

    const handleSubmit = async(e) => {
        e.preventDefault();
        setLoading(true)
        setError(null)
        setSuccess(null)
    
        const formData = new FormData();
        formData.append("username", username);
        formData.append("email",email);
        formData.append("descripcion", descripcion);
        formData.append("perfil_privado", perfilPrivado);

        if(fotoPerfil){
            formData.append("foto_perfil", fotoPerfil);
        }

        try{
            const res = await fetch("http://127.0.0.1:8000/actualizar/", {
                method:"PUT",
                headers:{
                    Authorization: `token ${localStorage.getItem("token")}`,
                },
                body:formData
            })

            const data = await res.json();

            if(!res.ok){
                throw data;
            }

            setSuccess("Perfil Actualizado correctamente ✔️")
        }catch(err){
            setError(err)
        }finally{
            setLoading(false)
        }
    }

    return(
        <div>
            <h1>Editar Perfil</h1>
            <form onSubmit={handleSubmit}>
                {error && <pre style={{ color:"red" }}>{JSON.stringify(error, null, 2)}</pre>}
                {success && <p style={{ color:"green" }}>{success}</p>}

                <div>
                    <label>Usuario</label>
                    <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required/>
                </div>

                <div>
                    <label>Email</label>
                    <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required/>
                </div>

                <div>
                    <label>Description</label>
                    <textarea value={descripcion} onChange={(e) => setDescripcion(e.target.value)}/>
                </div>

                <div>
                    <label>
                        <input type="checkbox" checked={perfilPrivado} onChange={(e) => setPerfilPrivado(e.target.checked)}/>
                        Perfil privado
                    </label>
                </div>

                <div>
                    <label>Foto de perfil</label>
                    <input type="file" accept="image/*" onChange={handleFileChange}/>
                </div>

                {preview && (
                    <div>
                        <img src={preview} alt="Preview" style={{ width: "100px", height: "100px" }} />
                    </div>
                )}

                <button type="submit" disabled ={loading}>
                    {loading ? "guardando" : "guardar cambios"}
                </button>
            </form>
            <DropdownMenu/>
        </div>
    )
}