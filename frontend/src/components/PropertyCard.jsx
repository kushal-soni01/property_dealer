import React, { useState } from 'react';
import ChatModal from './ChatModal';
import ChatWindow from './ChatWindow';

export default function PropertyCard({ property, locality }) {
  const [showChatModal, setShowChatModal] = useState(false);
  const [activeChat, setActiveChat] = useState(null);

  const handleChatCreated = (chat) => {
    setActiveChat(chat);
  };

  return (
    <>
      <div className="bg-white rounded-lg border border-slate-200 shadow-sm hover:shadow-md transition overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-slate-50 to-slate-100 px-4 py-3 border-b border-slate-200">
          <h3 className="font-bold text-slate-900 text-base">{property.title}</h3>
          <p className="text-xs text-slate-600 mt-1">{locality?.name}, {locality?.city}</p>
        </div>

        {/* Content */}
        <div className="p-4 space-y-3">
          {/* Price */}
          <div className="flex items-center justify-between">
            <span className="text-sm text-slate-600">Price:</span>
            <span className="font-bold text-lg text-slate-900">
              ${property.price?.toLocaleString()}
            </span>
          </div>

          {/* Description */}
          <div>
            <p className="text-sm text-slate-700 line-clamp-2">
              {property.description || 'No description available'}
            </p>
          </div>

          {/* Locality Info */}
          {locality?.profile && (
            <div className="bg-blue-50 p-2 rounded border border-blue-100">
              <p className="text-xs text-slate-600 mb-1">
                <strong>Tourist Rating:</strong> {locality.profile.tourist_rating || 'N/A'}/10
              </p>
              <p className="text-xs text-slate-600">
                <strong>Commercial Rating:</strong> {locality.profile.commercial_rating || 'N/A'}/10
              </p>
            </div>
          )}

          {/* Metadata */}
          <div className="text-xs text-slate-500 pt-2 border-t border-slate-100">
            Listed on {new Date(property.created_at).toLocaleDateString()}
          </div>
        </div>

        {/* Actions */}
        <div className="bg-slate-50 px-4 py-3 border-t border-slate-200 flex gap-2">
          <button
            onClick={() => setShowChatModal(true)}
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg font-medium text-sm transition flex items-center justify-center gap-2"
          >
            <span>💬</span> Contact Admin
          </button>
          <button
            onClick={() => alert('View details feature coming soon!')}
            className="flex-1 bg-slate-200 hover:bg-slate-300 text-slate-900 px-3 py-2 rounded-lg font-medium text-sm transition"
          >
            Details
          </button>
        </div>
      </div>

      {/* Chat Modal */}
      {showChatModal && (
        <ChatModal
          property={property}
          onClose={() => setShowChatModal(false)}
          onChatCreated={handleChatCreated}
        />
      )}

      {/* Chat Window */}
      {activeChat && (
        <ChatWindow
          chat={activeChat}
          onClose={() => setActiveChat(null)}
        />
      )}
    </>
  );
}
