import { useParams } from "react-router-dom"
import PrivateChat from "./privateChat";

export function ChatPage(){
    const { userId } = useParams()

    return <PrivateChat otherUserId={userId} />;

}