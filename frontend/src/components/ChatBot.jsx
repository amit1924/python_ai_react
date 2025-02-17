import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { motion } from "framer-motion"; // Import Framer Motion

export default function ChatBot() {
  const [messages, setMessages] = useState([
    { user: "", bot: "Hello, how can I assist you today?" }, // Initial message
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false); // State to handle typing effect
  const [image, setImage] = useState(null);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() && !image) return;

    setLoading(true);
    const userMessage = {
      user: input || "Image uploaded",
      bot: "Thinking...",
    };
    setMessages([...messages, userMessage]);
    setIsTyping(true); // Set typing effect for bot's message

    try {
      if (image) {
        const formData = new FormData();
        formData.append("file", image);
        const response = await axios.post(
          "https://python-ai-react.onrender.com/image", // Updated URL to the FastAPI image processing endpoint
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );
        const imageDescription = response.data.response;
        const botMessage = {
          user: "Uploaded Image",
          bot: `Here's the description: ${imageDescription}`,
        };

        setMessages((prevMessages) => [...prevMessages, botMessage]);
      } else {
        const response = await axios.post(
          "https://python-ai-react.onrender.com/chat",
          {
            message: input,
          }
        );

        const botMessage = response.data.response;
        console.log(botMessage);

        // Format the response with line breaks and bullet points
        const formattedMessage = botMessage.split("\n").map((line, index) => (
          <div key={index} className="mb-2">
            {line.includes("*") ? (
              <ul className="list-disc pl-5">
                {line.split("*").map((item, idx) => {
                  if (item.trim()) {
                    return (
                      <li key={idx} className="text-green-300 text-lg">
                        {item.trim()}
                      </li>
                    );
                  }
                  return null;
                })}
              </ul>
            ) : (
              <p className="text-lg text-white">{line}</p>
            )}
          </div>
        ));

        setMessages((prevMessages) => [
          ...prevMessages,
          { user: input, bot: formattedMessage },
        ]);
      }

      setIsTyping(false); // Stop typing effect when done
    } catch (error) {
      console.error("Error sending message:", error);
      setError("There was an error with your request.");
    }
    setInput("");
    setLoading(false);
    setImage(null); // Reset the image after sending
  };

  const handleFileChange = (event) => {
    setImage(event.target.files[0]);
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen overflow-clip bg-gradient-to-r from-green-900 to-black text-white p-4">
      <motion.h1
        className="text-4xl font-bold mb-6 text-center text-gradient bg-clip-text"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1 }}
      >
        AI Chatbot
      </motion.h1>

      <motion.div
        className="w-full bg-gray-800 p-6 rounded-lg shadow-xl"
        initial={{ scale: 0.8 }}
        animate={{ scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        <div className="h-[480px] lg:h-[500px] overflow-y-auto mb-4 p-2 lg:p-4 border border-gray-700 rounded-lg bg-gray-900 shadow-inner">
          {messages.map((msg, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 * index, duration: 0.5 }}
              className="mb-4"
            >
              <p className="text-blue-300 font-bold text-lg">You: {msg.user}</p>
              <div className="text-green-300 font-bold text-lg">{msg.bot}</div>
            </motion.div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="flex gap-2 items-center relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1 p-2 lg:p-4 rounded-lg bg-gray-700 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-400 transition-all pr-12"
            placeholder="Type your message..."
          />
          <label className="absolute right-[4rem] lg:right-[7rem] top-1 lg:top-2 cursor-pointer">
            <input type="file" className="hidden" onChange={handleFileChange} />
            <span className="text-white text-2xl">📷</span>
          </label>

          <motion.button
            onClick={sendMessage}
            disabled={loading || isTyping}
            className="px-2 py-1 md:px-4 lg:px-6 lg:py-3 bg-blue-500 hover:bg-blue-600 rounded-lg disabled:bg-gray-500 text-lg font-semibold transition-all"
          >
            {loading ? (
              <motion.div className="w-6 h-6 border-4 border-t-4 border-white border-solid rounded-full animate-spin" />
            ) : (
              <span>{image ? "Upload" : "Send"}</span>
            )}
          </motion.button>
        </div>

        {error && <p className="text-red-500 mt-2">{error}</p>}
      </motion.div>
    </div>
  );
}
