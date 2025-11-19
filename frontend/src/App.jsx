import { Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import DocumentList from './pages/DocumentList';
import Upload from './pages/Upload';
import Chat from './pages/Chat';
import './App.css';

function App() {
  return (
    <div className="app">
      <Navigation />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<DocumentList />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/chat" element={<Chat />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
