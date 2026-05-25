import React, { useState } from 'react';
import axios from 'axios';

export default function ChatModal({ property, onClose, onChatCreated }) {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleStartChat = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        setError('Please log in to contact the admin');
        setLoading(false);
        return;
      }

      // Create chat
      const chatRes = await axios.post(
        'http://localhost:8000/api/chats/',
        { property: property.id },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const chat = chatRes.data;

      // Send initial message if provided
      if (message.trim()) {
        await axios.post(
          `http://localhost:8000/api/chats/${chat.id}/send_message/`,
          { message },
          { headers: { Authorization: `Bearer ${token}` } }
        );
      }

      onChatCreated(chat);
      onClose();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to start chat');
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4 rounded-t-lg flex justify-between items-center">
          <div>
            <h2 className="text-white font-bold text-lg">Contact Admin</h2>
            <p className="text-blue-100 text-sm">{property.title}</p>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:text-blue-200 text-2xl font-light"
          >
            ✕
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleStartChat} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Price: ${property.price?.toLocaleString() || 'N/A'}
            </label>
            <p className="text-xs text-slate-500">{property.description}</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Your Message
            </label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Tell us about your interest in this property..."
              rows="4"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="flex gap-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-slate-300 rounded-lg text-slate-700 font-medium hover:bg-slate-50 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white rounded-lg font-medium transition"
            >
              {loading ? 'Starting Chat...' : 'Start Chat'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
