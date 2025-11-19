import { NavLink } from 'react-router-dom';

function Navigation() {
  return (
    <nav className="navigation">
      <div className="nav-brand">RAG Application</div>
      <ul className="nav-links">
        <li>
          <NavLink to="/" className={({ isActive }) => isActive ? 'active' : ''}>
            Documents
          </NavLink>
        </li>
        <li>
          <NavLink to="/upload" className={({ isActive }) => isActive ? 'active' : ''}>
            Upload
          </NavLink>
        </li>
        <li>
          <NavLink to="/chat" className={({ isActive }) => isActive ? 'active' : ''}>
            Chat
          </NavLink>
        </li>
      </ul>
    </nav>
  );
}

export default Navigation;
