import DropdownMenu from "../components/Base"
import "../components/profileModule.css"
import { useState } from "react"

export function Profile(){
    const [texto, setTexto] = useState('')
    const [archivo, setArchivo] = useState(null)
    const [showModal, setShowModal] = useState(false)

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

    const handleFileChange = (e) => {
        const file = e.target.files[0];

        if (file) {
            const maxSize = 50 * 1024 * 1024;

            if (file.size > maxSize) {
                setShowModal(true)
                e.target.value = null;
                return
            }
            console.log('Archivo valido: ',file.name)
        }
    }

    return(
        <div>
            <h1>Profile</h1>

            <div>
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
                {showModal && (
                    <div className="overlay">
                        <div className="modal">
                            <p>El archivo excede el tamaño maximo de 50 MB</p>
                            <button onClick={() => setShowModal(false)}>Cerrar</button>
                        </div>
                    </div>
                )}
            </div>

            <DropdownMenu/>
        </div>
    )
}