import DropdownMenu from "../components/Base"
import { useState } from "react";
import { useNavigate } from 'react-router-dom';

export function SearchPage(){
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);

    const navigate = useNavigate();

    const searchUsers = async (value) => {
        setQuery(value);

        if (value.length < 2) {
            setResults([]);
            return;
        }

        const res = await fetch(`http://127.0.0.1:8000/users/search/?q=${value}`, {
            headers: {
            Authorization: `token ${localStorage.getItem("token")}`,
            }
        });

        const data = await res.json();
        setResults(data.results);
    };

    return (
        <div>
            <input
                type="text"
                placeholder="Buscar usuarios..."
                value={query}
                onChange={(e) => searchUsers(e.target.value)}
            />
            <button onClick={() => searchUsers(query)}>Buscar</button>

            <ul>
                {results.map(user => (
                    <li
                        key={user.id}
                        onClick={() => navigate(`/perfil/${user.id}`)}
                        >
                        {user.username}
                    </li>
                ))}
            </ul>

            <DropdownMenu />
        </div>
    )
}