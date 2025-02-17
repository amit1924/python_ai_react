import React, { useState } from "react";
import axios from "axios";

const ImageUpload = ({ onDescription }) => {
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (event) => {
    setImage(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!image) return;

    const formData = new FormData();
    formData.append("file", image);

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(
        "http://localhost:8000/image", // Updated URL to the FastAPI image processing endpoint
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      onDescription(response.data.response); // Update the description with the response from FastAPI
    } catch (error) {
      setError("Failed to upload image.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="image-upload">
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Uploading..." : "Upload Image"}
      </button>
      {error && <p className="error">{error}</p>}
    </div>
  );
};

export default ImageUpload;
