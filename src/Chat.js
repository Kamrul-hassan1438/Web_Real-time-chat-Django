import React, { useEffect, useState } from "react";

const Chat = ({ currentUser }) => {
  const [connectedUsers, setConnectedUsers] = useState([]);
  const [recipient, setRecipient] = useState("");
  const [socket, setSocket] = useState(null);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [recipientOnline, setRecipientOnline] = useState(false);
  const [image, setImage] = useState(null); // State to store selected image

  // Fetch previously connected users
  useEffect(() => {
    if (!currentUser) return;

    fetch(`http://localhost:8000/chat/connected-users/${currentUser}/`)
      .then((res) => res.json())
      .then(setConnectedUsers)
      .catch((err) => console.error("Failed to fetch connected users:", err));
  }, [currentUser]);

  // Load previous messages
  useEffect(() => {
    if (!currentUser || !recipient) return;

    fetch(`http://localhost:8000/messages/${currentUser}/${recipient}/`)
      .then((res) => res.json())
      .then(setMessages)
      .catch((err) => console.error("Failed to fetch messages:", err));
  }, [currentUser, recipient]);

  // WebSocket setup
  useEffect(() => {
    if (!currentUser || !recipient) return;

    const ws = new WebSocket(
      `ws://localhost:8000/ws/chat/${encodeURIComponent(
        currentUser
      )}/${encodeURIComponent(recipient)}/`
    );
    setSocket(ws);

    ws.onopen = () => console.log("WebSocket connected");

    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);

        if (data.type === "status") {
          setRecipientOnline(data.online);
        } else if (data.sender && data.message) {
          console.log("Received message:", data); // Log the data to check

          // Update messages with sender, message, and image_url
          setMessages((prev) => [
            ...prev,
            {
              sender: data.sender,
              message: data.message,
              imageUrl: data.image_url, // Store the image URL
            },
          ]);
        }
      } catch (err) {
        console.error("WebSocket message error:", err);
      }
    };

    ws.onclose = () => console.log("WebSocket closed");
    ws.onerror = (e) => console.error("WebSocket error:", e);

    return () => ws.close();
  }, [currentUser, recipient]);

  const handleSendMessage = () => {
    if (
      (!message.trim() && !image) ||
      !socket ||
      socket.readyState !== WebSocket.OPEN
    ) {
      return console.error("WebSocket not ready or message is empty");
    }

    // Preparing the data to send
    const messageData = {
      sender: currentUser,
      recipient,
      message: message.trim(),
      image: image ? image : null, // Send image if present
    };

    console.log("Sending message data:", messageData); // Log the data being sent

    socket.send(JSON.stringify(messageData));
    setMessage("");
    setImage(null); // Clear the image after sending
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImage(reader.result);
        console.log("Image data:", reader.result); // Log the base64 image data
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div>
      <h2>Chat App</h2>
      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="recipient">Choose a user to chat with:</label>
        <select
          id="recipient"
          value={recipient}
          onChange={(e) => setRecipient(e.target.value)}
        >
          <option value="">-- Select --</option>
          {connectedUsers.map((user) => (
            <option key={user.username} value={user.username}>
              {user.username}
            </option>
          ))}
        </select>
        {recipient && (
          <span
            style={{
              marginLeft: 10,
              color: recipientOnline ? "green" : "gray",
            }}
          >
            {recipientOnline ? "Online" : "Offline"}
          </span>
        )}
      </div>

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
          messages.map((msg) => (
            <div
              key={msg.id}
              style={{
                margin: "5px 0",
                textAlign: msg.sender === currentUser ? "right" : "left",
              }}
            >
              <strong>{msg.sender}:</strong>
              {msg.message && <p>{msg.message}</p>}
              {msg.imageUrl && (
                <img
                  src={`http://localhost:8000${msg.imageUrl}`}
                  alt="sent_image"
                  style={{ maxWidth: "200px", marginTop: "5px" }}
                />
              )}
            </div>
          ))
        ) : (
          <p style={{ color: "#888" }}>No messages yet.</p>
        )}
      </div>

      <div style={{ marginBottom: "10px" }}>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          rows="4"
          cols="50"
          placeholder="Type your message..."
        />
      </div>

      <div>
        <input
          type="file"
          accept="image/*"
          onChange={handleImageChange}
          style={{ marginRight: "10px" }}
        />
        <button onClick={handleSendMessage}>Send</button>
      </div>
    </div>
  );
};

export default Chat;
