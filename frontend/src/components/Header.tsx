import React from 'react';
import { Link } from 'react-router-dom';

const Header: React.FC = () => {
  return (
    <header className="bg-blue-600 text-white shadow-md">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <Link to="/" className="text-2xl font-bold">
          Question Paper Scrutinizer
        </Link>
        <nav>
          <ul className="flex space-x-6">
            <li>
              <Link to="/" className="hover:text-blue-200">
                Dashboard
              </Link>
            </li>
            <li>
              <Link to="/upload-syllabus" className="hover:text-blue-200">
                Upload Syllabus
              </Link>
            </li>
            <li>
              <Link to="/upload-textbook" className="hover:text-blue-200">
                Upload Textbook
              </Link>
            </li>
            <li>
              <Link to="/upload-question-paper" className="hover:text-blue-200">
                Upload Question Paper
              </Link>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
};

export default Header; 