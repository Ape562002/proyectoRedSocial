import { useEffect, useState, useRef } from "react";
import "../components/ChatModule.css"

const PrivateChat = ({ otherUserId }) => {
  const [socket, setSocket] = useState(null);
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [offset, setOffset] = useState(15);
  const [wsReady,setWsReady] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  const token = localStorage.getItem("token")
  const senderId = localStorage.getItem("user_id");
  const wsRef = useRef(null);
  const topRef = useRef(null);
  const chatContainerRef = useRef(null);
  const messageIdsRef = useRef(new Set());
  const prevScrollHeighRef = useRef(0);
  const isInitialLoadRef = useRef(true);

  useEffect(() => {

    wsRef.current = new WebSocket(
      `ws://127.0.0.1:8001/ws/chat/private/${otherUserId}/?token=${token}`
    );

    wsRef.current.onopen = () => {
      console.log("✅ WS conectado")
      setWsReady(true);
    }

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "history_batch"){
        console.log("📦 history_batch detectado:", data.messages.length, "mensajes");
        const newMessage = data.messages.filter(
          msg => !messageIdsRef.current.has(msg.id || msg.timestamp)
        );

        newMessage.forEach(msg => {
          messageIdsRef.current.add(msg.id || msg.timestamp);
        });

        setMessages(prev => [...newMessage, ...prev]);
        setHasMore(data.has_more)
        setIsLoading(false);
        return;
      }

      const msgId = data.id || data.timestamp;

      if (messageIdsRef.current.has(msgId)){
        return;
      }

      messageIdsRef.current.add(msgId);

      if (data.is_history) {
        setMessages(prev => [...prev, data]);

        if(isInitialLoadRef.current){
          setTimeout(scrollToBottom, 100);
          isInitialLoadRef.current = false;
        }
      }else{
        setMessages(prev => [...prev, data])
        setTimeout(scrollToBottom, 50)
      }
    };

    wsRef.current.onclose = () => {
      console.log("❌ WS cerrado")
      setWsReady(false);
    }
    wsRef.current.onerror = (e) => console.log("WS error", e)

    setSocket(wsRef);

    return () => {
      wsRef.current?.close();
      wsRef.current = null;
    }
  }, [senderId,otherUserId]);

  const scrollToBottom = () => {
    if(chatContainerRef.current){
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }

  const sendMessage = () => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN){
      console.log("ws aun no esta listo")
      return;
    } 

    wsRef.current.send(JSON.stringify({
      type:"message",
      message: text
    }));

    setText("");
  };

  useEffect(() => {
    const observer = new IntersectionObserver((entries) => {
      const entry = entries[0];

      if (
        entry &&
        entry.isIntersecting &&
        wsRef.current &&
        wsRef.current.readyState === WebSocket.OPEN &&
        !isLoading &&
        hasMore
      ){
        console.log("🔄 Cargando más mensajes, offset:", offset);
        setIsLoading(true);

        if (chatContainerRef.current){
          prevScrollHeighRef.current = chatContainerRef.current.scrollHeight;
        }

        wsRef.current.send(JSON.stringify({
          type: "load_more",
          offset: offset,
          limit: 15
        }));
        setOffset(prev => prev + 15);
      }
    })

    if(topRef.current){
      observer.observe(topRef.current);
    }

    return () => observer.disconnect();
  },[offset, isLoading, hasMore]);

  useEffect(() => {
    if (isLoading && chatContainerRef.current && prevScrollHeighRef.current > 0) {
      const container = chatContainerRef.current;
      const newScrollHeight = container.scrollHeight;
      const newScrollDiff = newScrollHeight - prevScrollHeighRef.current;
      container.scrollTop = newScrollDiff;
    }
  },[messages, isLoading]);

  const senderIdNum = Number(senderId);

  return (
    <div>
      <h3>Chat privado</h3>

      <div ref={chatContainerRef} className="chat-container">
        <div ref={topRef} style={{ height: '1px' }}/>

          {isLoading && <div style={{textAlign: 'center', padding: '10px'}}>Cargando...</div>}

          {!hasMore && messages.length > 0 && (
            <div style={{textAlign: 'center', padding: '10px', color: '#999'}}>
              No hay mas mensajes
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={msg.id || msg.timestamp || i} className={msg.sender_id === senderIdNum ? 'message-row' : 'message-row-theirs'}>
              <div className={msg.sender_id === senderIdNum ? 'message-bubble' : 'bubble-theirs'}>
                <b>{msg.sender_id === senderIdNum ? "Yo" : "Él"}:</b>: {msg.message}
              </div>
            </div>
          ))}
      </div>

      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && sendMessage()}
      />
      <button onClick={sendMessage}>Enviar</button>
    </div>
  );
};

export default PrivateChat;