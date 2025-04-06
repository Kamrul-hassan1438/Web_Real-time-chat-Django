import React, { useEffect, useState } from "react";

const Chat = ({ currentUser, recipient }) => {
  const [socket, setSocket] = useState(null);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    // Check if both currentUser and recipient are specified
    if (!currentUser) {
      console.error("Both `currentUser` and `recipient` must be specified.");
      return;
    }
    console.log(currentUser);
    // Initialize WebSocket connection
    const ws = new WebSocket(
      `ws://localhost:8000/ws/chat/${currentUser}/${recipient}/`
    );

    setSocket(ws);

    // When WebSocket connection is established
    ws.onopen = () => {
      console.log("WebSocket connection established.");
    };

    // When WebSocket is closed
    ws.onclose = (e) => {
      console.log("Disconnected from WebSocket:", e);
    };

    // When a message is received from WebSocket
    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        console.log("Message received:", data); // Debugging statement
        if (data.sender && data.message) {
          setMessages((prevMessages) => [
            ...prevMessages,
            `${data.sender}: ${data.message}`,
          ]);
        }
      } catch (error) {
        console.error("Failed to parse WebSocket message:", error);
      }
    };

    // When an error occurs with WebSocket
    ws.onerror = (error) => {
      console.error("WebSocket encountered an error:", error);
    };

    // Cleanup WebSocket on component unmount or when user/recipient changes
    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
      console.log("WebSocket connection closed during cleanup.");
    };
  }, [currentUser, recipient]);

  // Handle sending a message
  const handleSendMessage = () => {
    if (!message.trim()) {
      console.warn("Cannot send an empty message.");
      return;
    }

    if (socket && socket.readyState === WebSocket.OPEN) {
      console.log("Sending message:", message.trim());
      socket.send(
        JSON.stringify({
          sender: currentUser,
          message: message.trim(),
        })
      );
      setMessage(""); // Clear input field after sending
    } else {
      console.error("WebSocket is not open. Cannot send the message.");
    }
  };

  return (
    <div>
      <h3>Chat with {recipient}</h3>
      <div
        style={{
          border: "1px solid #ccc",
          padding: "10px",
          maxHeight: "300px",
          overflowY: "auto",
          marginBottom: "10px",
        }}
      >
        {messages.length > 0 ? (
          messages.map((msg, index) => (
            <p key={index} style={{ margin: "5px 0" }}>
              {msg}
            </p>
          ))
        ) : (
          <p style={{ color: "#888" }}>No messages yet.</p>
        )}
      </div>
      <div style={{ display: "flex", gap: "10px" }}>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type a message"
          style={{ flex: 1, padding: "5px" }}
        />
        <button onClick={handleSendMessage} style={{ padding: "5px 10px" }}>
          Send
        </button>
      </div>
    </div>
  );
};

export default Chat;
