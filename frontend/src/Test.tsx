import React from 'react';

export const Test: React.FC = () => {
  return (
    <div className="p-8 bg-blue-500 text-white rounded-lg shadow-lg">
      <h1 className="text-2xl font-bold mb-4">Tailwind CSS v3 Test</h1>
      <p className="text-lg">Tailwind CSS v3 is working with upgraded Node.js setup!</p>
      
      <div className="grid grid-cols-2 gap-4 mt-6">
        <div className="bg-chess-light p-4 rounded text-black font-semibold">Chess Light Square</div>
        <div className="bg-chess-dark p-4 rounded text-white font-semibold">Chess Dark Square</div>
      </div>
      
      <div className="grid grid-cols-4 gap-2 mt-4">
        <div className="bg-chess-blunder p-3 rounded text-white text-sm font-bold">Blunder</div>
        <div className="bg-chess-mistake p-3 rounded text-white text-sm font-bold">Mistake</div>
        <div className="bg-chess-inaccuracy p-3 rounded text-white text-sm font-bold">Inaccuracy</div>
        <div className="bg-chess-good p-3 rounded text-white text-sm font-bold">Good Move</div>
      </div>
    </div>
  );
};

export default Test;
