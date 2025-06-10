import React, { useState } from 'react';
import { apiService } from '../services/api';
import Alert from './Alert';
import LoadingSpinner from './LoadingSpinner';

const SyllabusUploader = ({ subjectName }) => {
  const [courseName, setCourseName] = useState(subjectName || '');
  const [units, setUnits] = useState([
    { unit: 'Unit I', title: '', syllabus_content: '' }
  ]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');

  const addUnit = () => {
    const nextUnitNumber = units.length + 1;
    const romanNumerals = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII'];
    const unitName = romanNumerals[nextUnitNumber - 1] || `${nextUnitNumber}`;
    
    setUnits([...units, { 
      unit: `Unit ${unitName}`, 
      title: '', 
      syllabus_content: '' 
    }]);
  };

  const removeUnit = (index) => {
    if (units.length > 1) {
      setUnits(units.filter((_, i) => i !== index));
    }
  };

  const updateUnit = (index, field, value) => {
    const newUnits = [...units];
    newUnits[index][field] = value;
    setUnits(newUnits);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const syllabusData = {
      course_name: courseName,
      units: units.filter(unit => unit.title.trim() && unit.syllabus_content.trim())
    };

    if (syllabusData.units.length === 0) {
      setMessage('Please add at least one unit with title and content');
      setMessageType('error');
      return;
    }

    setLoading(true);
    try {
      const result = await apiService.uploadSyllabus(subjectName, syllabusData);
      setMessage(`Syllabus uploaded successfully! Created ${result.documents_created} document chunks.`);
      setMessageType('success');
    } catch (error) {
      setMessage(error.response?.data?.error || 'Failed to upload syllabus');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="text-xl font-semibold text-secondary-900">Upload Syllabus for {subjectName}</h2>
      </div>
      <div className="card-body">
        {message && (
          <Alert
            type={messageType}
            message={message}
            onClose={() => setMessage('')}
            className="mb-4"
          />
        )}
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="courseName" className="block text-sm font-medium text-secondary-700 mb-2">
              Course Name
            </label>
            <input
              type="text"
              id="courseName"
              value={courseName}
              onChange={(e) => setCourseName(e.target.value)}
              className="input-field"
              required
            />
          </div>

          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-medium text-secondary-900">Units</h3>
              <button
                type="button"
                onClick={addUnit}
                className="btn-secondary text-sm"
              >
                Add Unit
              </button>
            </div>

            {units.map((unit, index) => (
              <div key={index} className="border border-secondary-200 rounded-lg p-4">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="font-medium text-secondary-800">Unit {index + 1}</h4>
                  {units.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeUnit(index)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Remove
                    </button>
                  )}
                </div>
                
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-1">
                      Unit Identifier
                    </label>
                    <input
                      type="text"
                      value={unit.unit}
                      onChange={(e) => updateUnit(index, 'unit', e.target.value)}
                      className="input-field"
                      placeholder="e.g., Unit I"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-1">
                      Unit Title
                    </label>
                    <input
                      type="text"
                      value={unit.title}
                      onChange={(e) => updateUnit(index, 'title', e.target.value)}
                      className="input-field"
                      placeholder="e.g., Introduction to Operating Systems"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-1">
                      Syllabus Content
                    </label>
                    <textarea
                      value={unit.syllabus_content}
                      onChange={(e) => updateUnit(index, 'syllabus_content', e.target.value)}
                      className="input-field"
                      rows="4"
                      placeholder="Enter the detailed syllabus content for this unit..."
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary flex items-center"
          >
            {loading && <LoadingSpinner size="sm" className="mr-2" />}
            Upload Syllabus
          </button>
        </form>
      </div>
    </div>
  );
};

export default SyllabusUploader;
