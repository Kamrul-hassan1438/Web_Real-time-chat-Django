import React, { useState } from "react";
import Chat from "./Chat";

function App() {
  const [currentUser, setCurrentUser] = useState("");
  const [password, setPassword] = useState("");
  const [recipient, setRecipient] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleLogin = async () => {
    if (currentUser.trim() && password.trim()) {
      try {
        const response = await fetch("http://localhost:8000/login/", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: new URLSearchParams({
            username: currentUser,
            password: password,
          }),
        });
  
        if (response.ok) {
          setIsLoggedIn(true);
        } else {
          const data = await response.json();
          alert(data.error || "Login failed");
        }
      } catch (error) {
        alert("Failed to connect to the server.");
      }
    } else {
      alert("Please fill in both username and password.");
    }
  };
  

  return (
    <div>
      {!isLoggedIn ? (
        <div>
          <h2>Login</h2>
          <input
            type="text"
            value={currentUser}
            onChange={(e) => setCurrentUser(e.target.value)}
            placeholder="Enter your username"
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
          />
          <button onClick={handleLogin}>Login</button>
        </div>
      ) : (
        <div>
          <h2>Welcome, {currentUser}</h2>
          <input
            type="text"
            value={recipient}
            onChange={(e) => setRecipient(e.target.value)}
            placeholder="Enter recipient's username"
          />
          <Chat currentUser={currentUser} recipient={recipient} />
        </div>
      )}
    </div>
  );
}

export default App;
